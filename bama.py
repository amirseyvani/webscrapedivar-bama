import time
import bs4
import re,sys
from selenium import webdriver
import traceback
import datetime
import unidecode
import io
import Jalali
import math
import sqlite3
import uuid



def get_driver(driver_width=600, driver_height=300, limit=300):
    connections_attempted = 0
    while connections_attempted < limit:
        try:
            driver = webdriver.Chrome('chromedriver.exe')
            driver.set_window_size(driver_width , driver_height)
            return driver
        except Exception as e:
            connections_attempted += 1
            print('Getting driver again...')
            print('  connections attempted: {}'.format(connections_attempted))
            print('  exception message: {}'.format(e))
            traceback.print_exc()





def process_whole_page(pages):
    results = []
    url = 'https://bama.ir/car?page='
    for i in range(pages):
        driver = get_driver()
        driver.get(url + str(i+1))
        soup = bs4.BeautifulSoup(driver.page_source,'lxml')
        result = soup.findAll('div',{'class' : "listdata"})
        for item in result:
            results.append(item)
    return results

def getadurls(item):
    item = str(item)
    caraddreg = re.compile(r'href=[\'"]?([^\'" >]+)')
    caraddlist = re.findall(caraddreg,item)
    caradd = caraddlist[0]
    return caradd




def getcardetailspage(caraddurl):
    driver = get_driver()
    driver.get(caraddurl)
    time.sleep(3)
    x = driver.find_elements_by_css_selector('[onclick="openContactNum()"]')
    if(not(x == [])):
        print('--')
        x[0].click()
    else:
        return -1
    soup = bs4.BeautifulSoup(driver.page_source,'lxml')
    result = soup.findAll('div', {'class': "inforight"})
    return result




def extracatcardetails(item):
    item = str(item)
    item = item.replace('\n','').replace('  ',' ')
    item = item[1:-1]
    title_regex = re.compile(r'<(\s*span[^>]*|span)>(.*?)<\s*/\s*span>')
    title_list_regex = re.findall(title_regex, item)
    temp = []
    for item in title_list_regex:
        temp.append([item[0].strip(' '), item[1].strip(' ')])
    return temp




def getadtime(adtimestring):
    currdate = datetime.datetime.now().strftime("%y-%m-%d")
    if('لحظه' in adtimestring):
        return currdate
    if('روز' in adtimestring and not('دیروز' in adtimestring)):
        return currdate - (datetime.timedelta(days=int(adtimestring.split(' ')[0])))
    if('دیروز' in adtimestring):
        return currdate - (datetime.timedelta(days=1))
    if('ساعت'):
        return currdate
    if('دقیقه'):
        return currdate
    if('ماه'):
        return currdate - datetime.timedelta(days=30*int(adtimestring.split(' ')[0]))




def convertyear(year):
    return Jalali.Persian((year+'-1-1')).gregorian_datetime().strftime('%y')

def convertkarkard(karkard):
    if(karkard == ''):
        return -1
    temp = (karkard.split(' ')[0]).split(',')
    kar = 0
    for i in range(len(temp)):
        kar += int(temp[i-len(temp)+1]) * math.pow(1000,i)
    return int(kar)

def convertprice(price):
    if(price == ''):
        return -1
    if('tamas' in price):
        return -1
    temp = price.split(',')
    prc = 0
    for i in range(len(temp)):
        prc += int(temp[i - len(temp) + 1]) * math.pow(1000, i)
    return int(prc)

def convertbadane(badane):
    temp = badane.split(' ')
    rang = temp[0]
    if(rang == 'بدون'):
        return 0
    if(rang == 'یک'):
        if(temp[1] == 'لکه'):
            return 1
        if(temp[1] == 'درب'):
            return 10
    if (rang == 'دو'):
        if(temp[1] == 'لکه'):
            return 2
        if(temp[1] == 'درب'):
            return 13
    if (rang == 'چند'):
        return 3
    if (rang == 'دور'):
        return 4
    if (rang == 'صافکاری'):
        return 5
    if (rang == 'گلگیر'):
        if(temp[1] == 'رنگ'):
            return 6
        if(temp[1] == 'تعویض'):
            return 9
    if(rang == 'کامل'):
        return 7
    if(rang == 'کاپوت'):
        if(temp[1] ==  'تعویض'):
            return 8
        if(temp[1] == 'رنگ'):
            return 11
    if(rang == 'درب'):
        return 12
    if('تصادف' in rang):
        return 13
    if('اتاق' in rang):
        return 14
    if('اوراق' in rang):
        return 15
    if('سوخته' in rang):
        return 16
    return -1

def convertfuel(sukht):
    if('بن' in sukht):
        return 0
    if('بر' in sukht):
        return 1
    if('سوز' in sukht):
        return 2
    if('زل' in sukht):
        return 3
    return -1

def convertgearbox(gear):
    if('اتو' in gear):
        return 0
    if('دنده' in gear):
        return 1
    return -1

def realdata(data):
    year = ''
    brand = ''
    model = ''
    price = ''
    karkard = ''
    adtime = ''
    color = ''
    badane = ''
    ostan = ''
    bazdid = ''
    sukht = ''
    gearbox = ''
    phone = ''
    for item,anoth in zip(data,data[1:]):
        if ('datetime' in item[0]):
            year = item[1]
        if('brand' in item[0]):
            brand = item[1]
        if('model' in item[0]):
            model = item[1]
        if('price' in item[0] and not('Curr' in item[0]) ):
            if(' ' in item[1]):
                price = 'tamas'
            else:
                price = item[1]
        if('span' in item[0] and  'کیلومتر' in item[1]):
            karkard = item[1]
        if('color' in item[1] and 'itemprop' in item[1]):
            colorreg = re.compile(r'<\s*f[^>]*>(.*?)<\s*/\s*f>')
            colorlist = re.findall(colorreg, item[1])
            color = colorlist[0]
        if('span' in item[0] and 'پیش' in item[1]):
            adtime = getadtime(item[1])
        if(item[0] == 'span' and 'رنگ' in item[1]):
            badane = item[1]
        if('استان' in item[1]):
            ostan = anoth[1]
        if('بازديد' in item[1]):
            bazdid = anoth[1]
        if ('سوخت' in item[1]):
            sukht = anoth[1]
        if('گیربکس' in item[1]):
            gearbox = anoth[1]
        if('phone-field' in item[0]):
            #phone = anoth[1][1:-1]+item[1]
            phone = item[1]
            if('color' in phone):
                phone = 'no-numb'
        address = ostan + ' ' + bazdid
    return [brand,model,convertyear(year),convertkarkard(karkard),convertprice(price),color,adtime,convertbadane(badane),address,convertfuel(sukht),convertgearbox(gearbox),phone]


def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn

def create_table(conn, create_table_sql):
        c = conn.cursor()
        c.execute(create_table_sql)

def enterdatatodb(conn, list, id):
    for item in list:
        print(type(item))
    c = conn.cursor()
    c.execute("INSERT INTO  bamacars VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (id,list[0],list[1],list[2],float(list[3]),float(list[4]),list[5],list[6],list[7],list[8],list[9],list[10],list[11]))
    conn.commit()



def writelinkstofile(pages):
    x = process_whole_page(pages)
    f = open('adds.txt', 'w')
    for item in x:
        f.writelines('https://bama.ir' + getadurls(item)+"\n")
    f.close()

def createdbtable(data):
    create_table_sql = """ CREATE TABLE  bamacars (
                          id NCHAR PRIMARY KEY ,
                          brand NCHAR L,
                          model NCHAR ,
                          year NCHAR ,
                          karkar FLOAT ,
                          price FLOAT ,
                          color NCHAR ,
                          adtime NCHAR ,
                          badane INTEGER ,
                          addres NCHAR  ,
                          sukht INTEGER ,
                          gearbox INTEGER ,
                          phone NCHAR
                          );"""


    conn = create_connection('bama.db')
    create_table(conn, create_table_sql)



def writeadstofile(item):
    x = getcardetailspage(item)
    if(x != -1):
        temp = str([0])
        f = open(item.split('/')[4]+".txt",'w',encoding='utf-8')
        f.write(temp)
    else:
        print('ok!')

def test():
    f = open('adds.txt', 'r')
    ads = f.read().split('\n')
    for item in ads:
        writeadstofile(item)

def makecleardata():
    f = open('adds.txt','r')
    ads = f.read().split('\n')
    data = []
    counter = 1
    for item in ads:
        print(counter)
        f= open(str(item)+'.txt','r')
        temp = extracatcardetails(f.read())
        temp = realdata(temp)
        data.append(temp)
        counter += 1
    conn = create_connection('bama.db')
    for item in data:
        enterdatatodb(conn, item, str(uuid.uuid4()).replace('-', ''))


def select_all_tasks(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM bamacars")

    rows = cur.fetchall()

    for row in rows:
        print(row)

test()
