import re
import requests
from bs4 import BeautifulSoup
import mysql.connector

headers = {'User-agent': 'Mozilla/5.0'}

main_db = mysql.connector.connect(host="gb.csle6sy7qkr1.us-east-1.rds.amazonaws.com", user="ximena", password="Horse4horse")
main_cursor = main_db.cursor()
db_statement = "use partners"
main_cursor.execute(db_statement)

link = input('insert link: ').strip()

def findPageUrl(link):
    sql = 'select pid from jobtemp where url = %s'
    args = (link,)
    main_cursor.execute(sql, args)
    pid = main_cursor.fetchall()[0][0]
    print('pid', pid)
    sql = 'select joburl from partner where pid = {}'.format(pid)
    main_cursor.execute(sql)
    page_url = main_cursor.fetchall()[0][0]
    print('page_url', page_url)
    return page_url


page_url = findPageUrl(link)
res = requests.get(str(page_url), headers=headers, timeout=5)
soup = BeautifulSoup(str(res.text), features="html.parser", multi_valued_attributes=None)


blacklist = [
    'noscript',
    'header',
    'meta',
    'head',
    'script',
    'nav',
    'footer'
]
#for s in soup(blacklist): s.decompose()
#if soup.body: soup = soup.body


#for ele in soup.find_all(attrs={"ng-show" : re.compile('^.*$')}): ele.decompose()

#for ele in soup.find_all(attrs={"onclick" : re.compile('^(\W?)(\w+)\(.*\)(;?)$')}): ele.decompose() #function format name(var1, var2, ...)

#for ele in soup.find_all(style=re.compile('^\W?display\W+none\W?$')): ele.decompose()
parent_tree = []

    


def parent_r(div):
    tag = {}
    tag['name'] = div.name
    for x, y in div.attrs.items(): tag[x] = y
    parent_tree.append(tag)
    #print(len(parent_tree))
    #print(parent_tree)
    print(tag)
    if div.parent:
        return parent_r(div.parent)
    else: return 


print('\nhere is the link:', link)


#if the text is in the same div
div = soup.find('a', {'href' : link})
print('div', div)
print(type(div))

parent_r(div)
#print('Here is the tree:')
#for x in parent_tree: print(x)

