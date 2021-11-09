import re
import requests
from bs4 import BeautifulSoup
from collections import Counter

#from findLinks import getLinks, filterLinks
from findJobs import getLinks, filterLinks

headers = {'User-agent': 'Mozilla/5.0'}


def main():
    page_url = input('insert page url: ').strip()

    res = requests.get(str(page_url), headers=headers, timeout=5)
    soup = BeautifulSoup(str(res.text), features="html.parser", multi_valued_attributes=None)
    if soup.body: soup = soup.body
    unfiltered_links = getLinks(soup)[1]
    links = filterLinks(unfiltered_links, page_url)[0]
    print('Links:')
    print(links)
    #lengths = []
    link_lengths = {}
    structure = []
    for link in links:
        #print('\nLink:', link)
        tree = parent(soup, link)
        tree.reverse()
        #lengths.append(len(tree))
        link_lengths[link] = len(tree)
        tree_size = parent2(soup, link)
        print("parent1: {} {}".format(link_lengths[link], link))
        print("parent2: {} {}".format(tree_size, link))
        #print(type(tree))
        #for item in tree: print(item)
        structure.append(tree)

    print(link_lengths)
    #for x in link_lengths: print(x)
    #print('lengths:', link_lengths)

    
    freq_len = Counter(link_lengths.values()).most_common()
    print("lengths and frequency:", freq_len)
    if len(freq_len) == 1:
        print("there are no outliers")
    elif len(freq_len) > 2 or freq_len[1][1] > 1:
        print("there are multiple outliers, do nothing")
    else:
        outlier_len = freq_len[1][0];

        index = list(link_lengths.values()).index(outlier_len)
        outlier_link = list(link_lengths.keys())[index]
        #outlier_link = link_lengths.index(outlier_len)
        print("outlier: {}".format(outlier_link))
    #elif len(freq_len) = 2 and :

        



    #if freq_len[0][1] == len(link_lengths.values()): print("there are no links that are outliers in structure")
    #elif freq_len[0][1] == (len(link_lengths.values()) - 1):
    #    print('there is 1 outlier')
    #elif freq_len[0][1] > (len(link_lengths.values()) - 1):
    #    print("there is more that 1 outliner - do nothing")
    #else: print('something is weird with the structure')

    #print("frequencies::", freq_len[0][1], freq_len[1][1])





    compare_structure = []
    for item_num in range(max(link_lengths.values())):
        level = []
        for tree in structure:
            try: level.append(tree[item_num])
            except: level.append({})
        compare_structure.append(level)
    
    ##this prints the structure for each level
    #for level in compare_structure:
    #    for item in level: print(item) #prints all the div info for each link
    #    print('')

def parent2(soup, link):
    tree_size = 1
    div = soup.find('a', {'href' : link})
    while div.parent:
        tree_size += 1
        div = div.parent
    #print("{}:{}".format(tree_size, link))
    return tree_size





def parent(soup, link):
#returns a list of dictionaries about elements in the parent structure of a single link
    parent_tree = []

    def parent_r(div):
    #edit this so it is th div itself and the attributes 
        tag = {} 
        tag['name'] = div.name
        for x, y in div.attrs.items(): tag[x] = y
        #tag['div_content'] = div 
        parent_tree.append(tag)
        #print(len(parent_tree))
        #print(parent_tree)
        if div.parent:
            return parent_r(div.parent)
        else: return
        
    div = soup.find('a', {'href' : link})
    parent_r(div)
    return parent_tree


if __name__ == '__main__':
    main()
