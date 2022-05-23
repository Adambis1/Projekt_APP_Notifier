# pip3 install mysql-connector
# pip3 install Flask
# pip3 install pymessenger
# pip3 install pyngrok

# Python libraries that we need to import for our bot
from telegram.ext import *
from telegram import *
import random
import os, sys
import json
import schedule
import time
import re, string
import mysql.connector
from pymessenger.bot import Bot
from datetime import datetime
from telegram.ext import Updater

ACCESS_TOKEN = ""
with open('../../passes.json', 'r') as json_file:
    data = json.load(json_file)
    ACCESS_TOKEN=data['TELEGRAM_TOKEN']
    mydb = mysql.connector.connect(
        host=data['DB_HOST'],
        user=data['DB_USER'],
        password=data['DB_PASSWORD'],
        database=data['DB_DATABASE']
    )
mysql_client = mydb.cursor();
updater = Updater(ACCESS_TOKEN)


def send_schedule(recipient_id):
    update: Update
    sql = 'SELECT `Text`, DATE_FORMAT(`data`, "%d.%m.%Y %T") FROM `todo` '
    sql += 'WHERE `recipient_id`={} AND DATE(sysdate()) = DATE(`data`) ORDER BY DATE_FORMAT(`data`, "%d.%m.%Y") DESC'.format(
        recipient_id[0])
    mysql_client.execute(sql)
    myresult = list(mysql_client.fetchall())
    if mysql_client.rowcount == 0:
        result = "Brak zadan"
    else:
        returnstring = "Powiadomienie\n"
        for val in myresult:
            returnstring = returnstring + val[1] + " " + val[0] + "\n"
        result = returnstring
    sql = 'SELECT `telegram_id` FROM `users` '
    sql += 'WHERE `recipient_id`={} AND `telegram_id`'.format(recipient_id[0])
    mysql_client.execute(sql)
    myresult = list(mysql_client.fetchall())
    if mysql_client.rowcount > 0:
        tg_id = myresult[0][0]
        updater.bot.send_message(chat_id=tg_id, text=result)


def send_schedule_to_all():
    print("Telegram Notify Sending {}".format(datetime.now()))
    sql = 'SELECT DISTINCT `recipient_id` FROM `todo` T NATURAL JOIN `users` U '
    sql += 'WHERE DATE(sysdate()) = DATE(`data`) AND U.telegram_id ORDER BY DATE_FORMAT(`data`, "%d.%m.%Y") DESC'
    mysql_client.execute(sql)
    myresult = list(mysql_client.fetchall())
    for recip in myresult:
        send_schedule(recip)

def send_message(recipient_id, response):
    def send_message_message(update: Update, context: CallbackContext):
        updater.bot.send_message(chat_id=recipient_id, text=response)
        return "success"

schedule.every(5).minutes.do(send_schedule_to_all)

if __name__ == "__main__":
    send_schedule_to_all()
    print("Telegram Notify {}".format(datetime.now()))
    while True:
        schedule.run_pending()
        time.sleep(1)
