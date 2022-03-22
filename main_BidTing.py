import lib_BidTing as bt
import lib_datam as dm
import time


def get_inputs():
    webdriver = input('Enter preferred webdriver: ')
    url = input('Enter url: ')
    client_name = input('Enter client name: ')
    print('BidTing is now running...\n')
    return webdriver, url, client_name


def get_projectsweb(webdriver, url, client_name):
    # Receive initial url
    path = bt.get_path_webdriver(webdriver)
    driver = bt.get_driver(path, headless=False)
    driver.get(url)

    # Receive page numbers need to be scraped
    print('BidTing is identifying page number ...\n')
    bt.click_button_awarded(driver)
    bt.click_button_page100(driver)
    page_number = bt.get_driverpagenumber(driver)

    # forcesleep
    time.sleep(10)
    page_start = 0

    # split out a tuple: ((list_projectname, list_projectweb, list_clientname))
    projects_info = bt.get_projects(url, driver, page_number, page_start, client_name)
    print('BidTing had collected all project url...\n')

    return projects_info


def get_projects(projects_info, client_name):
    # initiate list
    list_projects = dm.init_list_projects()
    list_projectsubmitters = dm.init_list_projectsubmitters()

    print('BidTing is extracting all projects information...\n')
    bt.cocurrent_webscraping(list_projects, list_projectsubmitters, 100, projects_info)

    # export data to excel

    print('BidTing is exporting data to csv file...\n')

    bt.get_csv(list_projectsubmitters, '{}result_submitter.csv'.format(client_name))


def main():
    webdriver, url, client_name = get_inputs()
    projects_info = get_projectsweb(webdriver, url, client_name)
    get_projects(projects_info, client_name)


if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print('The scrapping tool completed its processing!\n')
    print('Run time is', round((end - start) / 60, 2), 'mins.')
