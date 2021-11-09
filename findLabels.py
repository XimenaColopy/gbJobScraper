import requests
from bs4 import BeautifulSoup
import re
import mysql.connector
from urllib.parse import urljoin

from findLinks import getLinks, filterLinks

headers = {'User-agent': 'Mozilla/5.0'}

other_db = mysql.connector.connect(host="localhost", user="ximena", password="Horse4horse")
other_cursor = other_db.cursor()
db_statement = "use Bad_job_info"
other_cursor.execute(db_statement)


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


def findLabels(soup, links):
    #find the names of links
    all_labels = []

    def hTag_r(item):
        #print('hTag_r is being called for', item)
        tag = item.find(re.compile('h\d'))
        if tag:
            label = tag.string.strip()
            if checkIfBad(item, label):
                return label
        try:
            return hTag_r(item.parent)
        except:
            return None

    for link in links:
        labels = []
        divs = soup.find_all('a', {'href' : link})
        #print('# occurances:', len(divs))
        if len(divs) != 1: print('# occurances for {}: {}'.format(link, len(divs)))
        for div in divs:
            if div.string:
                label = div.string
                if checkIfBad(div, label):
                    labels.append(label)
        
        if not labels:
            for div in divs:
                label = hTag_r(div)
                labels.append(label)
            
        labels = [i for i in labels if i]
        labels = list(dict.fromkeys(labels))# remove duplicates
        if len(labels) == 1:
            all_labels.append(labels[0].strip())
        else:
            if len(labels) > 1: print("Error multiple labels:", labels)
            else: print('No label')
            all_labels.append('')

    return all_labels

main()


