import requests
from bs4 import BeautifulSoup
import re
import mysql.connector
from urllib.parse import urljoin

from findLinks import getLinks, filterLinks

import sys
sys.path.append('/home/ximena/auth')
import authJS

mydb = mysql.connector.connect(host=authJS.HOSTNAME, user=authJS.USERNAME, password=authJS.PASSWORD)
mycursor = mydb.cursor()
db_statement = "use {}".format(authJS.DATABASE)
mycursor.execute(db_statement)


headers = {'User-agent': 'Mozilla/5.0'}

def main():
    page_url = input('insert page url: ').strip()

    res = requests.get(str(page_url), headers=headers, timeout=5)
    soup = BeautifulSoup(str(res.text), features="html.parser", multi_valued_attributes=None)
    if soup.body: soup = soup.body
    unfiltered_links = getLinks(soup)[1]
    links = filterLinks(unfiltered_links, page_url)[0]


    #print('links:', links)

    #res = requests.get(str(page_url), headers=headers, timeout=5)
    #soup = BeautifulSoup(str(res.text), features="html.parser", multi_valued_attributes=None)

    labels = findLabels(soup, links)
    print('\nlinks')
    for x in links: print(x)
    print('\nlabels')
    for x in labels: print(x)
    print('')


def findLabels(soup, links):
    #find the names of links
    all_labels = []

    def hTag_r(item):
        #print('hTag_r is being called for', item)
        tag = item.find(re.compile('h\d'))
        if tag:
            label = tag.string.strip()
            if checkBadLabel(item, label):
                return label
        try:
            return hTag_r(item.parent)
        except:
            return None

    for link in links:
        labels = []
        divs = soup.find_all('a', {'href' : link})
        #if len(divs) != 1: print('# occurances for {}: {}'.format(link, len(divs)))
        for div in divs:
            if div.string:
                label = div.string
                if checkBadLabel(div, label):
                    labels.append(label)

        if not labels:
            for div in divs:
                label = hTag_r(div)
                labels.append(label)

        labels = [i for i in labels if i]
        labels = list(dict.fromkeys(labels))# remove duplicates
        if len(labels) == 1:
            all_labels.append(labels[0])
        else:
            if len(labels) > 1: print("multiple labels for {}:".format(link), labels)
            else: print('no label for {}'.format(link))
            all_labels.append('')

    return all_labels


def checkBadLabel(item, label): #returns False if the label has a bad match
    bad_labels = compileLists('label')
    for bad in bad_labels:
        #print('re.match statement', r''+bad, label)
        if re.match(r''+bad, label): ##This is throwing a lot of warnings and I don't know why
            #print(label, 'was a bad match')
            return False
    if item.has_attr("class"):
        cls_names = compileLists('class-label')
        for bad in cls_names:
            if re.match(r''+bad, label):
                print(label, 'had a bad class name:', div['class'])
                return False
    return True

def compileLists(des): #returns a list of regex statements
    if des == 'class-soup': tid = 1
    elif des == 'label': tid = 2
    elif des == 'class-label': tid = 3
    sql = 'select tag, diffregex from soup_tags where tid={}'.format(tid)
    main_cursor.execute(sql)
    data = main_cursor.fetchall()
    return [x[0] if x[1]==1 else '(?i)(^|^.*\W+){}($|\W+.*$)'.format(x[0]) for x in data]

main()


