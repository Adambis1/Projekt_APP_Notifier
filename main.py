from telegram.ext import *
from telegram import *
from telebot import *
from telegram.utils.helpers import escape_markdown
import telegram_send
import logging
import math
import datetime
from datetime import datetime
import time
import re


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
    context.bot.send_message(chat_id=update.effective_chat.id, text="Влад, ты? Фу , иди нахуй",reply_markup=keyboard_1
)



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
    za_ile = re.search(r"через [0-9]+ (дня|часа|минуты)", text)
    if za_ile:
        za_ile = str(za_ile.group(0))
    else: za_ile = "None"
    x = text.replace(data, "")
    x = x.replace(za_ile, "")
    x = x.replace("/rem", "")
    x = x.replace("/learn", "")
    return x

def rem(update: Update, context: CallbackContext):
    input_text = update.message.text
    input_date = update.message.date
    input_id = update.message.chat.id
    text_from_str = parsing_text(input_text)
    if parsing_date(input_text):
        date = parsing_date(input_text)
        print('dodano do bazy')
        output_rem = 'text: ' + str(text_from_str) + '\n' + 'date: ' + str(date) + '\n' + 'id: ' + str(input_id)
        telegram_send.send(messages=[output_rem])
         #  sql = ('INSERT INTO `todo`(`recipient_id`, `Text`, `data`) VALUES ({},"{}","{}")'.format(user_id, text_from_str, date))
    elif "через" in input_text:
        try:
            format_temp = re.search(r"через [0-9]+ (дня|часа|минуты)", input_text)
        except (TypeError, AttributeError):
            return "problem z za"
        try:
            za_jak_dlugo = re.search(r"[0-9]+",format_temp.group())
        except (TypeError, AttributeError):
            return "problem z data"
        type_of = ""
        if "дня" in format_temp.group():
            type_of = 'day'
        elif "часа" in format_temp.group():
            type_of = "hour"
        else:
            type_of = "minute"
        parsing_text(input_text)
      #  sql = (
           # 'INSERT INTO `todo`(`recipient_id`, `Text`, `data`) VALUES ({},"{}",DATE_ADD(SYSDATE(), INTERVAL {} {}))'.format( myresult[0], text, date, type_of))
       # mysql_client.execute(sql)
        #mydb.commit()
        output_rem = 'text: ' + str(text_from_str) + '\n' + 'date: ' + str(za_jak_dlugo.group(0)) + '\n' + 'id: ' + str(type_of)
        telegram_send.send(messages=[output_rem])

    else: telegram_send.send(messages=['cos poszlo nie tak'])



#def learn(update: Update, context: CallbackContext):

#def all(update: Update, context: CallbackContext):
      #  (select * from todo where recipient_id = ??)




#text_handler = MessageHandler(Filters.text & (~Filters.command), rem)
#dispatcher.add_handler(text_handler)

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater("5155925406:AAG7tqWtA9D5TmSonu50cTl5VuA4lJtk7RM")
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
  #  dispatcher.add_handler(CommandHandler("learn", learn))
    dispatcher.add_handler(CommandHandler("rem", rem))
    #dispatcher.add_handler(CommandHandler("all", all))
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()


