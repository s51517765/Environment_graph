# Environment_graph

## 概要 (Overview)

ラズパイに接続したBME280で温湿度を測定し、Firebaseを用いてWebに表示します。<br>
グラフはChart.jsを使用しています。

### 自動起動設定
```
$ sudo crontab -e
xx 4,16 * * * /usr/bin/python3 /home/<acount name>/cron.py
@reboot sleep 15; /usr/bin/python3 /home/<acount name>/main.py

$ crontab -e
xx xx * * 5 sh /home/<acount name>/Environment_raw_data/gitPush.sh
```
管理者権限でスクリプトmain.pyの起動と、ウォッチドックタイマーcron.pyを起動し、ユーザー権限でraw_dataバックアップスクリプトを起動します。

※ xxは起動時刻の数値

## 画面イメージ (ScreenShot)

<img src="https://github.com/s51517765/Environment_graph/blob/main/image1.jpg">

<img src="https://github.com/s51517765/Environment_graph/blob/main/image2.jpg">

## 動作要件 (Requirements)

Python3 / Raspberry Pi / BME280(i2c) / Firebase

## 技術的解説 (Technical explanation)

https://s51517765.hatenadiary.jp/entry/2021/07/12/073000


## 回路図 (Circuit diagram)

<img src="https://github.com/s51517765/Environment_graph/blob/main/%E5%9B%9E%E8%B7%AF%E5%9B%B3.png">

## 参考（Reference）

https://developers.google.com/chart/interactive/docs/gallery/linechart

https://github.com/s51517765/Environment_raw_data

## ライセンス (License)

This software is released under the MIT License, see LICENSE.
