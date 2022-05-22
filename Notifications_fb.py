#pip3 install mysql-connector
#pip3 install Flask
#pip3 install pymessenger
#pip3 install pyngrok
  
#Python libraries that we need to import for our bot
import random
import os, sys
import json
import schedule
import time
import re, string
import mysql.connector
from pymessenger.bot import Bot
from datetime import datetime

#os.system()
#os.system("curl -s http://localhost:4040/api/tunnels > tunnels.json")

#with open('tunnels.json') as data_file:
#    datajson = json.load(data_file)


#msg = "ngrok URL's: \n"
#for i in datajson['tunnels']:
#  msg = msg + i['public_url'] +'\n'

ACCESS_TOKEN = ''
# need's to be more secure than in code.
VERIFY_TOKEN = ''
with open('../../passes.json', 'r') as json_file:
    data = json.load(json_file)
    ACCESS_TOKEN=data['FB_ACCESS_TOKEN']
    VERIFY_TOKEN=data['FB_VERIFY_TOKEN']
    mydb = mysql.connector.connect(
      host=data['DB_HOST'],
      user=data['DB_USER'],
      password=data['DB_PASSWORD'],
      database=data['DB_DATABASE']
    )
mysql_client = mydb.cursor();
bot = Bot(ACCESS_TOKEN)



def send_schedule(recipient_id):
    sql= 'SELECT `Text`, DATE_FORMAT(`data`, "%d.%m.%Y %T") FROM `todo`'
    sql+= 'WHERE `recipient_id`={} AND DATE(sysdate()) = DATE(`data`) ORDER BY DATE_FORMAT(`data`, "%d.%m.%Y") DESC'.format(recipient_id[0])
    mysql_client.execute(sql)
    myresult = list(mysql_client.fetchall())
    if mysql_client.rowcount == 0:
        result = "Brak zadan"
    else:
        returnstring=""
        for val in myresult:
            returnstring=returnstring+val[1]+" "+val[0]+"\n"
        result = returnstring
    sql=  'SELECT `facebook_id` FROM `users` '
    sql+= 'WHERE `recipient_id`={} AND `facebook_id`'.format(recipient_id[0])
    mysql_client.execute(sql)
    myresult = list(mysql_client.fetchall())
    if mysql_client.rowcount > 0:
        fb_id = myresult[0][0]
        send_message(fb_id, result)

def send_schedule_to_all():
    sql= 'SELECT DISTINCT `recipient_id` FROM `todo` T NATURAL JOIN `users` U'
    sql+= 'WHERE DATE(sysdate()) = DATE(`data`) AND U.facebook_id ORDER BY DATE_FORMAT(`data`, "%d.%m.%Y") DESC'
    #wybieranie tych użytkowników, którzy mają dziś cokolwiek w planie.
    mysql_client.execute(sql)
    myresult = list(mysql_client.fetchall())
    for recip in myresult:
        send_schedule(recip)

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

schedule.every(5).minutes.do(send_schedule_to_all)

if __name__ == "__main__":
    #send_schedule_to_all()
    while True:
        schedule.run_pending()
        time.sleep(1)
