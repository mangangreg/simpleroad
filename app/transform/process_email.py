import email

import dotenv
from bs4 import BeautifulSoup
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def process_email(email_data, email_id=None):
    '''
    Process a single email

    Inputs:
        - email_data (tuple): returned by iIMAP4.fetch
    Outputs:
        (dict)
    '''

    email_extracted = {'email_id':email_id}

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