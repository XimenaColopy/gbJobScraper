import requests
from bs4 import BeautifulSoup
import re

page_url = input('Input link: ')

#https://matix.io/extract-text-from-webpage-using-beautifulsoup-and-python/

headers = {
    'User-agent': 'Mozilla/5.0'
}
r = requests.get(str(page_url), headers=headers, timeout=5)
html_page = r.content
soup = BeautifulSoup(str(r.text), features="html.parser", multi_valued_attributes=None)


#set([t.parent.name for t in text])

#print(type(text))

output = ''
blacklist = [
    #'[document]',
    'noscript',
    'header',
    #'html',
    'meta',
    'head',
    'input',
    'script',
    'nav', 
    'footer'
    # there may be more elements you don't want, such as "style", etc.
]

for s in soup(blacklist):
    s.decompose()


cls_name = [
    'logo',
    'hidden_elements',
    re.compile('^.*footer.*$'),
    re.compile('^.*header.*$'),
    re.compile('^.*cookies.*$')
]

for ele in soup.find_all("div", id = cls_name):
    ele.decompose()

for ele in soup.find_all("div", class_ = cls_name):
    ele.decompose()


style_name = [
    re.compile('^(\W?)height(\W?):(\W?)0px(\W?)$'), 
    re.compile('^(\W?)display(\W?):(\W?)name(\W?)$')
]

for ele in soup.find_all(style=style_name):
    ele.decompose()



#do something where if div.parent have to 'job' or 'position' in the text in it 


tag = soup.find_all(re.compile('h\d'))
for t in tag: 
    print('')
    print(type(t))
    label = t.string.strip()
    print(label)
    print(t.parent)









#print(soup.prettify())
#text = soup.find_all(text=True)
#for t in text:  print(t)
# t is <class 'bs4.element.NavigableString'>

#print(output)
#print(type(output))
