import BidTing as bt
import datam as dm
import time
import os
import system_access as sa

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


n = len(projects_info[0])

for i in range(n):
    project_list = bt.get_project_biddinginformation(projects_info[0][i],
                                      client_name,
                                      projects_info[1][i])

    print(project_list)


end = time.time()
print('Run time is', end - start)

print(projects_info[0])
print(len(projects_info[0]))