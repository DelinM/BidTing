import os.path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures
import time
from bs4 import BeautifulSoup as bs
import lxml
import pandas as pd

import lib_system_access as sa


def get_path_webdriver(driver):
    driver = driver.lower()

    path = sa.get_currentpath()

    if sa.get_Windows():
        if driver == 'chrome':
            chromedriver_name = 'chromedriver.exe'
            path = os.path.join(path, chromedriver_name)
            return path
        elif driver == 'firefox':
            firefoxdriver_name = 'geckodriver.exe'
            path = os.path.join(path, firefoxdriver_name)
            return path
    elif not sa.get_Windows():
        if driver == 'chrome':
            chromedriver_name = 'chromedriver'
            path = os.path.join(path, chromedriver_name)
            return path
        elif driver == 'firefox':
            firefoxdriver_name = 'geckodriver'
            path = os.path.join(path, firefoxdriver_name)
            return path
    else:
        raise Exception('Error: unable to get webdriver (path issue)')


def get_driver(path, headless):
    if 'chromedriver.exe' or 'chromedriver' in path:
        from selenium.webdriver.chrome.service import Service
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        # options.add_argument('--incognito')
        options.add_argument('--ignore_certificate-error')
        chr_service = Service(path)
        driver = webdriver.Chrome(service=chr_service, options=options)
        return driver

    elif 'geckodriver.exe' or 'geckodriver' in path:

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
        li[8].click()

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
    page_number = int(page_number.text)
    if page_number >= 0:
        print('BidTing identified {} to be scrapped.\n'.format(page_number))
        time.sleep(40)
        return page_number
    else:
        raise Exception('Error: Page number cannot be extracted (get_driverpagenumber)')



def click_button_nextpage(driver):
    button_next = driver.find_element(by=By.CSS_SELECTOR, value='.btn.btn-default.repeater-next')
    button_next.click()


def get_projects_basiccontainer(driver):
    from bs4 import BeautifulSoup as soup
    html = driver.page_source
    soup_projects = soup(html, 'lxml')
    project_container = soup_projects.find_all('tbody')[0]
    project_container_inner = project_container.find_all('div', {'style': 'float:right;'})
    return project_container_inner


def get_projects_basicinformation(basiccontainer, url, clientname, list_projectname, list_projectweb, list_clientname):
    for project in basiccontainer:
        project_name = project.span.contents[0]
        project_name = project_name.split('- ')[2].strip()

        # receive the url to get into the page
        project_website = url + project.a['href']
        list_projectname.append(project_name)
        list_projectweb.append(project_website)
        list_clientname.append(clientname)
        # print(project_website)


def get_projects(url, driver, page_number, page_start, client_name):
    list_projectname = []
    list_projectweb = []
    list_clientname = []

    for i in range(page_start, 2, 1):
        '''time buffer added, to be removed.'''
        time.sleep(10)

        '''below included if page_start is not 0, for future implementation'''
        if i == page_start and page_start != 0:
            time.sleep(10)

        project_container = get_projects_basiccontainer(driver)
        get_projects_basicinformation(project_container, url, client_name, list_projectname, list_projectweb,
                                      list_clientname)

        if i < page_number - 1:
            click_button_nextpage(driver)

    # driver.quit()

    return (list_projectname, list_projectweb, list_clientname)


def get_project_biddinginformation(project_name, client_name, url):
    '''
    start development: Feb 19th, 2021
    end development: Mar 20th, 2022

    Purpose: extract a AWARDED project information when a AWARDED project url is provided. The function will return
    a list of AWARDED project information.


    Patch 0.1 - Feb 25th, 221
    Some awarded project does not have award table or submitted project table, so codes to be modified so that
    if some projects do not have the table(s), the code will return empty

    Patch 0.2 - March 6th, 2021
    Changes to make to extract Bid Number. Bid Number is important as it will be act as an "ID" for each project to
    prevent duplications in future database.

    Patch 0.3 - March 6th, 2021
    Some projects do not have bid classification, code added to avoid if everything we look for are blank.
    Multiple bugs were fixed under this patch
    1. When opened page is an 'Error' page, the code can now identify and will return an empty list
    2. When awarded table is missing, the code can now identify and will return an empty winner list

    Patch 0.4 - Wining Price Extraction - March 14th, 2021
    Code modification to extract awarded company' cost.

    Patch 0.5 - Precision Extraction - March 14th, 2021
    Code modification to "precision" extract the information we need.
    1. Before information were extract based on the location, but now information will be extracted base on keywords.
    2. Before project name and project type were extract from Function "BidTenders_AwardProjects", which was not ideal
       as the name show in the main page is not accurate. Modification is made.

    Patch 0.6 - Bids Submitted Information Extraction - March 15th, 2021
    Codes added to extract Bids Submitted Information

    Patch 0.7 - Bid Cost Update - March 16th, 2021
    cCode patch to solve the following problems.
    1. Sometimes, the winners in the submitter table has a project cost, but the cost is not in the winner's table, and
    vice versa.
    2. list_submitter can supersede the list_project

    Patch 1.0 - Final Update for BidTing -  March 20th, 2021


    '''
    from bs4 import BeautifulSoup as soup

    # receive HTML using selenium chrome
    webdriver = 'chrome'
    path = get_path_webdriver(webdriver)
    driver = get_driver(path, headless=True)
    driver.get(url)
    time.sleep(0)
    html = driver.page_source
    # driver.close()

    soup_ob = soup(html, 'html.parser')

    # web checking:
    error = str(soup_ob.find_all('body')[0].contents[0])
    if 'error' in error:
        return [client_name, project_name, '', '', '', '', '', '', '', '', '', '']

    else:

        # code below are modified during Patch 0.5, project_information contains all necessary information
        project_information_list = soup_ob.find_all('div', {'id': 'pnlBidDetails_Container'})
        project_information = project_information_list[0]

        # receive bid classification - Patch 0.5 completed
        bid_classification = project_information.find_all('div', {'id': 'bidClass'})
        if len(bid_classification) == 0:
            output_bid_classification = ''
        else:
            output_bid_classification = bid_classification[0]
            output_bid_classification = output_bid_classification.contents[0]

        # for loop to extract bid type, bid ID, bid name, bid date, and bid year

        project_infobox = project_information.find_all('tr')

        # set initial value for all output values
        output_bid_type = ''
        output_bid_id = ''
        output_projectname = ''
        output_awarded_date = ''
        output_awarded_year = ''

        for p in range(len(project_infobox)):

            if len(project_infobox[p].contents) != 0:
                if 'Bid Type' in str(project_infobox[p].contents[1]):
                    output_bid_type = project_infobox[p].find_all('td')
                    output_bid_type = output_bid_type[0].contents[0].strip()

                elif 'Bid Number' in str(project_infobox[p].contents[1]):
                    output_bid_id = project_infobox[p].find_all('td')
                    output_bid_id = output_bid_id[0].contents[0].strip()

                elif 'Awarded Date' in str(project_infobox[p].contents[1]):
                    awarded_time = project_infobox[p].find_all('td')
                    awarded_time = awarded_time[0].contents[0].split()
                    output_awarded_date = awarded_time[1] + ' ' + awarded_time[2].rstrip(',')
                    output_awarded_year = awarded_time[3]

                elif output_awarded_date == '' and output_awarded_year == '' and 'Bid Closing Date' in str(
                        project_infobox[p].contents[0]):
                    awarded_time = project_infobox[p].find_all('td')
                    awarded_time = awarded_time[0].contents[0].split()
                    output_awarded_date = awarded_time[1] + ' ' + awarded_time[2].rstrip(',')
                    output_awarded_year = awarded_time[3]

        # receive awarded winners' name, they will be organzied in a string, and return how many winners
        # if there is one single winner, receive winner's price.

        awarded_company_table = soup_ob.find_all('div', {'id': 'dgAwarded_Container'})
        if len(awarded_company_table) == 0:
            output_no_winner = 0
            output_winnercompany_name = ''
            output_winnerprice = ''

        else:
            awarded_company_table = awarded_company_table[0]
            awarded_company_names = awarded_company_table.find_all('div',
                                                                   {
                                                                       'class': 'x-grid3-cell-inner x-grid3-col-CompanyName'})
            output_no_winner = 0
            output_winnercompany_name = ''
            for company_name in awarded_company_names:
                company_name = company_name.contents[0].strip()
                output_no_winner += 1
                output_winnercompany_name += company_name + ', '
                output_winnerprice = ''

            # statement in place in case the awarded company is not recorded.
            if output_winnercompany_name == '':
                output_no_winner = 0
                output_winnerprice = ''

            if output_no_winner == 1:
                output_winnerprice = awarded_company_table.find_all('div',
                                                                    {'class': 'x-grid3-cell-inner x-grid3-col-Value'})
                output_winnerprice = output_winnerprice[0].contents[0]

        # receive plan takers' names, they will be organized in a string, and return how many takers

        # Patch 0.6: add list to store submitter's information: [bid_id, bid_company, results]
        list_submitter = []
        output_winnerstatus = 0
        submitted_company_table = soup_ob.find_all('div', {'id': 'dgSubmitted_Container'})
        if len(submitted_company_table) == 0:
            output_no_submitted = 0
            output_submitted_name = ''
            list_submitter.append([client_name,
                                   project_name,
                                   output_bid_classification,
                                   output_bid_type,
                                   output_bid_id,
                                   output_awarded_date,
                                   output_awarded_year,
                                   '',
                                   '',
                                   ''])
        else:
            submitted_company_table = submitted_company_table[0]
            submitted_company_names = submitted_company_table.find_all('div', {
                'class': 'x-grid3-cell-inner x-grid3-col-CompanyName'})
            submitted_company_price = submitted_company_table.find_all('div', {
                'class': 'x-grid3-cell-inner x-grid3-col-VerifiedValue'})

            output_no_submitted = 0
            output_submitted_name = ''

            # patch: code modified to fix unstable price issue
            list_submitted_price = []
            for element in submitted_company_price:
                if len(element.contents) > 1:
                    sum = ''
                    for value in element:
                        sum += str(value)
                    if '<br/>' in sum:
                        sum = sum.replace('<br/>', '')
                    list_submitted_price.append(sum.strip())
                else:
                    list_submitted_price.append(element.contents[0].strip())

            for position, company_name in enumerate(submitted_company_names):

                # receive company name and company price
                company_name = company_name.contents[0].strip()
                company_price = list_submitted_price[position].strip()

                if company_price == '--':
                    company_price = ''

                # if the company is a winner, but the winner's price is not updated, then use the data in submitter
                # table to update, and vice versa (patch 0.7)
                list_awarded_company_names = output_winnercompany_name.split(', ')
                if len(list_awarded_company_names) == 1:
                    if list_awarded_company_names[0] == company_name:
                        output_winnerstatus = 1
                        if output_winnerprice == '--' or output_winnerprice == '':
                            output_winnerprice = company_price
                        elif company_price == '--' or company_price == '':
                            company_price = output_winnerprice
                if len(list_awarded_company_names) != 1:
                    if company_name in list_awarded_company_names:
                        output_winnerstatus = 1
                # Patch 0.6: write into submitter's list
                list_submitter.append([client_name,
                                       project_name,
                                       output_bid_classification.strip(),
                                       output_bid_type,
                                       output_bid_id,
                                       output_awarded_date,
                                       output_awarded_year,
                                       company_name,
                                       company_price,
                                       output_winnerstatus])
                output_winnerstatus = 0
                # write into project information spreadsheet
                output_no_submitted += 1
                output_submitted_name += company_name + ', '

            output_winnercompany_name = output_winnercompany_name.rstrip(', ')
            output_submitted_name = output_submitted_name.rstrip(', ')

        list_project = [client_name,
                        project_name,
                        output_bid_classification,
                        output_bid_type,
                        output_bid_id,
                        output_awarded_date,
                        output_awarded_year,
                        output_no_winner,
                        output_winnercompany_name,
                        output_winnerprice,
                        output_no_submitted,
                        output_submitted_name]

        project_list = [list_project, list_submitter]

        return project_list


def get_csv(list, filename):
    df = pd.DataFrame(list)
    df.to_csv(filename, index=False, header=False)


def cocurrent_webscraping(empty_projects, empty_projectsubmitters, jump, projects_info):
    list_projectname = projects_info[0]
    list_projectweb = projects_info[1]
    list_clientname = projects_info[2]

    list_projectname = [list_projectname[x:x + jump] for x in range(0, len(list_projectname), jump)]
    list_projectweb = [list_projectweb[x:x + jump] for x in range(0, len(list_projectweb), jump)]
    list_clientname = [list_clientname[x:x + jump] for x in range(0, len(list_clientname), jump)]

    for list_chunk_num in range(len(list_projectname)):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(get_project_biddinginformation, list_projectname[list_chunk_num],
                                   list_clientname[list_chunk_num], list_projectweb[list_chunk_num])

            # results is a list of [list_project, [list_submitter]]
            # position 0: list_project  position 1: list_submitter

            for result in results:

                # access and append list_project
                print(result[0])
                empty_projects.append(result[0])

                # access and append list_submitter
                for item in result[1]:
                    empty_projectsubmitters.append(item)
