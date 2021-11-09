import requests
from bs4 import BeautifulSoup
import re



url = 'https://www.processmaker.com/about/careers/'
url = 'https://www.seguno.com/careers#jobs'
#url = 'https://www.feedtrail.com/open-positions/'

headers = {
    'User-agent': 'Mozilla/5.0'
}


r = requests.get(str(url), headers=headers, timeout=5)
soup = BeautifulSoup(str(r.text), features="html.parser", multi_valued_attributes=None)

links = []
for a in soup.find_all('a', href=True):
    links.append(a['href'])
#print('\nunfiltered links:')
#for x in links: print(x)

links2 = []
blacklist = [
    'noscript',
    'header',
    'meta',
    'head',
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
    #re.compile('^(\W?)height(\W?):(\W?)0px(\W?)$'), #this is accordian
    re.compile('^(\W?)display(\W?):(\W?)name(\W?)$')
]

for ele in soup.find_all(style=style_name):
    ele.decompose()

searched_cls = [
    
]



###This does a good jobs of getting labels from feed trail
searched_words = [
    re.compile('^.*(?i)(\s)(job)(\s).*$'),
    re.compile('^.*(?i)(\s)(work)(\s)(in|with|on)(\s).*$')
    #re.compile('^.*(?i)(to apply).*$')
    #re.compile('^.*(?i)(\s)position(\s).*$')
]

results = soup.find_all(string=searched_words, recursive=True)
print("# search word matches", len(results))

tags = []
for item in results:
    print('\nItem:', item)
    divs = item.find_parents("div")
    for div in divs:
        print('Div:', div.attrs)
        tag = div.find_all(re.compile('h\d'))
        #for i, s in enumerate(tag): tag[i] = s.string.strip()
        tag = [i for i in tag if i] #remove empty strings
        #for t in tag:
            #t = t.string.strip()
        if len(tag) > 0:
            print('Tag:', tag)
            tags.extend(tag)
            break
        else:
            continue

        
tags = list(dict.fromkeys(tags)) #get rid of duplicates
#print('tags:', tags)
#print(type(tags[2]))



#for tag in tags:
    #print('')
    #print(tag.attrs)
    #tag = tag.string.strip()
    #print(tag)









