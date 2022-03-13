#pip3 install Flask
#pip3 install pymessenger==0.0.7.0
  
#Python libraries that we need to import for our bot
import random
import os, sys
import json
from flask import Flask, request
from pymessenger.bot import Bot

app = Flask(__name__)
ACCESS_TOKEN = ''
# need's to be more secure than in code.
VERIFY_TOKEN = ''
bot = Bot(ACCESS_TOKEN)


#ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
#VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
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
                    response_sent_text = get_message()
                    send_message(recipient_id, response_sent_text)
                #send anything for media
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return random item to the user
    return random.choice(sample_responses)

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    __init__()
    app.run(port=50000)