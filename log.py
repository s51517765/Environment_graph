# https://qiita.com/pytry3g/items/aa38d8c2acf59b90aaac
import codecs
import datetime

# root実行時のファイル場所
# less /root/temparature.log

filename ='temparature.log'

def write_log(text):
    text = str(datetime.datetime.now())+"\n"+text
    #print(text, file=codecs.open(filename, 'a', 'utf-8'))
    with open(filename, 'a',encoding='utf-8') as file:
        file.write(text+"\n")
    
if __name__ == '__main__':
    write_log("てすと\nてすと")