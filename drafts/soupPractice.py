import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

'''This script finds all of the href and scr links (non recursively) on a page'''

headers = {'User-agent': 'Mozilla/5.0'}

job_url = input("enter job url:")

res = requests.get(str(job_url), headers=headers, timeout=5)
soup = BeautifulSoup(str(res.text), features="html.parser", multi_valued_attributes=None)

href_links = []
for a in soup.find_all(href=True):
    link = urljoin(job_url, a['href'])
    href_links.append(link)

src_links = []
for a in soup.find_all(src=True):
    link = urljoin(job_url, a['src'])
    src_links.append(link)


href_links = list(dict.fromkeys(href_links))# remove duplicates
src_links = list(dict.fromkeys(src_links))# remove duplicates

"""
for x in href_links:
    print('\n\n')
    print(x['href'])
    print(x)
"""

"""
for x in src_links: 
    print('\n\n')
    print(x['src'])
    print(x)
   
"""

##print just the links
print('\n\nhref links:')
for x in href_links: print(x)

print('\n\nsrc links:')
for x in src_links: print(x)
