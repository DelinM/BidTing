import os.path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures
import time
from bs4 import BeautifulSoup as bs

import system_access as sa


def get_path_webdriver(driver):
    driver = driver.lower()

    path = sa.get_currentpath()
    if sa.get_Windows() and driver == 'chrome':
        chromedriver_name = 'chromedriver.exe'
        path = os.path.join(path, chromedriver_name)
        return path
    elif sa.get_Windows() and driver == 'firefox':
        firefoxdriver_name = 'geckodriver.exe'
        path = os.path.join(path, firefoxdriver_name)
        return path
    else:
        raise Exception('ERROR: The system is not windows.')


def get_driver(path):
    if 'chromedriver.exe' in path:

        from selenium.webdriver.chrome.service import Service
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--incognito')
        options.add_argument('--ignore_certificate-error')
        chr_service = Service(path)
        driver = webdriver.Chrome(service=chr_service, options=options)
        return driver

    elif 'geckodriver.exe' in path:

        from selenium.webdriver.firefox.service import Service

        firef_service = Service(path)
        driver = webdriver.Firefox(service=firef_service)
        return driver
    else:
        raise Exception('Error: Driver issue.')


def click_button_awarded(driver):
    from selenium.webdriver.support.ui import WebDriverWait
    try:
        button_bidtype = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.btn.btn-default.dropdown-toggle.input-lg'))
        )
        button_bidtype.click()
    finally:
        li = button_bidtype.parent.find_elements(by=By.TAG_NAME, value='li')
        time.sleep(3)
        li[5].click()

    time.sleep(5)

def click_button_page100(driver):
    from selenium.webdriver.support.ui import WebDriverWait
    try:
        button_limitresults = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.btn-group.selectlist.dropup'))
        )
        button_limitresults.click()
    finally:
        li_2 = button_limitresults.find_elements(by=By.TAG_NAME, value='li')
        li_2[3].click()

    time.sleep(10)

def get_driverpagenumber(driver):
    page_number = driver.find_element(by=By.CLASS_NAME, value='repeater-pages')
    print(page_number)
    page_number = int(page_number.text)
    return page_number


