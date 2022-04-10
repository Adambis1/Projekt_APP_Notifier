#pip3 install mysql-connector
#pip3 install Flask
#pip3 install pymessenger
#pip3 install pyngrok
  
#Python libraries that we need to import for our bot
import random
import os, sys
import json
import re, string
import mysql.connector
from flask import Flask, request
from pymessenger.bot import Bot
from datetime import datetime
from pyngrok import ngrok

#os.system()
#os.system("curl -s http://localhost:4040/api/tunnels > tunnels.json")

#with open('tunnels.json') as data_file:
#    datajson = json.load(data_file)


#msg = "ngrok URL's: \n"
#for i in datajson['tunnels']:
#  msg = msg + i['public_url'] +'\n'

app = Flask(__name__)
ACCESS_TOKEN = ''
# need's to be more secure than in code.
VERIFY_TOKEN = ''
NGROK_TOKEN = ''
PUBLIC_IP_SEND_TO = ''
with open('../../passes.json', 'r') as json_file:
    data = json.load(json_file)
    ACCESS_TOKEN=data['FB_ACCESS_TOKEN']
    VERIFY_TOKEN=data['FB_VERIFY_TOKEN']
    NGROK_TOKEN = data['NGROK_TOKEN']
    PUBLIC_IP_SEND_TO = data['PUBLIC_IP_SEND_TO']
    mydb = mysql.connector.connect(
      host=data['DB_HOST'],
      user=data['DB_USER'],
      password=data['DB_PASSWORD'],
      database=data['DB_DATABASE']
    )
mysql_client = mydb.cursor();
ngrok.set_auth_token(NGROK_TOKEN)
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

def parsing_date(input):
    data = re.search(r"(\d+[/.]\d+[/.]\d+.*\d+:\d+)|(\d+[/.]\d+[/.]\d+)|(\d+:\d+)", input)
    try:
        date_formated = datetime.strptime(str(data.group(0)), '%d.%m.%Y %H:%M')
    except:
        return None
    date_formated = date_formated.strftime('%Y-%m-%d %H:%M')
    return date_formated


def parsing_text(text):
    data = re.search(r"(\d+[/.]\d+[/.]\d+.*\d+:\d+)|(\d+[/.]\d+[/.]\d+)|(\d+:\d+)", text)
    if data:
        data = str(data.group(0))
    else: data = "None"
    za_ile = re.search(r"(in|za|через) [0-9]+ ((dni|day|дня)|(godzin|hour|часа)|(minut|minute|минуты))", text)
    if za_ile:
        za_ile = str(za_ile.group(0))
    else: za_ile = "None"
    return x

def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

#supoort for commands
def get_message(text_from_message, recipient_id):
    if "help" in text_from_message:
        return "Aby zobaczyć liste wpisz !Pokaz\nJesli chcesz dokonać wpisu wpisz \n!Zrob [data - DD.MM.YYYY lub za [liczba] [dni/godziny/minuty]] [co?]"
    if "!" in text_from_message:
        sql=('SELECT `recipient_id` FROM `users` WHERE `facebook_id`={}'.format(recipient_id))
        mysql_client.execute(sql)
        # gets the number of rows affected by the command executed
        myresult = mysql_client.fetchall()
        if mysql_client.rowcount == 0:
            sql=('INSERT INTO `users`(`facebook_id`) VALUES ({})'.format(recipient_id))
            mysql_client.execute(sql)
            mydb.commit()
            sql=('SELECT `recipient_id` FROM `users` WHERE `facebook_id`={}'.format(recipient_id))
            mysql_client.execute(sql)
            myresult = mysql_client.fetchall()
        if "!Pokaz" in text_from_message:
            sql=('SELECT `Text`, DATE_FORMAT(`data`, "%d.%m.%Y %T") FROM `todo` WHERE `recipient_id`={} and `data`>SYSDATE() order by DATE_FORMAT(`data`, "%d.%m.%Y") desc'.format(myresult[0][0]))
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
                try:
                    format_temp=re.search("^!Zrob za [0-9]+ (dni|godzin|minut)", text_from_message).group()
                except (TypeError, AttributeError):
                    return "Cos poszlo nie tak"
                text = text_from_message[len(format_temp)+1:]
                date = re.search("[0-9]+", format_temp).group()
                type_of = ""
                if "dni|day|дня" in format_temp:
                    type_of = 'day'
                elif "godzin" in format_temp:
                    type_of = "hour"
                else:
                    type_of = "minute"
                #INSERT INTO `todo`(`recipient_id`, `Text`, `data`) VALUES (3,"jaka",DATE_ADD(SYSDATE(), INTERVAL 3 day))
                sql=('INSERT INTO `todo`(`recipient_id`, `Text`, `data`) VALUES ({},"{}",DATE_ADD(SYSDATE(), INTERVAL {} {}))'.format(myresult[0][0],text,date,type_of))
                mysql_client.execute(sql)
                mydb.commit()
                return "Zostało dodane "
            else:
                try:
                    format_temp=re.search("^!Zrob [0-9][0-9].[0-9][0-9].[0-9]+", text_from_message).group()
                except (TypeError, AttributeError):
                    return "Cos poszlo nie tak"
                text = text_from_message[len(format_temp)+1:]
                date = re.search("[0-9][0-9].[0-9][0-9].[0-9]+", format_temp).group()
                date_formated = datetime.strptime(date+' 08:00:00', '%d.%m.%Y %H:%M:%S')
                date_formated = date_formated.strftime('%Y-%m-%d %H:%M:%S')
                print('{}'.format(date_formated))
                #INSERT INTO `todo`(`recipient_id`, `Text`, `data`) VALUES (3,"{aaaaaaaaaaaaaaa}",'2022-03-28 08:00:00')
                sql=('INSERT INTO `todo`(`recipient_id`, `Text`, `data`) VALUES ({},"{}","{}")'.format(myresult[0][0],text,date_formated))
                mysql_client.execute(sql)
                mydb.commit()
                return "Zostało dodane "
        elif re.search(r"(Generuj kod|Generate code|Сгенерируй код)",input_text):
            kod=random.randint(100,999)
            user=myresult[0][0]
            #check if already not parred
            sql=('SELECT CASE WHEN EXISTS (SELECT * FROM `users` WHERE `facebook_id` is not null and `telegram_id` is not null and `facebook_id`={}) THEN "True" ELSE "False" END'.format(recipient_id))
            mysql_client.execute(sql)
            myresult = mysql_client.fetchall()
            if myresult[0][0]=="True":
                return "Konto zparowane"
            sql=('DELETE FROM `parowanie` WHERE `recipient_id`={}'.format(user))
            mysql_client.execute(sql)
            mydb.commit()
            while True:
                kod=random.randint(100,999)
                sql=('SELECT `kod` FROM `parowanie` WHERE `kod`={}'.format(kod))
                mysql_client.execute(sql)
                myresult = mysql_client.fetchall()
                if mysql_client.rowcount == 0:
                    break
            sql=('INSERT INTO `parowanie`(`recipient_id`, `date`, `kod`) VALUES ({},DATE_ADD(SYSDATE(), INTERVAL 30 minute),{})'.format(user,kod))
            mysql_client.execute(sql)
            mydb.commit()
            return "Generowany kod to: {}".format(kod)
        elif re.search(r"(Polacz|Connect|Подключи)",input_text):
            user_now=myresult[0][0] #fb user
            #check if already not parred
            sql=('SELECT CASE WHEN EXISTS (SELECT * FROM `users` WHERE `facebook_id` is not null and `telegram_id` is not null and `facebook_id`={}) THEN "True" ELSE "False" END'.format(recipient_id))
            mysql_client.execute(sql)
            myresult = mysql_client.fetchall()
            if myresult[0][0]=="True":
                return "Konto zparowane"
            #getting the code
            kod = re.search(r"[0-9]+", text_from_message)
            if kod:
                sql=('SELECT `recipient_id`, `date` FROM `parowanie` WHERE `kod`={}'.format(kod.group()))
                mysql_client.execute(sql)
                myresult = mysql_client.fetchall()
                if mysql_client.rowcount == 0:
                    return "Nie znalezono takiego kodu"
                user_parring=myresult[0][0]
                future = myresult[0][1]
                present = datetime.now()
                if present>=future:
                    sql=('DELETE FROM `parowanie` WHERE `recipient_id`={}'.format(user_parring))
                    mysql_client.execute(sql)
                    mydb.commit()
                    return "Kod wygasl"
                sql=('UPDATE `ToDo` SET `recipient_id`={} WHERE `recipient_id`={}'.format(user_now, user_parring))
                mysql_client.execute(sql)
                mydb.commit()
                sql=('SELECT `telegram_id` from `Users` where `recipient_id`={}'.format(user_parring))
                mysql_client.execute(sql)
                myresult = mysql_client.fetchall()
                sql=('UPDATE `Users` SET `telegram_id` = {} WHERE `recipient_id`={}'.format(myresult[0][0],user_now))
                mysql_client.execute(sql)
                mydb.commit()
                sql=('DELETE FROM `parowanie` WHERE `recipient_id`={} or `recipient_id`={}'.format(user_now,user_parring))
                mysql_client.execute(sql)
                mydb.commit()
                sql=('DELETE from `Users` WHERE `recipient_id`={}'.format(user_parring))
                mysql_client.execute(sql)
                mydb.commit()
                return "Konta polaczone"
            else:
                return get_message_rand()
                    


    return get_message_rand()
#chooses a random message to send to the user
def get_message_rand():
    sample_responses = ["Nie wiem o co ci chodzi!", "Wpisz !help aby zobaczyc funkcjonalnosc", "Ehhh ... !", "No :)"]
    # return random item to the user
    return random.choice(sample_responses)

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    #__init__()
    #http_tunnel = ngrok.connect(50000, 'http')
    #tunnels = ngrok.get_tunnels()
    #msg_to_adambis1='ngrok URL\'s: \n'+tunnels[0].public_url+'\n'+tunnels[1].public_url
    #send_message(PUBLIC_IP_SEND_TO, msg_to_adambis1)
    app.run(port=50000)
