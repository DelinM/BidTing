import BidTing as bt
import datam as dm
import time


start = time.time()
webdriver = 'firefox'
url = 'https://haltonregion.bidsandtenders.ca/'
client_name = 'Halton Region'

print('client_name')
path = bt.get_path_webdriver(webdriver)
driver = bt.get_driver(path)
driver.get(url)
bt.click_button_awarded(driver)
bt.click_button_page100(driver)
page_number = bt.get_driverpagenumber(driver)

list_projects = dm.init_list_projects()
list_submitters = dm.init_list_projectsubmitters()

time.sleep(10)

page_start = 0

for i in range(page_start, page_number, 1):
    '''time buffer added, to be removed.'''
    time.sleep(10)

    '''below included if page_start is not 0, for future implementation'''
    if i == page_start and page_start != 0:
        time.sleep(10)

    list_projectname = []
    list_projectweb = []
    list_clientname = []

    project_container = bt.get_projects_basiccontainer(driver)
    bt.get_projects_basicinformation(project_container,url,client_name,list_projectname,list_projectweb, list_clientname)

    if i < page_number - 1:
        bt.click_button_nextpage(driver)
driver.quit()

end = time.time()
print('Run time is', end - start)