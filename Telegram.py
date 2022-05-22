#pip3 install python-telegram-bot
#pip3 install telegram-send

from telegram.ext import *
from telegram import *
#from telebot import *
from telegram.utils.helpers import escape_markdown
import telegram_send
import logging
import schedule
import math
import datetime
from datetime import datetime
import time
import re
import random
import json
import mysql.connector
from telegram.ext import Updater

ACCESS_TOKEN = ""
with open('../../passes.json', 'r') as json_file:
    data = json.load(json_file)
    ACCESS_TOKEN=data['TELEGRAM_TOKEN']
    NGROK_TOKEN = data['NGROK_TOKEN']
    PUBLIC_IP_SEND_TO = data['PUBLIC_IP_SEND_TO']
    mydb = mysql.connector.connect(
        host=data['DB_HOST'],
        user=data['DB_USER'],
        password=data['DB_PASSWORD'],
        database=data['DB_DATABASE']
    )
mysql_client = mydb.cursor();
updater = Updater(ACCESS_TOKEN)
dispatcher = updater.dispatcher

#needs itegration and changing code bc no one other than coder can message it and get apprioret
#{'update_id': 65572448, 'message': {'chat': {'first_name': 'Kyrylo', 'type': 'private', 'id': 371968951, 'username': 'ocbtube'}, 'delete_chat_photo': False, 'message_id': 3, 'photo': [], 'supergroup_chat_created': False, 'text': 'привет', 'entities': [], 'new_chat_photo': [], 'caption_entities': [], 'date': 1647697981, 'new_chat_members': [], 'group_chat_created': False, 'channel_chat_created': False, 'from': {'id': 371968951, 'is_bot': False, 'username': 'ocbtube', 'language_code': 'ru', 'first_name': 'Kyrylo'}}}    

#https://api.telegram.org/bot[TOKEN]/getMe  to verify

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


button1 = KeyboardButton('Show ALL')
button2 = KeyboardButton('Set new reminder')
keyboard_1 = ReplyKeyboardMarkup([[button1, button2]],resize_keyboard=True, one_time_keyboard=True)

def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! ",reply_markup=keyboard_1)



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
    x = text.replace(data, "")
    x = x.replace(za_ile, "")
    x = x.replace("/rem", "")
    x = x.replace("/learn", "")
    x = x.replace("/operations", "")
    return x

def test(update: Update, context: CallbackContext):
    message_back=operations(update, context)
    input_id = update.message.chat.id
    updater.bot.send_message(chat_id = input_id, text=message_back)

def operations(update: Update, context: CallbackContext):
    input_text = update.message.text
    input_date = update.message.date
    recipient_id = update.message.chat.id
    text_from_message=parsing_text(input_text)
    sql=('SELECT `recipient_id` FROM `users` WHERE `telegram_id`={}'.format(recipient_id))
    mysql_client.execute(sql)
    # gets the number of rows affected by the command executed
    myresult = mysql_client.fetchall()
    if mysql_client.rowcount == 0:
        sql=('INSERT INTO `users`(`telegram_id`) VALUES ({})'.format(recipient_id))
        mysql_client.execute(sql)
        mydb.commit()
        sql=('SELECT `recipient_id` FROM `users` WHERE `telegram_id`={}'.format(recipient_id))
        mysql_client.execute(sql)
        myresult = mysql_client.fetchall()
    if re.search(r"(Pokaz|Show|placeholdershow)",text_from_message):
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
    elif parsing_date(input_text):
        date = parsing_date(input_text)
        output_rem = 'text: ' + str(text_from_str) + '\n' + 'date: ' + str(date) + '\n' + 'id: ' + str(input_id)
        sql=('INSERT INTO `todo`(`recipient_id`, `Text`, `data`) VALUES ({},"{}","{}")'.format(myresult[0][0],text,date_formated))
        mysql_client.execute(sql)
        mydb.commit()
        return "Zostal dodane"
        
    elif re.search(r"(in|za|через)",input_text):
        try:
            format_temp = re.search(r"(in|za|через) [0-9]+ ((dni|day|дня)|(godzin|hour|часа)|(minut|minute|минуты))", input_text)
        except (TypeError, AttributeError):
            return "problem z za"
        try:
            za_jak_dlugo = re.search(r"[0-9]+",format_temp.group()).group()
        except (TypeError, AttributeError):
            return "problem z data"
        type_of = ""
        if re.search(r"(dni|day|дня)",format_temp.group()):
            type_of = 'day'
        elif re.search(r"(godzin|hour|часа)",format_temp.group()):
            type_of = "hour"
        else:
            type_of = "minute"
        parsing_text(input_text)
        sql=('INSERT INTO `todo`(`recipient_id`, `Text`, `data`) VALUES ({},"{}",DATE_ADD(SYSDATE(), INTERVAL {} {}))'.format(myresult[0][0],text_from_message,za_jak_dlugo,type_of))
        mysql_client.execute(sql)
        mydb.commit()
        return "Zostało dodane"
    
    elif re.search(r"(Generuj kod|Generate code|Сгенерируй код)",input_text):
        kod=random.randint(100,999)
        user=myresult[0][0]
        #check if already not parred
        sql=('SELECT CASE WHEN EXISTS (SELECT * FROM `users` WHERE `facebook_id` is not null and `telegram_id` is not null and `telegram_id`={}) THEN "True" ELSE "False" END'.format(recipient_id))
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
        sql=('SELECT CASE WHEN EXISTS (SELECT * FROM `users` WHERE `facebook_id` is not null and `facebook_id` is not null and `facebook_id`={}) THEN "True" ELSE "False" END'.format(recipient_id))
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
            sql=('SELECT `facebook_id` from `Users` where `recipient_id`={}'.format(user_parring))
            mysql_client.execute(sql)
            myresult = mysql_client.fetchall()
            sql=('UPDATE `Users` SET `facebook_id` = {} WHERE `recipient_id`={}'.format(myresult[0][0],user_now))
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

def rem(update: Update, context: CallbackContext):
    input_text = update.message.text
    input_date = update.message.date
    input_id = update.message.chat.id
    print(input_id)
    text_from_str = parsing_text(input_text)
    
    if parsing_date(input_text):
        date = parsing_date(input_text)
        print('dodano do bazy')
        output_rem = 'text: ' + str(text_from_str) + '\n' + 'date: ' + str(date) + '\n' + 'id: ' + str(input_id)
        updater.send_message(chat_id = input_id, text=output_rem)
         #  sql = ('INSERT INTO `todo`(`recipient_id`, `Text`, `data`) VALUES ({},"{}","{}")'.format(user_id, text_from_str, date))
    elif re.search(r"(in|za|через)",input_text).group() in input_text:
        try:
            format_temp = re.search(r"(in|za|через) [0-9]+ ((dni|day|дня)|(godzin|hour|часа)|(minut|minute|минуты))", input_text)
        except (TypeError, AttributeError):
            return "problem z za"
        try:
            za_jak_dlugo = re.search(r"[0-9]+",format_temp.group()).group()
        except (TypeError, AttributeError):
            return "problem z data"
        type_of = ""
        if re.search(r"(dni|day|дня)",format_temp.group()):
            type_of = 'day'
        elif re.search(r"(godzin|hour|часа)",format_temp.group()):
            type_of = "hour"
        else:
            type_of = "minute"
        parsing_text(input_text)
      #  sql = (
           # 'INSERT INTO `todo`(`recipient_id`, `Text`, `data`) VALUES ({},"{}",DATE_ADD(SYSDATE(), INTERVAL {} {}))'.format( myresult[0], text, date, type_of))
       # mysql_client.execute(sql)
        #mydb.commit()
        output_rem = 'text: ' + text_from_str + '\n' + 'date: ' + za_jak_dlugo + '\n' + 'id: ' + type_of
        updater.bot.send_message(chat_id = input_id, text=output_rem)

    else: updater.bot.send_message(chat_id = input_id, text='COs poszlo nie tak')



#def learn(update: Update, context: CallbackContext):

#def all(update: Update, context: CallbackContext):
      #  (select * from todo where recipient_id = ??)




#text_handler = MessageHandler(Filters.text & (~Filters.command), rem)
#dispatcher.add_handler(text_handler)

def main() -> None:
    # Create the Updater and pass it your bot's token.

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
  #  dispatcher.add_handler(CommandHandler("learn", learn))
    dispatcher.add_handler(CommandHandler("rem", rem))
    dispatcher.add_handler(CommandHandler("operations", test))
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()

