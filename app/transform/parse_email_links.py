import sys

import pymongo
from bs4 import BeautifulSoup

sys.path.append('..')
from mongo_connect import MongoConnect

email_link_color='#0f77db'

def get_links_from_email_soup(soup):
    links = []
    for link in (soup.select('a')):
        if email_link_color in link.attrs.get('style',''):
            links.append({
                'url': link.attrs['href'].strip(),
                'listing_name': link.text.strip(),
            })
    return links

if __name__ == '__main__':
    print('Starting parse_email_links')

    MC = MongoConnect()
    MC.connect()
    db = MC.db

    # Find cases that haven't had links extracted yet
    res = db.emails.find({'links_extracted': False})

    counts = {'emails_parsed':0, 'links_extracted':0}

    for email in res:

        print(f"Parsing from email: {email['unique_mail_id']}")
        counts['emails_parsed'] += 1

        soup = BeautifulSoup(email['body'], 'html.parser')
        links = get_links_from_email_soup(soup)

        operations = [
            pymongo.UpdateOne(
                {'url': link['url']},
                {'$set': link},
                upsert = True
            )
            for link in links
        ]

        counts['links_extracted'] += len(links)

        db.listing_urls.bulk_write(operations)

        # Mark email as having links extracted now
        db.emails.update_one({'_id':email['_id']}, {'$set': {'links_extracted':True}})

    if counts['email_parsed'] ==0:
        print("No emails to proces")

    print(f"Finished parse_email_links, {counts}")