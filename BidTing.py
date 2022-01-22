import os.path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures
import time
from bs4 import BeautifulSoup as soup
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
        print('The system is not windows.')

p
