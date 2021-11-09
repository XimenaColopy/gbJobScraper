import requests
from bs4 import BeautifulSoup
import re

headers = {'User-agent': 'Mozilla/5.0'}


page_url = input('insert page url: ').strip()
link = input('insert link: ').strip()

res = requests.get(str(page_url), headers=headers, timeout=5)
soup = BeautifulSoup(str(res.text), features="html.parser", multi_valued_attributes=None)
if soup.body: soup = soup.body

def checkIfMatch(item):
    div = item.find('a', {'href' : link})
    return div
    

blacklist = [
    'noscript',
    'header',
    'meta',
    'head',
    'script',
    'nav',
    'footer'
]


for s in soup(blacklist):
    div = checkIfMatch(s)
    if div:
        print('bad tag',s.name)
        print(div, '\n')
    s.decompose()

for ele in soup.find_all(attrs={"ng-show" : re.compile('^.*$')}):
    div = checkIfMatch(ele)
    if div:
        print('ng-show',ele.attrs)
        print(div, '\n')
    ele.decompose()

for ele in soup.find_all(attrs={"onclick" : re.compile('^(\W?)(\w+)\(.*\)(;?)$')}): #function format name(var1, var2, ...)
    div = checkIfMatch(ele)
    if div:
        print('probably a function:',ele['onclick'])
        print(div, '\n')
    ele.decompose()

for ele in soup.find_all(style='display: none'):
    div = checkIfMatch(ele)
    if div:
        print('bad style:',ele['style'])
        print(div, '\n')
    ele.decompose()


cls_name = [
    'logo',
    'hidden_elements',
    re.compile('(^|^.*\W+)image(s?)($|\W+.*$)'),
    re.compile('(^|^.*\W+)footer(s?)($|\W+.*$)'),
    re.compile('(^|^.*\W+)header(s?)($|\W+.*$)'),
    re.compile('(^|^.*\W+)cookies($|\W+.*$)'), 
    re.compile('(^|^.*\W+)hidden($|\W+.*$)')
]


for ele in soup.find_all(id = cls_name):
    div = checkIfMatch(ele)
    if div: 
        print('bad id:',ele['id'])
        print(div, '\n')
    ele.decompose()

for ele in soup.find_all(class_ = cls_name):
    div = checkIfMatch(ele)
    if div: 
        print('bad class name:',ele['class'])
        print(div, '\n')
    ele.decompose()

print('Is the link still in there?')
for a in soup.find_all('a', href=True):
    div = checkIfMatch(a)
    if div: 
        print(a)







