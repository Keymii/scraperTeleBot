from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
def scrapeData(url):
    DRIVER_PATH = '/path/to/chromedriver'

    #Headless Mode
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

    driver.get(url)
    asin=url.split('dp/')[1]

    price="-"
    availability="-"
    title="-"
    imgLink="-"
    bestSellerData={"-":"-"}
    rating="-"
    aboutItem="-"
    technicalDetails={"-":"-"}
    additionalDetails={"-":"-"}

    title=driver.find_element(By.XPATH,"//span[@id='productTitle'][@class='a-size-large product-title-word-break']").text
    imgLink=driver.find_element(By.XPATH,"//span[@class='a-declarative']/div[@id='imgTagWrapperId']/img").get_attribute('src')
    availability=driver.find_element(By.XPATH,"//div[@id='availability']/span").text
    if "In stock" in availability:
        price = driver.find_element(By.XPATH,"//span[@class='a-price-whole']").text
    
    try:
        rating=driver.find_element(By.XPATH,"//th[text()='Customer Reviews']/../td").text
    except:
        pass

    try:
        bestSellerRankText=driver.find_element(By.XPATH,"//th[text()=' Best Sellers Rank ']/../td").text
        bestSellerList=bestSellerRankText.split("\n")
        bestSellerData={}
        for i in bestSellerList:
            i=i.split(" in ")
            rank=int(i[0].split("#")[1].replace(',',''))
            category=i[1].split(" (")[0]
            bestSellerData[category]=rank
    except:
        pass

    try:
        aboutUL=driver.find_elements(By.XPATH,"//div[@id='feature-bullets']/h1[text()=' About this item ']/../ul/li")
        aboutItem=[i.text for i in aboutUL]
        aboutItem="\n".join(aboutItem)
    except:
        pass

    try:
        technicalDetailsTable=driver.find_elements(By.XPATH,"//table[@class='a-keyvalue prodDetTable'][@id='productDetails_techSpec_section_1']/tbody/tr")
        technicalDetails={}
        for e in technicalDetailsTable:
            property= e.find_element(By.XPATH,".//th").text
            value = e.find_element(By.XPATH,".//td").text
            technicalDetails[property]=value

    except:
        pass

    try:
        additionalDetailsTable=driver.find_elements(By.XPATH,"//table[@class='a-keyvalue prodDetTable'][@id='productDetails_detailBullets_sections1']/tbody/tr")
        additionalDetails={}
        for e in additionalDetailsTable:
            property= e.find_element(By.XPATH,".//th").text
            value = e.find_element(By.XPATH,".//td").text
            additionalDetails[property]=value

    except:
        pass

    currTime=datetime.now().strftime('%d/%m/%y %H:%M:%S')
    data= {
        "url":url,
        "asin":asin,
        currTime:{
            "title":title,
            "availability":availability,
            "price":price,
            "image":imgLink,
            "rating":rating,
            "about":aboutItem,
            **technicalDetails,
            **additionalDetails
        }
    }
    return data