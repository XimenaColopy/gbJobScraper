import requests
from bs4 import BeautifulSoup
import re
import mysql.connector
from urllib.parse import urljoin


headers = {'User-agent': 'Mozilla/5.0'}
#headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
main_db = mysql.connector.connect(host="gb.csle6sy7qkr1.us-east-1.rds.amazonaws.com", user="ximena", password="Horse4horse")
main_cursor = main_db.cursor()

def main():

    job_url = input("enter job url:")
    print("\nJob url:", job_url)
    res = requests.get(str(job_url), headers=headers, timeout=5)
    if res: print('requests is working')
    soup = BeautifulSoup(str(res.text), features="html.parser", multi_valued_attributes=None)
    if soup: print('soup is working')

    if soup.body: soup = soup.body

    org_links = orgLinks(soup)
    print('\nOriginal Links:')
    for x in org_links: print(x)

    __x__ = getLinks(soup)
    soup = __x__[0]
    unfiltered_links = __x__[1]
    #divs = __x__[2]

    #if len(unfiltered_links) == len(divs): print('yes')
    print('\nUnfiltered links:')
    for x in unfiltered_links: print(x)
    print('')

    #print(divs)

    all_links = filterLinks(unfiltered_links, job_url)
    links = all_links[0]
    completed_links = all_links[1]
    bad_links = all_links[2]

    print('\nfiltered links:')
    for x in links: 
        print(x)

def orgLinks(soup):
    links = []
    #blacklist = [
    #    'noscript',
    #    'header',
    #    'meta',
    #    'head',
    #    'script',
    #    'nav',
    #    'footer'
    #]
    #for s in soup(blacklist): s.decompose()

    for a in soup.find_all('a', href=True):
        links.append(a['href'])

    links = list(dict.fromkeys(links))# remove duplicate links 

    return links

###########----- LINKS-----###############

def getLinks(soup):
    db_statement = "use ximena"
    main_cursor.execute(db_statement)
    links = []
    blacklist = [
        'noscript',
        'header',
        'meta',
        'head',
        'script',
        'nav',
        'footer'
    ]
    for s in soup(blacklist): s.decompose()

    #cls_name = [
    #    'logo',
    #    'hidden_elements',
    #    re.compile('(^|^.*\W+)image(s?)($|\W+.*$)'),
    #    re.compile('(^|^.*\W+)footer(s?)($|\W+.*$)'),
    #    re.compile('(^|^.*\W+)header(s?)($|\W+.*$)'),
    #    re.compile('(^|^.*\W+)cookies($|\W+.*$)')
    #]
    cls_name = compileLists('class-soup')
    cls_name = [re.compile(x) for x in cls_name]
    #for s in cls_name: s = re.compile



    for ele in soup.find_all(id = cls_name): ele.decompose()
    for ele in soup.find_all(class_ = cls_name): ele.decompose()

    for ele in soup.find_all(attrs={"ng-show" : re.compile('^.*$')}): ele.decompose()
    for ele in soup.find_all(attrs={"onclick" : re.compile('^(\W?)(\w+)\(.*\)(;?)$')}): ele.decompose() #function format name(var1, var2, ...)
    for ele in soup.find_all(style='display: none'): ele.decompose()

    for a in soup.find_all('a', href=True):
        links.append(a['href'])

    links = list(dict.fromkeys(links))# remove duplicate links 
    return soup, links


def filterLinks(links, target_url):
    #make sure the links actually go to another page.
    bad_links = []
    for link in links[:]:
        if '/' not in link:
            links.remove(link)
        elif link == target_url.split('#')[0]:
            links.remove(link)
        elif link in target_url:
            links.remove(link)

    #make sure the links are wanted 
    db_statement = "use ximena"
    main_cursor.execute(db_statement)
    for link in links[:]:
        sql = "SELECT keyword FROM urls WHERE %s LIKE CONCAT('%',keyword,'%')"
        args = (link, )
        main_cursor.execute(sql, args)
        if main_cursor.fetchone() != None:
            links.remove(link)
            bad_links.append(link)

    completed_links = []
    #make sure links are valid
    for link in links[:]:
        #complete the link if not already completed
        org_link = link
        link_split = link.split('/')
        if link_split[0] == 'http:':
            link_split[0] = 'https:'
            full_link = '/'.join(link_split)
        elif link_split[0] != 'https:':
            full_link = urljoin(target_url, link)
        else:
            full_link = link

        #make sure links are valid
        r = requests.get(full_link, headers=headers, timeout=5)
        if not r: links.remove(link)
        else:
            completed_links.append(full_link)
            link_soup = BeautifulSoup(str(r.text), features="html.parser")
            target = link_soup.find('html')
            if target.has_attr('lang'):
                if re.match(r'^\w*$', target['lang']) and re.match(r'^(?!en).*$', target['lang']):
                    links.remove(link)
                    completed_links.remove(full_link)
                    bad_links.append(link)

    if len(completed_links) != len(links):
        print('\nFunction "filterLinks" is not working\n') #This will cause adn error later with len(labels) != len(links)
    return links, completed_links, bad_links

def compileLists(des): #returns a list of regex statements 
    db_statement = "use ximena"
    main_cursor.execute(db_statement)
    if des == 'class-soup': tid = 1
    elif des == 'label': tid = 2
    elif des == 'class-label': tid = 3
    sql = 'select tag, diffregex from soup_tags where tid={}'.format(tid)
    main_cursor.execute(sql)
    data = main_cursor.fetchall()
    return [x[0] if x[1]==1 else '(?i)(^|^.*\W+){}($|\W+.*$)'.format(x[0]) for x in data]

if __name__ == '__main__':
    main()
