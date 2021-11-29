# Import Module
from bs4 import BeautifulSoup
import requests
import mysql.connector
from urllib.parse import urljoin
from findLinks import getLinks, filterLinks

headers = {'User-agent': 'Mozilla/5.0'}

main_db = mysql.connector.connect(host="gb.csle6sy7qkr1.us-east-1.rds.amazonaws.com", user="ximena", password="Horse4horse")
main_cursor = main_db.cursor()

db_statement = "use partners"
main_cursor.execute(db_statement)
sql = 'select joburl, pid from profiles where jobactive=1'

main_cursor.execute(sql)
data = main_cursor.fetchall()
for partner in data:
    job_url = partner[0]
    pid = partner[1]
    print("\nJob url:", job_url)
    res = requests.get(str(job_url), headers=headers, timeout=5)
    #if res: print('requests is working')
    soup = BeautifulSoup(str(res.text), features="html.parser", multi_valued_attributes=None)
    #if soup: print('soup is working')

    # Find select tag
    select_tag = soup.find("select")
    print("select tag:\n", select_tag)
    if select_tag:
        # find all option tag inside select tag
        options = select_tag.find_all("option")
        if options:
            # Iterate through all option tags and get inside text
            print("Options:")
            for option in options: print(option.text.strip())




   
