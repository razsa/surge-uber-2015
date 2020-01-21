class config:
    locations = [{
        'name': 'Bankhead/Grant-Park',
        'start_address': '317 Joseph E Lowery Blv',
        'start_latitude': 33.763481,
        'start_longitude': -84.417483,
        'end_address': '883 Boulevard SE',
        'end_latitude': 33.730078,
        'end_longitude': -84.368431
    }, {
        'name': 'Midtown',
        'start_address': '345 Boulevard NE',
        'start_latitude': 33.763879,
        'start_longitude': -84.371904,
        'end_address': '1512 Northside Dr NW',
        'end_latitude': 33.795983,
        'end_longitude': -84.407953
    }]
    url = 'https://api.uber.com/v1/estimates/price'
    key = API_KEY
    email = ['email@yahoo.com']
    source = 'email@gmail.com'
    product = 'uberX'
    min_surge = 1.0
    timer = 10
    gmail_user = "email@gmail.com"
    gmail_pwd = "password"

##
# script
##
import requests
import time
import smtplib
import os
import sys
from email.mime.text import MIMEText
from subprocess import Popen, PIPE


def send(text):
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s""" % (
        config.source, ", ".join(config.email), text, text)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(config.gmail_user, config.gmail_pwd)
    server.sendmail(config.source, config.email, message)
    server.close()
    print('Sending email - %s' % (text))


def listen():
    length = len(config.locations)
    pre_surge = [1 for i in range(length)]
    while True:
        for index in range(length):
            parameters = config.locations[index]
            parameters['server_token'] = config.key
            try:
                response = requests.get(config.url, params=parameters)
                data = response.json()
                if 'prices' in data:
                    data = [i for i in data['prices'] if i.get(
                        'localized_display_name') == config.product]
                    if len(data) == 1:
                        surge = data[0].get('surge_multiplier')
                        msg = '%s, Surge: %.2f' % (parameters['name'], surge)
                        if surge >= config.min_surge and pre_surge[index] != surge:
                            pre_surge[index] = surge
                            send(msg)
                        else:
                            print('Checking - %s (min: %.2f)' % (msg, config.min_surge))
                    else:
                        print('Unidentifiable product (%s).' % config.product)
                else:
                    print('Incomplete response. Prices array missing.')
            except Exception as e:
                print(str(e))
        sys.stdout.flush()
        time.sleep(config.timer)
listen()
