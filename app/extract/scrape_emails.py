import os
import sys
import email
import imaplib
import requests
from urllib import parse
from hashlib import md5

import dotenv
from bs4 import BeautifulSoup
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

sys.path.append('..')
from mongo_connect import MongoConnect

# Imap email search query
dotenv.load_dotenv('../.email.env')

def login_email(env_file='.email.env'):
    ''' Logs in and selects inbox '''
    mail = imaplib.IMAP4_SSL(os.environ['SMTP_SERVER'])
    res = mail.login(os.environ['EMAIL_ADDRESS'],os.environ['EMAIL_PASSWORD'])
    if res[0] != 'OK':
        raise ValueError('Unable to log in to SMTP server')
    mail.select('inbox')
    return mail

def fetch_ids(query, mail):
    '''
    Search a mail object and return matching email ids

    Inputs:
        - query (str): an IMAP email query
        - mail (imaplib.IMAP4_SSL)
    Output:
        (list) list of email ids
    '''

    data = mail.search(None, query)
    mail_ids = data[1]
    id_list = [int(x) for x in mail_ids[0].split()]
    return id_list

def fetch_mail_by_id(mail_id, mail):
    '''
    Fetch a single email, by email id

    Inputs:
        - mail_id (int): id of the email
        - mail (imaplib.IMAP4_SSL)
    Output
        - (tuple) see IMAP4.fetch
    '''
    return mail.fetch(str(mail_id), '(RFC822)' )

def process_email(email_data, unique_mail_id=None):
    '''
    Process a single email

    Inputs:
        - unique_mail_id (tuple): returned by iIMAP4.fetch
    Outputs:
        (dict)
    '''
    email_extracted = {'unique_mail_id':unique_mail_id}

    for response_part in email_data:
        arr = response_part[0]
        if isinstance(arr, tuple):
            msg = email.message_from_string(str(arr[1],'utf-8'))
            email_extracted['subject'] = msg['subject']
            email_extracted['from'] = msg['from']
            email_extracted['timestamp'] = msg['Date']

            payloads = msg.get_payload()
            # Always use the last one?
            email_extracted['body'] = payloads[-1].get_payload(decode=True)

    return email_extracted

if __name__ == '__main__':
    mail = login_email()
    query = os.environ.get('EMAIL_QUERY')

    ids = fetch_ids(query, mail)

    print(f"Found {len(ids)} emails that match query")

    # Get full list of ids on server

    MC = MongoConnect()
    MC.connect()
    db = MC.db

    res = db.emails.find({},{'unique_mail_id':1})
    seen_ids = [x['unique_mail_id'] for x in res]

    counts = {'inserted':0, 'skipped': 0}

    for mail_id in ids:
        unique_mail_id = f"{os.environ['EMAIL_ADDRESS']}_{mail_id}"

        if unique_mail_id not in res:

            email_data = fetch_mail_by_id(mail_id, mail)
            processed = process_email(email_data, unique_mail_id)

            processed['links_extracted'] = False

            print(f"Inserting {unique_mail_id}...")

            ins = db.emails.update_one(
                {'unique_mail_id':unique_mail_id},
                {
                    '$set': processed,
                    '$currentDate': {'_insertedAt':{'$type':'date'}}
                },
                upsert=True
            )

            counts['inserted'] += 1

        else:
            counts['inserted'] += 1

    print(f"Finished scrape_emails.py, {counts}")



