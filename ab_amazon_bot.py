import os
import telebot
from dotenv.main import load_dotenv
from excelWriter import generateXL
import pymongo
from data_collector import scrapeData
from db_operations import addItem, filterWithUrl
from datetime import datetime
import threading

schedule=int(datetime.now().strftime('%H%M'))

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
access_pswd=os.environ.get('PSWD')


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
database = myclient["amazonItems"]
chatIds = database["notify"]
itemsCollection = database["items"]

def filterWithChatId(chat_id,collection):
    query={"chat_id":chat_id}
    item=collection.find(query)
    for i in item:
        return i

    
@bot.message_handler(commands=['start', 'hello','hi'])
def send_welcome(message):
    bot.reply_to(message, "Hi, what do you wanna do?\n(type /help for help)")
@bot.message_handler(commands=['help','h'])
def send_help(message):
    helpMsg="""**Use the following commands to access me**
    /register <password> : use this command to add yourself to the list of people who want to access the bot
    /add <ASIN> : use this command to add ASIN number of a product you want to track
    /report : use this command to obtain an .xlsx report
    /scrape : to scrape again at real time
    /help or /h : use this command to access this help message again"""
    
    bot.reply_to(message,helpMsg)
    pass
@bot.message_handler(commands=['add'])
def add_url(message):
    listOfChatIDs= chatIds.find({}, {"chat_id": 1,"_id":0})
    chat_id = message.chat.id
    if {'chat_id':chat_id} in listOfChatIDs:
        asin = message.text
        asin='\n'+asin[5:]

        if asin !="\n":
            listOfUrls=open('item_urls.txt','a+')
            listOfUrls.write(asin)
            listOfUrls.seek(0)
            listOfUrls.close()
    else:
        bot.reply_to(message, "Register yourself first")

@bot.message_handler(commands=['scrape'])
def scrape_now(message):
    listOfChatIDs= chatIds.find({}, {"chat_id": 1,"_id":0})
    chat_id = message.chat.id
    if {'chat_id':chat_id} in listOfChatIDs:
         global schedule
         schedule=int(datetime.now().strftime('%H%M'))
    else:
        bot.reply_to(message, "Register yourself first")

@bot.message_handler(commands=['report'])
def generateReport(message):
    listOfChatIDs= chatIds.find({}, {"chat_id": 1,"_id":0})
    chat_id = message.chat.id
    if {'chat_id':chat_id} in listOfChatIDs:
        try:
            chat_id = message.chat.id
            report=open('report.xlsx','rb')
            bot.send_document(chat_id,report)
            report.close()
        except:
            bot.reply_to(message, "Sorry, some error occurred")
    else:
        bot.reply_to(message, "Register yourself first")
@bot.message_handler(commands=['register'])
def notify_on_change(message):
    chat_id = message.chat.id
    pswd=message.text[10:]
    if pswd==access_pswd:
        exists=filterWithChatId(chat_id,chatIds)
        if exists ==None:
            var=chatIds.insert_one({"chat_id":chat_id})    
            bot.reply_to(message, "Okay, I will remind you of changes")        
        else:
            bot.reply_to(message, "Don't worry, I remember you")
    else:
        bot.reply_to(message, "wrong password")

def changeDetected(url, title):
    for x in chatIds.find({}, {"chat_id": 1}):
        chat_id=x["chat_id"]
        bot.send_message(chat_id, text=title+'\n'+url)

def scrpaingProcess():
    global schedule
    ASINs=open("item_urls.txt").readlines()
    schedule=int(datetime.now().strftime('%H%M'))
    while True:
        currTime=int(datetime.now().strftime('%H%M'))
        if (currTime>=schedule) and not (currTime >=2300 and schedule < 100):
            for asin in ASINs:
                url="https://www.amazon.in/dp/"+asin.replace(" ","").replace("\n","")

                print("\n iter\n\n\n\n\n")
                data = scrapeData(url)
                itemFromDB=filterWithUrl(url,itemsCollection)
                compDataNew=data
                addItem(data,itemsCollection)
                if itemFromDB != None:
                    compDataOld=itemFromDB[itemFromDB["latest"]]
                    
                    del compDataNew["url"]
                    del compDataNew["asin"]

                    compDataNew=compDataNew[list(compDataNew.keys())[0]]
                    del compDataNew["image"]
                    del compDataOld["image"]

                    if compDataNew!=compDataOld:
                        changeDetected(url,compDataNew['title'])
            
            f=open("item_urls.txt",'r').readlines()
            generateXL(f)
            schedule=currTime+100

t1=threading.Thread(target=scrpaingProcess)
t1.start()


bot.infinity_polling()
