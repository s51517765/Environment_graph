import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import datetime
import requests
import sys
import pathlib
import os


def send_line(str):
    url = "https://notify-api.line.me/api/notify"
    LINE_Token = "*************"
    headers = {"Authorization": "Bearer " + LINE_Token}

    dt = datetime.datetime.now()
    message = 'Temp SNS stop from '+str+" @"+dt.strftime('%H:%M:%S')
    payload = {"message": message}
    r = requests.post(url, headers=headers, params=payload)


def get_last_data():
    path = pathlib.Path(__file__).resolve().parent
    JSON_PATH = str(path)+'/'+'serviceAccountKey.json'
    cred = credentials.Certificate(JSON_PATH)
    app = firebase_admin.initialize_app(cred)

    db = firestore.client()
    ref = db.collection(u'Current')
    docs = ref.stream()

    hasData = False
    for doc in docs:
        hasData = True
        # print(u'{} => {}'.format(doc.id, doc.to_dict()))
        if datetime.datetime.now() - datetime.datetime.strptime(doc.id[:19], '%Y-%m-%d %H:%M:%S') > datetime.timedelta(hours=1):
            send_line(doc.id[:19])
            print(datetime.datetime.now())
            print("NG -> OS reboot!")
            os.system('sudo reboot')
        else:
            print("OK", str(datetime.datetime.now()))

    if not hasData:
        print(datetime.datetime.now())
        print("No data -> OS reboot!", str(datetime.datetime.now()))
        send_line("No Data")
        os.system('sudo reboot')


if __name__ == '__main__':
    get_last_data()
