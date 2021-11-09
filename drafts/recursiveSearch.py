import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

"""This script finds all the href and scr links recursively from a page"""



headers = {'User-agent': 'Mozilla/5.0'}

job_url = input("enter job url:")
job_url = str(job_url)


res = requests.get(job_url, headers=headers, timeout=5)
b_soup = BeautifulSoup(str(res.text), features="html.parser", multi_valued_attributes=None)

def find_Href(soup):
    links = []
    for a in soup.find_all(href=True): links.append(urljoin(job_url, a['href']))
    links = list(dict.fromkeys(links))# remove duplicates
    return links

def find_Src(soup):
    links = []
    for a in soup.find_all(src=True): links.append(urljoin(job_url, a['src']))
    links = list(dict.fromkeys(links))# remove duplicates
    return links

href_links = find_Href(b_soup)
src_links = find_Src(b_soup)

def rmRepeats(base_links, new_links):
    links = []
    for l in new_links:
        if l not in base_links:
            links.append(l)
    return links

def findEmbedded(link):
    r = requests.get(link, headers=headers, timeout=5)
    if not r:
        return [], []
    else:
        e_soup = BeautifulSoup(str(r.text), features="html.parser", multi_valued_attributes=None)
        h_links = find_Href(e_soup)
        h_links = rmRepeats(href_links, h_links)
        s_links = find_Src(e_soup)
        s_links = rmRepeats(src_links, s_links)
        #print('type h_links', type(h_links))
        #print('type s_links'+type(s_links))
        #print('type all_links'+type(all_links))
        all_links = [h_links, s_links]
        return all_links

def goThrough(links):
    for link in links:
        print('\n'+link)
        all_links = findEmbedded(link)
        h_links = all_links[0]
        s_links = all_links[1]
        if h_links:
            print('embeded href links:')
            for l in h_links: print(l)
        if s_links:
            print('embeded src links:')
            for l in s_links: print(l)


print('\n\n\nHref Links:')
goThrough(href_links)

print('\n\n\nSrc Links:')
goThrough(src_links)



