import requests
from bs4 import BeautifulSoup
import re
import mysql.connector
from urllib.parse import urljoin


headers = {'User-agent': 'Mozilla/5.0'}

main_db = mysql.connector.connect(host="gb.csle6sy7qkr1.us-east-1.rds.amazonaws.com", user="ximena", password="Horse4horse")
main_cursor = main_db.cursor()
#db_statement = "use partners"
#main_cursor.execute(db_statement)

#other_db = mysql.connector.connect(host="localhost", user="ximena", password="Horse4horse")
#other_cursor = other_db.cursor()
#db_statement = "use Bad_job_info"
#other_cursor.execute(db_statement)

def main():
    db_statement = "use partners"
    main_cursor.execute(db_statement)
    #sql = 'select joburl, pid from profiles where jobactive=1'    
    job_url = "https://allobee-inc.breezy.hr/"
    sql = 'select joburl, pid from profiles where joburl="{}"'.format(job_url)
    main_cursor.execute(sql)
    data = main_cursor.fetchall()
    print('Data:',data)
    for partner in data:
        main_loop(partner)

def main_loop(partner):
    """Main for each partner"""
    job_url = partner[0]
    pid = partner[1]

    print('\nJob Url:', job_url)

    res = requests.get(str(job_url), headers=headers, timeout=5)
    if not res:
        print('\n\nERROR REQUESTS ISNT WORKING\n\n')
        return 
    #print('Res:', res)
    soup = BeautifulSoup(str(res.text), features="html.parser", multi_valued_attributes=None)
    if not soup:
        print('\n\nERROR SOUP ISNT WORKING\n\n')
        return 
    #if soup: print("Soup is working")
    if soup.body: soup = soup.body

    try:
        __x__ = getLinks(soup)
        soup = __x__[0]
        unfiltered_links = __x__[1]
        #print("getLinks is working")
    except:
        print('\n\nERROR getLinks ISNT WORKING\n\n')
        return

    try:
        all_links = filterLinks(unfiltered_links, job_url)
        links = all_links[0]
        completed_links = all_links[1]
        bad_links = all_links[2]
        #print('filterLinks is working')
        if bad_links: print('Bad links:', bad_links)
    except:
        print('\n\nERROR filterLinks ISNT WORKING\n\n')
        return

    try:
        labels = findLabels(soup, links)
    #print('findLabels is working')
    except:
        print('\n\nERROR findLabels ISNT WORKING\n\n')
        return

    if len(labels) != len(completed_links):
        #have something here that sends and email
        print('\n\nERROR THERE AREN\'T THE SAME NUMBER OF LINKS AND LABELS\n\n')
        return

    job_info = [(completed_links[i], labels[i]) for i in range(0, len(completed_links))]
    job_info = removeNoLabel(job_info)

    insertInfo(pid, job_info)

def removeNoLabel(job_info):
    for job in job_info[:]:
        if not job[1]:
            print('Error no label for {}'.format(job[0]))
            job_info.remove(job)
    return job_info

def insertInfo(pid, job_info):
    db_statement = "use partners"
    main_cursor.execute(db_statement)
    for item in job_info:
        link = str(item[0]).strip()
        label = str(item[1]).strip()

        sql = 'SELECT title FROM jobtemp WHERE url=%s'
        args = (link,)
        main_cursor.execute(sql, args)
        data = main_cursor.fetchone()

        if data: #update info
            current_label = data[0]
            if current_label != label: #update title
                #sql = 'UPDATE jobtemp SET title=%s WHERE title=%s'
                #args = (label, current_label)
                #print('incorrect label:', current_label, link)
                sql = 'UPDATE jobtemp SET title=%s WHERE url=%s'
                args = (label, link)
                main_cursor.execute(sql, args)
                main_db.commit()
                #sql = 'SELECT title FROM jobtemp WHERE url=%s'
                #args = (link,)
                #main_cursor.execute(sql, args)
                #data = main_cursor.fetchone()
                print('updated label {} was previously {}'.format(label, current_label))
            #update timestamp
            sql = 'UPDATE jobtemp SET modifydate=NOW() WHERE title=%s AND url=%s'
            args = (label, link)
            main_cursor.execute(sql, args)
            main_db.commit()
            print(label, link)
        
        else: #insert information
            sql = "insert into jobtemp(pid, title, url) values(%s, %s, %s)"
            args = (pid, label, link)
            main_cursor.execute(sql, args)
            main_db.commit()
            print('add new job:', label, link)

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

###########----- LABELS -----###############

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
    db_statement = "use ximena"
    main_cursor.execute(db_statement)
    sql = "select tid from tag_types where des='{}'".format(des)
    main_cursor.execute(sql)
    tid = main_cursor.fetchone()[0]
    #if des == 'class-soup': tid = 1
    #elif des == 'label': tid = 2
    #elif des == 'class-label': tid = 3
    sql = 'select tag, diffregex from soup_tags where tid={}'.format(tid)
    main_cursor.execute(sql)
    data = main_cursor.fetchall()
    return [x[0] if x[1]==1 else '(?i)(^|^.*\W+){}($|\W+.*$)'.format(x[0]) for x in data]



if __name__ == '__main__':
    main()

