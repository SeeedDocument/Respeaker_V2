##!/usr/bin/python
# coding:utf-8

import logging
import time
import os
import signal
from threading import Thread, Event
from respeaker import Microphone
from aip import AipSpeech
import json

#请申请Key: https://console.bce.baidu.com/ai/?fromai=1#/ai/speech/overview/index 

APP_ID = ''
API_KEY = ''
SECRET_KEY = ''

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

# 读取文件
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

# 识别本地文件
def baidu_speech(fileName):
    data = client.asr(get_file_content(fileName), 'wav', 16000, {
        'dev_pid': 1537,
    })

    #print (data)

    string = json.loads(json.dumps(data))

    if string['err_no'] == 0:
        pstr = str(string['result'])
        str_doc = pstr.replace("u\'","").replace("\'","").replace("[","").replace("]","").decode('unicode_escape').replace("]","").strip()
        #print(str_doc)
        return str_doc



def task(quit_event):
    mic = Microphone(quit_event=quit_event)

    while not quit_event.is_set():
        if mic.wakeup('respeaker'):
            print('Wake up')
            #data = mic.listen()
            os.system("arecord -d 2 -r 16000 -f S16_LE -t wav /home/respeaker/test.wav")
            try:
                text = baidu_speech('/home/respeaker/test.wav')
                if text:
                    print('Recognized %s' % text)
                    if (u'开灯') in text:
                        print('主人马上为你开灯')
                    if (u'关灯') in text:
                        print('主人马上为你关灯')
            except Exception as e:
                print(e.message)


def main():
    logging.basicConfig(level=logging.DEBUG)
    quit_event = Event()

    def signal_handler(sig, frame):
        quit_event.set()
        print('quit')
    signal.signal(signal.SIGINT, signal_handler)

    thread = Thread(target=task, args=(quit_event,))
    thread.daemon = True
    thread.start()
    while not quit_event.is_set():
        time.sleep(1)

    time.sleep(1)


if __name__ == '__main__':
    main()
