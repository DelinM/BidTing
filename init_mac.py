import BidTing as bt
import datam as dm

import time
import os
import system_access as sa
import concurrent.futures
from xlsxwriter import Workbook

start = time.time()

webdriver = 'chrome'
url = 'https://haltonregion.bidsandtenders.ca/'
client_name = 'Halton Region'

print('client_name')
''' Computer Program '''

# Receive initial url
path = bt.get_path_webdriver(webdriver)
driver = bt.get_driver(path, headless=False)
driver.get(url)

# Receive page numbers need to be scraped
bt.click_button_awarded(driver)
bt.click_button_page100(driver)
page_number = bt.get_driverpagenumber(driver)

# forcesleep
time.sleep(10)
page_start = 0

# split out a tuple: ((list_projectname, list_projectweb, list_clientname))
projects_info = bt.get_projects(url, driver, page_number, page_start, client_name)

# initiate list
list_projects = dm.init_list_projects()
list_projectsubmitters = dm.init_list_projectsubmitters()

bt.cocurrent_webscraping(list_projects, list_projectsubmitters, 100, projects_info)

# export data to excel
bt.get_csv(list_projectsubmitters, '{}result_submitter.csv'.format(client_name))

end = time.time()

print('\n')
print('Run time is', round((end - start)/60,2), 'mins')
