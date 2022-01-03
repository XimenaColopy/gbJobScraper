import re
import requests
from bs4 import BeautifulSoup
import mysql.connector

headers = {'User-agent': 'Mozilla/5.0'}

#page_url = input('insert page url: ').strip()
link = input('insert link: ').strip()

#res = requests.get(str(page_url), headers=headers, timeout=5)
#soup = BeautifulSoup(str(res.text), features="html.parser", multi_valued_attributes=None)

import sys
sys.path.append('/home/ximena/auth')
import authJS

mydb = mysql.connector.connect(host=authJS.HOSTNAME, user=authJS.USERNAME, password=authJS.PASSWORD)
mycursor = mydb.cursor()
db_statement = "use {}".format(authJS.DATABASE)
mycursor.execute(db_statement)

tag = {}

def findPageUrl(link):
    sql = 'select pid from jobtemp where url = %s'
    args = (link,)
    main_cursor.execute(sql, args)
    pid = main_cursor.fetchone()[0]
    print('pid', pid)
    sql = 'select joburl from profiles where pid = {}'.format(pid)
    main_cursor.execute(sql)
    page_url = main_cursor.fetchone()[0]
    print('page_url', page_url)
    return page_url
    

def findDivInfo(div):
    tag['name'] = div.name
    for x, y in div.attrs.items(): tag[x] = y
    tag['contents'] = div


def hTag_r(item):
    #print('hTag_r is being called for', item)
    tag = item.find(re.compile('h\d'))
    print('\nHere is the tag', tag)
    if tag:
        label = tag.string.strip()
        if checkIfBad(item, label):
            findDivInfo(item)
            return label
    try:
        return hTag_r(item.parent)
    except:
        return None

def compileLists(des): #returns a list of regex statements 
    if des == 'label': 
        tid = 2
    elif des == 'class-label': 
        tid = 3
    else: 
        print('entered "des" incorrectly')
        return
    sql = 'select tag, diffregex from soup_tags where tid={}'.format(tid)
    other_cursor.execute(sql)
    data = other_cursor.fetchall()
    return [x[0] if x[1]==1 else '(^|^.*\W+){}($|\W+.*$)'.format(x[0]) for x in data]


def checkIfBad(item, label):
    bad_labels = compileLists('label')
    for bad in bad_labels: 
        if re.match(r''+bad, label): 
            print(label, 'was a bad match')
            return False
    if item.has_attr("class"):
        cls_names = compileLists('class-label')
        for bad in cls_names:
            if re.match(r''+bad, label):
                print(label, 'had a bad class name:', div['class'])
                return False
    print(label, 'is all good')
    return True


page_url = findPageUrl(link)
print('Page Url:', page_url)
res = requests.get(str(page_url), headers=headers, timeout=5)
soup = BeautifulSoup(str(res.text), features="html.parser", multi_valued_attributes=None)


labels = []
divs = soup.find_all('a', {'href' : link})
print('# occurances:', len(divs))
for div in divs:
    print('\ndiv:', div)
    if div.string:
        label = div.string
        print('the label is in the div string', label)
        if checkIfBad(div, label):
            findDivInfo(div)
            labels.append(label)

if not labels:
    #print('h tag check is being called')
    label = hTag_r(div)
    #print('do we have a label?', label)
    labels.append(label)


labels = [i for i in labels if i]#get rid of blanks
labels = list(dict.fromkeys(labels))# remove duplicates

print('here is the div info:', tag)

if len(labels) > 1: print("Error multiple labels!:", labels)
elif len(labels) == 0: print('Error no label')
else: print(labels[0])
