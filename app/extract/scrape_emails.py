import os
import re
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
dotenv.load_dotenv('.email.env')

def login_email(env_file='.email.env'):
    ''' Logs in and selects inbox '''
    mail = imaplib.IMAP4_SSL(os.environ['SMTP_SERVER'])
    res = mail.login(os.environ['EMAIL_ADDRESS'],os.environ['EMAIL_PASSWORD'])
    mail.select('inbox')
    print(res)
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

if __name__ == '__main__':
    mail = login_email()
    query = os.environ.get('EMAIL_QUERY')
    ids = fetch_ids(query, mail)

    # Get full list of ids on server

    MC = MongoConnect()
    MC.connect()
    db = MC['landing']

    res = set(db.emails.query({},{'mail_id':1}))



