import os
import telebot
from dotenv.main import load_dotenv
load_dotenv()
chat_ids=[] 
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['add'])
def add_url(message):
    url = message.text
    url='\n'+url[5:]
    listOfUrls=open('item_urls.txt','a+')
    listOfUrls.write(url)
    listOfUrls.seek(0)
    listOfUrls.close()

@bot.message_handler(commands=['notify'])
def notify_on_change(message):
    global chat_ids
    chat_id = message.chat.id
    chat_ids.append(chat_id)
    
    # for i in chat_ids:
    #     bot.send_message(i,"done")
bot.infinity_polling()
