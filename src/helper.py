import os
import json
import logging
from datetime import datetime, timedelta
from colorama import Fore, Back, Style
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# load settings.json file
def load_settings():
    # absolute path
    current_dir = os.path.dirname(__file__)
    # build settings.json path
    settings_path = os.path.join(current_dir, 'config', 'settings.json')
    # load file
    with open(settings_path, 'r') as f:
        settings = json.load(f)
    # return file content
    return settings

# selenium redirect to route
def route(driver, route):
    driver.get(route)

# retrieve config param from key (settings.json)
def config(key):
    if '.' in key:
        # return array of splitted keys
        elements = key.split('.')
        # load config file
        settings = load_settings()

        for element in elements:
            # create settings[element1][element2]...
            settings = settings.setdefault(element, {})

        return settings

    return None

# print custom using colorama lib
def print_c(message, color = 'green', colorama_ob = Fore):
    # if not string, cast
    if not isinstance(message, str): message = str(message)
    # build style att with color and colorama objects (Fore, Back...)
    style = getattr(colorama_ob, color.upper())
    # print and reset
    print(style + message + Style.RESET_ALL)

# removes spaces, strips the string and to lower
def normalize_string(s):
    if (not isinstance(s, str)):
        return ''

    return s.strip().lower().replace(' ', '')

# get current date
def get_current_date():
    return datetime.now().strftime("%Y%m%d%H%M%S")


# --------------------
# SELENIUM FUNCTIONS
# --------------------

def visibility_of_element_located(wait, type, target):
    wait.until(EC.visibility_of_element_located((getattr(By, type), target)))

def element_to_be_clickable(wait, type, target, click = False):
    element = wait.until(EC.element_to_be_clickable((getattr(By, type), target)))
    if click: element.click()

    return element

def find_element(driver, type, target):
    return driver.find_element(getattr(By, type), target)

def find_elements(driver, type, target):
    return driver.find_elements(getattr(By, type), target)

def execute_script(driver, script, element):
    driver.execute_script(script, element)

def find_book_match(match, key):
    for book in match['books']:
        if book['book'] == key:
            return book
    return None
