#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import bme280
import time

import pathlib

# Use a service account
path = str(pathlib.Path(__file__).resolve().parent)
cred = credentials.Certificate(path+"/"+'serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()


def setTemp(Temp=25, Hum=55, Pres=1000):
    Date = datetime.datetime.now()
    Temp, Hum, Pres = bme280.main()
    print(Temp, Hum, Pres)
    # キーを日付時刻で作成
    ref = db.collection('Database').document(str(Date))
    ref.set({
        u'Pres': Pres,
        u'Hum': Hum,
        u'Temp': Temp,
    })


def setTemp_Current(Temp=25, Hum=55, Pres=1000):
    ref = db.collection('Current')
    docs = ref.stream()
    for doc in docs:
        db.collection('Current').document(doc.id).delete()

    Date = datetime.datetime.now()
    Temp, Hum, Pres = bme280.main()
    # キーを日付時刻で作成
    ref = db.collection('Current').document(str(Date))
    ref.set({
        u'Pres': Pres,
        u'Hum': Hum,
        u'Temp': Temp,
    })


maxLength = 24*7


def resizeDatabase():
    ref = db.collection('Database')
    docs = ref.stream()
    dataSize = 0
    for doc in docs:
        #print(doc.id, doc._data)
        dataSize += 1
        if dataSize == 1:
            firstDateId = doc.id

    if dataSize >= maxLength:
        for i in range(dataSize-maxLength):
            deleteDoc(firstDateId)


def exportData():
    filename = path+"/"+"env_result.txt"
    output = open(filename, 'a', encoding='utf')
    ref = db.collection('Database')
    docs = ref.stream()
    for doc in docs:
        output.write(doc.id)
        output.write(" , Pres " + doc._data["Pres"])
        output.write(" , Temp " + doc._data["Temp"])
        output.write(" , Hum " + doc._data["Hum"])
        output.write("\n")
    output.close()

def deleteDoc(id):
    db.collection('Database').document(id).delete()


if __name__ == '__main__':
    setTemp_Current()
    while(True):
        try:
            now = datetime.datetime.now()
            if now.minute == 0:
                setTemp()
                setTemp_Current()
                resizeDatabase()
                time.sleep(60)
            elif now.minute % 10 == 0:
                setTemp_Current()
                time.sleep(60)
            if now.weekday() == 5:  # 土曜日5
                if(now.hour == 23 and now.minute == 5):
                    exportData()
                    time.sleep(30)
            time.sleep(30)
        except Exception as e:
            print(now)
            print(e)
            time.sleep(30)
