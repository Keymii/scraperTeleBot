import pandas as pd
import pymongo
from db_operations import filterWithUrl
import os
from io import BytesIO
from urllib.request import urlopen
from UliPlot.XLSX import auto_adjust_xlsx_column_width
from collections import OrderedDict

noOfEntriesShown=800 #change this value to get more entries in excel sheets corresponding to each product

#authorization
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
database = myclient["amazonItems"]
itemsCollection = database["items"]

def generateXL(asinList):
    try:
        filename="report.xlsx"
        writer=pd.ExcelWriter(filename)
        try:    
            os.remove(filename)
        except:
            pass
        
        

        writer.book.formats[0].set_text_wrap()
        #making sheet "Home"
        homeData={}
        sheetname="Home"
        i=2
        for asin in asinList:
            url="https://www.amazon.in/dp/"+asin.replace(" ","").replace("\n","")
            data = filterWithUrl(url,itemsCollection)
            latestDate=data["latest"]
            latestData=data[latestDate]
            homeReport={
                "ASIN":latestData.get("ASIN"),
                "Title":latestData.get("title"),
                "Image":latestData.get("image"),
                "Price":latestData.get("price"),
                "Availability":latestData.get("availability"),
                "Rating":latestData.get("rating"),
                "About":latestData.get("about"),
                "Best Sellers Rank":latestData.get("Best Sellers Rank")

            }
            homeData[asin]=homeReport
            
        df = pd.DataFrame(homeData).T
        df.to_excel(writer,sheet_name=sheetname,index=False)
        auto_adjust_xlsx_column_width(df, writer, sheet_name=sheetname, margin=10)

        #making sheets of individual products

        #adding images to sheet
        i=2
        for asin in homeData.keys():
            try:
                img_url=homeData[asin]["Image"]
                image_data = BytesIO(urlopen(img_url).read())
                worksheet = writer.sheets["Home"]
                worksheet.insert_image('C'+str(i), img_url,{'image_data': image_data,'x_scale': 0.25, 'y_scale': 0.25})
            except:
                pass
            i+=1
    #adding data to sheet
        for asin in asinList:
            sheetname=asin
            url="https://www.amazon.in/dp/"+asin.replace(" ","").replace("\n","")
            data = filterWithUrl(url,itemsCollection)
            
            del data["latest"]
            del data["asin"]
            del data["url"]
            del data["_id"]
            global noOfEntriesShown
            data = OrderedDict(reversed(list(data.items())[:noOfEntriesShown]))
            df = pd.DataFrame(data).T
            df.to_excel(writer,sheet_name=sheetname,index=True)
            auto_adjust_xlsx_column_width(df, writer, sheet_name=sheetname, margin=0)

        writer.save()
    except Exception as e:
        print(e)


