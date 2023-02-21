import requests
import os
import smtplib
from bs4 import BeautifulSoup
from email.message import EmailMessage
from time import sleep
from dotenv import load_dotenv

load_dotenv()

URL = "https://www.cgeonline.com.ar/informacion/apertura-de-citas.html"

def remove_enter_elements(l):
    ans = []
    for element in l:
        if element != '\n':
            ans.append(element)
    return ans

def get_info():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }
    response = requests.get(URL, headers=headers)

    parser = BeautifulSoup(response.text, 'html.parser')
    table = parser.main.table.tbody
    for tr in remove_enter_elements(table.contents):
        tds = remove_enter_elements(tr.contents)
        if tds[0].string == 'Registro Civil-Nacimientos':
            return tds[1].string, tds[2].string
        
    raise RuntimeError("HTML structure changed")

def write_info_file(last_date, next_date):
    file = open("previous_info.txt", 'w')
    file.write(f'{last_date}\n{next_date}\n')
    file.close()

def info_changed(last_date, next_date):
    if not os.path.exists("previous_info.txt"):
        write_info_file(last_date, next_date)
        return False

    file = open("previous_info.txt", 'r')
    lines = file.readlines()
    file.close()
    previous_last_date = lines[0][:-1]
    previous_next_date = lines[1][:-1]

    if previous_last_date != last_date or previous_next_date != next_date:
        write_info_file(last_date, next_date)
        return True
    return False

def main():
    while True:
        try:
            last_date, next_date = get_info()
            if info_changed(last_date, next_date):
                msg = EmailMessage()
                msg['From'] = os.environ.get('EMAIL_FROM')
                msg['To'] = os.environ.get('EMAIL_TO')
                msg['Subject'] = 'There was a change on the website you\'re watching'
                msg.set_content(f'The webstite you\'re watching changed!\nHead to {URL}')
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(os.environ.get('EMAIL_FROM'), os.environ.get('EMAIL_PASSWORD'))
                    smtp.send_message(msg)
        except:
            msg = EmailMessage()
            msg['From'] = os.environ.get('EMAIL_FROM')
            msg['To'] = os.environ.get('EMAIL_TO')
            msg['Subject'] = 'Something went wrong on the website you\'re watching'
            msg.set_content(f'Something went wrong with your code. Check it please.')
            with smtplib.SMTP_SSL(os.environ.get('SMTP_HOST'), os.environ.get('SMTP_PORT')) as smtp:
                smtp.login(os.environ.get('EMAIL_FROM'), os.environ.get('EMAIL_PASSWORD'))
                smtp.send_message(msg)
        sleep(43200) # Sleep for 12 hours (43200 sec)

if __name__ == "__main__":
    main()