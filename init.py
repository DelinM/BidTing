import BidTing as bt
import datam as dm
import time


start = time.time()
webdriver = 'firefox'
url = 'https://york.bidsandtenders.ca/Module/Tenders/en'

path = bt.get_path_webdriver(webdriver)
driver = bt.get_driver(path)
driver.get(url)
bt.click_button_awarded(driver)
bt.click_button_page100(driver)

list_projects = dm.init_list_projects()
list_submitters = dm.init_list_projectsubmitters()



end = time.time()
print('Run time is', end - start)