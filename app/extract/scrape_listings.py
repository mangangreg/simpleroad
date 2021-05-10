import os
import re
import requests
from urllib import parse
from hashlib import md5

import dotenv
from bs4 import BeautifulSoup
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def select(el, query, squeeze=True):
    lib = el.__module__.split('.', maxsplit=1)[0]
    if lib=='bs4':
        res = el.select(query)

    elif lib=='selenium':
        res = el.find_elements_by_css_selector(query)

    if squeeze and len(res)==1:
        return res[0]
    else:
        return res

def make_id(val):
    hash_obj = md5()
    hash_obj.update(val.encode())
    return hash_obj.hexdigest()[:10]

def to_float(num):
    return float(num.lstrip('$').replace(',', '').strip())

def get_attr(el, attribute):
    lib = el.__module__.split('.')[0]

    if lib=='bs4':
        val = el.attrs.get(attribute)
    elif lib=='selenium':
        val = el.get_attribute(attribute)
        if attribute == 'class':
            val = val.split()

    return val

def get_coords(browser):
    ''' Get the co-ordinates of a listing, using the query string from the call to google map api'''
    network = browser.execute_script("var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;")

    map_url = None
    for item in network:
        if 'staticmap?' in item['name']:
            map_url = item['name']
            break

    if map_url:
        parsed_url = parse.urlparse(map_url)
        parsed_query = parse.parse_qs(parsed_url.query)

        markers = parsed_query['markers']

        if markers:
            coords = markers[0].split('|')[-1]
            try:
                coords = [float(x) for x in coords.split(',')]
            except:
                pass
            return coords


def init_browser(headless=True, pageLoadStrategy='normal'):
    opts = Options()
    opts.headless = headless
    caps = DesiredCapabilities().FIREFOX
    caps["pageLoadStrategy"] = pageLoadStrategy

    browser = Firefox(options=opts)
    return browser

def get_listing(data):

    browser = init_browser(headless=data.get('headless', True), pageLoadStrategy='eager')

    browser.get(data['input_url'])

    data['browser'] = browser

    return data

def extract_from_browser(data):
    '''Extract data that needs to come from the browser'''

    data['url'] = data['browser'].current_url
    data['page_source'] = data['browser'].page_source

    try:
        coords = get_coords(data['browser'])
    except:
        coords = None

    data['coords'] = coords
    data['browser'].close()
    del data['browser']

    return data