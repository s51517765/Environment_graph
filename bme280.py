#!/usr/bin/python3
# -*- coding: utf-8 -*-

# https://qiita.com/yukataoka/items/8f9046587c978e91f689
# i2cdetect -y 1 #i2c 認識確認

from smbus2 import SMBus  # pip install smbus2
import time
import datetime as dt


class Bme280:

    def __init__(self, busNumber=1, i2cAddress=0x76):

        self.bus = SMBus(busNumber)
        self.i2cAddress = i2cAddress
        self.digT = []
        self.digP = []
        self.digH = []
        self.timeFine = 0.0
        self.presRaw = 0.0
        self.tempRaw = 0.0
        self.humRaw = 0.0

        osrsT = 1  # Temperature oversampling x 1
        osrsP = 1  # Pressure oversampling x 1
        osrsH = 1  # Humidity oversampling x 1
        mode = 3  # Normal mode
        tSb = 5  # Tstandby 1000ms
        filter = 0  # Filter off
        spi3wEn = 0  # 3-wire SPI Disable

        ctrlMeasReg = (osrsT << 5) | (osrsP << 2) | mode
        configReg = (tSb << 5) | (filter << 2) | spi3wEn
        ctrlHumReg = osrsH

        self.writeReg(0xF2, ctrlHumReg)
        self.writeReg(0xF4, ctrlMeasReg)
        self.writeReg(0xF5, configReg)
        self.getCalibParam()

        self.readData()

    def writeReg(self, regAddress, data):
        self.bus.write_byte_data(self.i2cAddress, regAddress, data)

    def getCalibParam(self):
        calib = []

        for i in range(0x88, 0x88+24):
            calib.append(self.bus.read_byte_data(self.i2cAddress, i))
        calib.append(self.bus.read_byte_data(self.i2cAddress, 0xA1))
        for i in range(0xE1, 0xE1+7):
            calib.append(self.bus.read_byte_data(self.i2cAddress, i))

        self.digT.append((calib[1] << 8) | calib[0])
        self.digT.append((calib[3] << 8) | calib[2])
        self.digT.append((calib[5] << 8) | calib[4])
        self.digP.append((calib[7] << 8) | calib[6])
        self.digP.append((calib[9] << 8) | calib[8])
        self.digP.append((calib[11] << 8) | calib[10])
        self.digP.append((calib[13] << 8) | calib[12])
        self.digP.append((calib[15] << 8) | calib[14])
        self.digP.append((calib[17] << 8) | calib[16])
        self.digP.append((calib[19] << 8) | calib[18])
        self.digP.append((calib[21] << 8) | calib[20])
        self.digP.append((calib[23] << 8) | calib[22])
        self.digH.append(calib[24])
        self.digH.append((calib[26] << 8) | calib[25])
        self.digH.append(calib[27])
        self.digH.append((calib[28] << 4) | (0x0F & calib[29]))
        self.digH.append((calib[30] << 4) | ((calib[29] >> 4) & 0x0F))
        self.digH.append(calib[31])

        for i in range(1, 2):
            if self.digT[i] & 0x8000:
                self.digT[i] = (-self.digT[i] ^ 0xFFFF) + 1

        for i in range(1, 8):
            if self.digP[i] & 0x8000:
                self.digP[i] = (-self.digP[i] ^ 0xFFFF) + 1

        for i in range(0, 6):
            if self.digH[i] & 0x8000:
                self.digH[i] = (-self.digH[i] ^ 0xFFFF) + 1

    def readData(self):
        data = []
        for i in range(0xF7, 0xF7+8):
            data.append(self.bus.read_byte_data(self.i2cAddress, i))
        self.presRaw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        self.tempRaw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        self.humRaw = (data[6] << 8) | data[7]

    def getPressure(self):
        pressure = 0.0

        v1 = (self.timeFine / 2.0) - 64000.0
        v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * self.digP[5]
        v2 = v2 + ((v1 * self.digP[4]) * 2.0)
        v2 = (v2 / 4.0) + (self.digP[3] * 65536.0)
        v1 = (((self.digP[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)
                ) / 8) + ((self.digP[1] * v1) / 2.0)) / 262144
        v1 = ((32768 + v1) * self.digP[0]) / 32768

        if v1 == 0:
            return 0
        pressure = ((1048576 - self.presRaw) - (v2 / 4096)) * 3125
        if pressure < 0x80000000:
            pressure = (pressure * 2.0) / v1
        else:
            pressure = (pressure / v1) * 2
        v1 = (self.digP[8] * (((pressure / 8.0) *
                               (pressure / 8.0)) / 8192.0)) / 4096
        v2 = ((pressure / 4.0) * self.digP[7]) / 8192.0
        pressure = pressure + ((v1 + v2 + self.digP[6]) / 16.0)
        return pressure/100

    def getTemperature(self):
        v1 = (self.tempRaw / 16384.0 - self.digT[0] / 1024.0) * self.digT[1]
        v2 = (self.tempRaw / 131072.0 - self.digT[0] / 8192.0) * (
            self.tempRaw / 131072.0 - self.digT[0] / 8192.0) * self.digT[2]
        self.timeFine = v1 + v2
        temperature = self.timeFine / 5120.0
        return temperature

    def getHumidity(self):
        varH = self.timeFine - 76800.0
        if varH != 0:
            varH = (self.humRaw - (self.digH[3] * 64.0 + self.digH[4]/16384.0 * varH)) * (self.digH[1] / 65536.0 * (
                1.0 + self.digH[5] / 67108864.0 * varH * (1.0 + self.digH[2] / 67108864.0 * varH)))
        else:
            return 0
        varH = varH * (1.0 - self.digH[0] * varH / 524288.0)
        if varH > 100.0:
            varH = 100.0
        elif varH < 0.0:
            varH = 0.0
        return varH


def main():
    print("BME280 Start!")
    tdatetime = dt.datetime.now()
    try:
        sensor = Bme280()
        Pres = "{:.1f}".format(sensor.getPressure())
        Temp = "{:.1f}".format(sensor.getTemperature())
        Hum = "{:.1f}".format(sensor.getHumidity())
        #env_result = str(Pres)+"hPa / "+str(Temp)+"deg / "+str(Hum) + "%"
        #print(env_result)
        # file = open('env_result.txt', 'a', encoding='utf')  # 追記モードでオープン
        #file.write(str(tdatetime)+", "+Pres + ", "+Temp+", "+Hum+"\n")
    except Exception as e:
        print(tdatetime)
        print("Error in BME280")
        print(e)
    return Temp, Hum, Pres


def get_env_loop(inerval=3600):
    while (True):
        main()
        time.sleep(inerval)


if __name__ == '__main__':
    #get_env_loop()
    t,h,p=main()
    print(t,h,p)