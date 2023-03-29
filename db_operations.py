def filterWithUrl(url,collection):
    query={"url":url}
    item=collection.find(query)
    for i in item:
        return i
        
def addItem(data, collection):
    try:
        existingData=filterWithUrl(data["url"],collection)
        latestTime=list(data.keys())
        latestTime.remove('url')
        latestTime.remove('asin')
        latestTime=latestTime[0]
        if existingData==None:
            
            var=collection.insert_one(data)
            collection.update_one({"url":data["url"]},{"$set":{"latest":latestTime}})
            return True
        else:

            existingData[latestTime]=data[latestTime]
            collection.update_one({"url":data["url"]},{"$set":{latestTime:data[latestTime]}})
            collection.update_one({"url":data["url"]},{"$set":{"latest":latestTime}})
            return True
    except:
        return False

def deleteWithUrl(url,collection):
    query={"url":url}
    collection.delete_one(query)