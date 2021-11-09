import mysql.connector
import requests

headers = {'User-agent': 'Mozilla/5.0'}

main_db = mysql.connector.connect(host="gb.csle6sy7qkr1.us-east-1.rds.amazonaws.com", user="ximena", password="Horse4horse")
main_cursor = main_db.cursor()
db_statement = "use partners"
main_cursor.execute(db_statement)


sql = "SELECT title, url FROM jobtemp  WHERE DATE(modifydate) != CURDATE()"
main_cursor.execute(sql)
old_jobs= main_cursor.fetchall()

def testLinks(jobs):
    bad_jobs = []
    for job in jobs:
        link = job[1]
        r = requests.get(link, headers=headers, timeout=5)
        if not r: bad_jobs.append(job)
    return bad_jobs

def testNoRedirects(jobs):
    bad_jobs = []
    for job in jobs:
        link = job[1]
        r = requests.get(link, headers=headers, timeout=5, allow_redirects=False)
        if not r: bad_jobs.append(job)
    return bad_jobs
    
print('Unupdated Links:')
for x, y in old_jobs: print(y)

broken_links = testLinks(old_jobs)
print('\nBroken Links:')
for x, y in broken_links: print(x,": ",y)
old_links = [item for item in old_jobs if item not in broken_links]

redirect_links = testNoRedirects(old_jobs)
print('\nThese links redirected:')
for x, y in redirect_links: print(x,": ",y)
old_links = list(set(old_jobs) - set(redirect_links))

print('\nMaybe ok:')
for x, y in old_links: print(y)


