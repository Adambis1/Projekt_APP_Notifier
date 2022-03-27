#pip3 install Flask
#pip3 install pymessenger==0.0.7.0
  
#Python libraries that we need to import for our bot
import random
import os, sys
import json
import re, string
import mysql.connector
from flask import Flask, request
from pymessenger.bot import Bot
from datetime import datetime

app = Flask(__name__)
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
#mysql_client.execute("SELECT * FROM users where 'facebookid'==")

#myresult = mysql_client.fetch()


#for latter or env variables after implementing other modules
#def __init__():
#    with open('../../passes.json', 'r') as json_file:
#        data = json.load(json_file)
#        ACCESS_TOKEN=data['ACCESS_TOKEN']
#        VERIFY_TOKEN=data['VERIFY_TOKEN']

@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    else:
        # get message from user
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user 
                recipient_id = message['sender']['id']
                if message['message'].get('text'):
                    response_sent_text = get_message(message['message'].get('text'), recipient_id)
                    send_message(recipient_id, response_sent_text)
                #send anything for media
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message_rand()
                    send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

#supoort for commands
def get_message(text_from_message, recipient_id):
    if "!help" in text_from_message:
        return "Aby zobaczyć liste wpisz !Pokaz\nJesli chcesz dokonać wpisu wpisz \n!Zrob [data - DD.MM.YYYY lub za [liczba] [dni/godziny/minuty]] [co?]"
    if "!" in text_from_message:
        sql=('SELECT `recipient_id` FROM `users` WHERE `facebook_id`={}'.format(recipient_id))
        mysql_client.execute(sql)
        # gets the number of rows affected by the command executed
        myresult = mysql_client.fetchone()
        if mysql_client.rowcount == 0:
            sql=('INSERT INTO `users`(`facebook_id`) VALUES ({})'.format(recipient_id))
            mysql_client.execute()
            mydb.commit()
        else:
            if "!Pokaz" in text_from_message:
                sql=('SELECT `Text`, DATE_FORMAT(`data`, "%d.%m.%Y %T") FROM `todo` WHERE `recipient_id`={} and `data`>SYSDATE() order by DATE_FORMAT(`data`, "%d.%m.%Y") desc'.format(myresult[0]))
                mysql_client.execute(sql)
                myresult = list(mysql_client.fetchall())
                if mysql_client.rowcount == 0:
                    return "Brak zadan"
                else:
                    returnstring=""
                    for val in myresult:
                        returnstring=returnstring+val[1]+" "+val[0]+"\n"
                    return returnstring
            elif "!Zrob" in text_from_message:
                if "!Zrob za" in text_from_message:
                    format_temp=re.search("^!Zrob za +[0-9] (dni|godzin|minut)", text_from_message).group()
                    text = text_from_message[len(format_temp)+1:]
                    date = re.search("[0-9]+", format_temp).group()
                    type_of = ""
                    if "dni" in format_temp:
                        type_of = 'day'
                    elif "godzin" in format_temp:
                        type_of = "hour"
                    else:
                        type_of = "minute"
                    print(type_of)
                    #INSERT INTO `todo`(`recipient_id`, `Text`, `data`) VALUES (3,"jaka",DATE_ADD(SYSDATE(), INTERVAL 3 day))
                    sql=('INSERT INTO `todo`(`recipient_id`, `Text`, `data`) VALUES ({},"{}",DATE_ADD(SYSDATE(), INTERVAL {} {}))'.format(myresult[0],text,date,type_of))
                    mysql_client.execute(sql)
                    mydb.commit()
                    return "Zostało dodane "
                else:
                    format_temp=re.search("^!Zrob [0-9][0-9].[0-9][0-9].[0-9]+", text_from_message).group()
                    text = text_from_message[len(format_temp)+1:]
                    date = re.search("[0-9][0-9].[0-9][0-9].[0-9]+", format_temp).group()
                    date_formated = datetime.strptime(date+' 08:00:00', '%d.%m.%Y %H:%M:%S')
                    date_formated = date_formated.strftime('%Y-%m-%d %H:%M:%S')
                    print('{}'.format(date_formated))
                    #INSERT INTO `todo`(`recipient_id`, `Text`, `data`) VALUES (3,"{aaaaaaaaaaaaaaa}",'2022-03-28 08:00:00')
                    sql=('INSERT INTO `todo`(`recipient_id`, `Text`, `data`) VALUES ({},"{}","{}")'.format(myresult[0],text,date_formated))
                    mysql_client.execute(sql)
                    mydb.commit()
                    return "Zostało dodane "


    #myresult = mysql_client.fetchone()
        return "Brawo :)"
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return random item to the user
    return random.choice(sample_responses)
#chooses a random message to send to the user
def get_message_rand():
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return random item to the user
    return random.choice(sample_responses)

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    #__init__()
    app.run(port=50000)