from distutils.log import error
import imaplib
import email
from email import policy 
import requests
from bs4 import BeautifulSoup as bs
import time
import re
from private.privateManager import getKey

def login():
    imap = imaplib.IMAP4_SSL('imap.naver.com')
    id = getKey('naver_email')
    pw = getKey('naver_password')
    imap.login(id, pw)
    return imap

def get_link(message):
    byte = message.get_payload()
    return byte.split(' ')[4].split('=')[0]

def print_time(endWith = '\n'):
    now = time.localtime()
    print ("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec), end = endWith)

def getCurId():
    now = time.localtime()
    id = ((now.tm_year * 12) + now.tm_mon) * 50 + now.tm_mday
    return id

def getDateId(date):
    date = date.split(',')[1].strip().split(' ')[:-2]
    accsum = int(date[2])
    monthList = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    i = 0
    for month in monthList:
        i += 1
        if date[1] == month:
            break
    accsum = accsum * 12 + i
    accsum = accsum * 50 + int(date[0])
    return accsum

def no_space(text):
  text1 = re.sub('\nbsp;|&nbsp;|\n|\t|\r|  ', '', text)
  text2 = re.sub('\n\n', '', text1)
  return text2

def authentication(link):
    resp = requests.get(link)
    soup = bs(resp.text, 'html.parser')
    result = no_space(soup.find('div', {'class' : 'box-message'}).text)
    print_time(endWith = ' -> ')
    print(result)

authSender = 'noreply@ruauth3.coursemos.kr'
tick = 5

if __name__=='__main__':
    while True:
        print_time()
        # login
        try:
            session = login()
            session.select('inbox')
            # search mail
            mails = session.search('utf-8', 'From', authSender)[1][-1]
            last_mail = mails.split(b' ')[-1]
            data = session.fetch(last_mail, '(RFC822)')[1]
            raw_mail = data[0][1]
            email_message = email.message_from_bytes(raw_mail, policy = policy.default)

            # accessability
            if getDateId(email_message['Date']) == getCurId():
                # authenticate
                link = get_link(email_message)
                authentication(link)
                # delete
                session.store(last_mail, '+FLAGS', '\\Deleted')
                session.expunge()
                # set sleep time
                now = time.localtime()
                sleep_time = 24 * 60 * 60 + tick
                sleep_time -= now.tm_hour * 60 * 60
                sleep_time -= now.tm_min * 60
                sleep_time -= now.tm_sec
                print(f'sleep time: {sleep_time}')
                time.sleep(sleep_time)
            # logout
            session.close()
            session.logout()
        except Exception as e:
            print(f'error: {e}')
            pass
        time.sleep(tick)