import smtplib, ssl
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.service import Service


import time
from bs4 import BeautifulSoup as soup
import lxml
import html5lib

import concurrent.futures
import pandas as pd


def emailsender(sender, sender_password, receiver, message):
    port = 465
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
        server.login(sender, sender_password)
        server.sendmail(sender, receiver, message)

def dy_pageextraction(url, sleeptime):
    """
    Extract HTML for dynamic website, aka JS

    Patch 0.1 March 7th 2021
    Patch changed to D drive because if the drive saved in C, it will fill up the storage space..
    """
    from selenium.webdriver.chrome.service import Service

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--incognito')
    options.add_argument('--ignore_certificate-error')
    e_path = Service('C:/Users/PC/PycharmProjects/pythonProject/venv/chromedriver')

    drive = webdriver.Chrome(service = e_path, options=options)
    drive.get(url)
    time.sleep(sleeptime)
    html = drive.page_source
    drive.close()
    return html

def BidsTenders_projecttype(url):
    from bs4 import BeautifulSoup as soup
    html = dy_pageextraction(url, 0)
    soup_ob = soup(html, 'html.parser')
    bid_type = soup_ob.find_all('div', {'id': 'extNonResponsive'})[0]
    bid_type = bid_type.find_all('td')[3].contents[0].strip()

    return bid_type

def BidsTenders_Extraction_OpenProjectTesting(url, client_name):
    list = []
    from bs4 import BeautifulSoup as soup
    html = dy_pageextraction(url, 3)

    soup = soup(html, 'html.parser')
    project_container = soup.find_all('tbody')[0]
    project_container_inner = project_container.find_all('div', {'style': 'float:right;'})

    for project in project_container_inner:
        project_name = project.span.contents[0]
        project_name = project_name.split('Bid Details - ')[1]

        # receive project website
        project_website = url + project.a['href']

        # recevie project
        project_type = BidsTenders_projecttype(project_website)
        list.append([client_name, project_type, project_name, project_website])
        print(list)

    return list

def excel_generator(list, filename):
    import \
        xlsxwriter

    import pandas as pd
    df = pd.DataFrame(list)
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='output', index=False)
    writer.save()

def BidsTenders_Extraction_AwardedProject(project_name, client_name, url):
    '''
    start development: Feb 19th, 2021
    end development: ?????

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


    '''
    from bs4 import BeautifulSoup as soup
    html = dy_pageextraction(url, 0)
    soup_ob = soup(html, 'html.parser')

    # web checking:
    error = str(soup_ob.find_all('body')[0].contents[0])
    if 'error' in error:
        return [client_name, project_name,'','','','','','','','','','']

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
        project_infobox = project_information.find_all('td')

        # set initial value for all output values
        output_bid_type = ''
        output_bid_id = ''
        output_projectname = ''
        output_awarded_date = ''
        output_awarded_year = ''
        for p in range(len(project_infobox)):

            if len(project_infobox[p].contents) != 0:

                if 'Bid Type' in project_infobox[p].contents[0]:
                    output_bid_type = project_infobox[p+1].contents[0].strip()


                elif 'Bid Number' in project_infobox[p].contents[0]:
                    output_bid_id = project_infobox[p+1].contents[0].strip()


                elif 'Bid Name' in project_infobox[p].contents[0]:
                    output_projectname = project_infobox[p+1].contents[0].strip().title()


                elif 'Awarded Date' in project_infobox[p].contents[0]:
                    awarded_time = project_infobox[p+1].contents[0].split()
                    output_awarded_date = awarded_time[1] + ' ' + awarded_time[2].rstrip(',')
                    output_awarded_year = awarded_time[3]

                elif output_awarded_date =='' and output_awarded_year == '' and 'Bid Closing Date' in project_infobox[p].contents[0]:
                    awarded_time = project_infobox[p + 1].contents[0].split()
                    output_awarded_date = awarded_time[1] + ' ' + awarded_time[2].rstrip(',')
                    output_awarded_year = awarded_time[3]

        # receive awarded winners' name, they will be organzied in a string, and return how many winners
        # if there is one single winner, receive winner's price.

        awarded_company_table = soup_ob.find_all('div', {'id': 'dgAwarded_Container'})
        if len(awarded_company_table) == 0:
            output_no_winner = 0
            output_winnercompany_name =''
            output_winnerprice = ''

        else:
            awarded_company_table = awarded_company_table[0]
            awarded_company_names = awarded_company_table.find_all('div',
                                                                   {'class': 'x-grid3-cell-inner x-grid3-col-CompanyName'})
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
                                   output_projectname,
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
                        sum = sum.replace('<br/>','')
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
                                       output_projectname,
                                       output_bid_classification,
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
                        output_projectname,
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

        project_list = [list_project,list_submitter]

        return project_list

def BidTenders_AwardProjects(webdriver_address, clientname, url, jump, page):
    '''
    start development: Feb 28th, 2021 (or earlier as before it was not a function)
    end development: ?????

    Purpose: extract Multiple AWARDED projects' information when client url is provided. The function will return
    an excel spreadsheet which saved all AWARDED projects' information.

    Recommendation: function need to use BidsTenders_Extraction_AwardedProject

    Patch 0.1 - Feb 28th, 2021
    Original code always crush when it was scrapping at around page 7,8 due to unknown reason. The patch is added to
    eliminate the "pages need to be scrapped" by changing the "Limit Results' from "25" to "100"

    Patch 0.2 - March 3rd, 2021
    Error message: "selenium.common.exceptions.ElementClickInterceptedException: Message: Element
    <button class="btn btn-default repeater-next" type="button"> is not clickable at point (348,946)
    because another element <div class="repeater-pagination"> obscures it"
    Analysis: this may be a result of website loading issue. Time.sleep() function in the loop is used, it may has time
    wasting issue but it is a risk i can take
    Note(March 5th, 2021): above analysis is correct. Time

    Patch 0.3 - March 3rd, 2021 - March 4th, 2021
    The function exhibits slowness because it collect information one by one by one. The patch is added to allow for
    information collection for multiple websites happening at the same time

    Patch 0.4 - March 6th, 2021
    "jump" is added in as one of a function parameter, it is used to control how many web page a user is hopping to
    scrape at one time. It is related to concurrent function. The larger the jump number, the more efficient the
    the function would be; however, a larger risk may result in the user's addresses to be banned.

    Patch 0.5 - Superseding BidTenders_AwardProjects_PageSpecific Function - March 14th, 2021
    BidTenders_AwardProjects_PageSpecific was superseded.

    Patch 0.4 - Wining Price Extraction - March 14th, 2021
    Code modification to extract awarded company' cost. Majority of work was not done here, code in this function was
    modified to have the right columns for output.

    Patch 0.6 - Precision Extraction (for extraction function) - March 14th, 2021
    Code modification to "precision" extract the information we need. (note to can be applied here)
    1. Before information were extract based on the location, but now information will be extracted base on keywords.
    2. Before project name and project type were extract from Function "BidTenders_AwardProjects", which was not ideal
       as the name show in the main page is not accurate. Modification is made.

    Patch 0.7 - Bids Submitted Information Extraction - March 15th, 2021
    Codes added to extract Bids Submitted Information

    Patch 0.8 - Modification in List_Submitter - March 16th, 2021
    Code modification to solve the following problem
    2. list_submitter can supersede the list_project

    '''
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import concurrent.futures
    import time
    from bs4 import BeautifulSoup as soup

    s = Service(path)
    driver = webdriver.Firefox(service=s)
    # Click "Awarded" li[5] to re-filter the table

    driver.get(url)

    try:
        button_bidtype = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.btn.btn-default.dropdown-toggle.input-lg'))
        )
        button_bidtype.click()
    finally:
        #li = button_bidtype.parent.find_elements_by_tag_name('li') superceded
        li = button_bidtype.parent.find_elements(by=By.TAG_NAME, value='li')
        time.sleep(3)
        li[5].click()

    time.sleep(3)
    try:
        button_limitresults = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.btn-group.selectlist.dropup'))
        )
        button_limitresults.click()
    finally:
        #li_2 = button_limitresults.find_elements_by_tag_name('li')
        li_2 = button_limitresults.find_elements(by=By.TAG_NAME, value='li')
        li_2[3].click()

    # try&final does not work here as page always have a 'repeater-pages', time.sleep() need to be forced
    # code below to find the page number`

    time.sleep(7)
    #page_number = driver.find_element_by_class_name('repeater-pages')
    page_number = driver.find_element(by=By.CLASS_NAME, value='repeater-pages')
    page_number = int(page_number.text)
    print(page_number)

    # initiate list
    list_projects = [
        ['client_name',
         'project_name',
         'bid_classification',
         'bid_type',
         'bid_ID',
         'awarded_date',
         'awarded_year',
         'no_winner',
         'winner_company_name',
         'winner_price',
         'no_submitted',
         'submitted_name']
    ]

    list_projectsubmitters = [
        ['client_name',
         'project_name',
         'bid_classification',
         'bid_type',
         'bid_ID',
         'awarded_date',
         'awarded_year',
         'company_name',
         'submitted_price',
         'winning_status']
    ]

    # Patch 0.5: Code to get to the right page

    if page != 0:
        for i in range(page):
                time.sleep(15)
                #button_next = driver.find_element_by_css_selector('.btn.btn-default.repeater-next')
                button_next = driver.find_element(by=By.CSS_SELECTOR, value='.btn.btn-default.repeater-next')
                button_next.click()


    # code below to iterate through the page
    time.sleep(7)

    for _ in range(page, page_number, 1):
        time.sleep(1)

        if _ == page and page != 0:
            time.sleep(20)

        start = time.time()
        # with in the _ of page number to extract: address of each "bid detail"

        html = driver.page_source
        soup_ob = soup(html, 'html5lib')

        project_container = soup_ob.find_all('tbody')[0]
        project_container_inner = project_container.find_all('div', {'style': 'float:right;'})

        if _ < page_number - 1:
            #button_next = driver.find_element_by_css_selector('.btn.btn-default.repeater-next')
            button_next = driver.find_element(by=By.CSS_SELECTOR, value='.btn.btn-default.repeater-next')
            button_next.click()


        # patch 0.3 notes: two loops
        # first loop: extract all project name and project web
        # second loop: (cocurrent processing)
        list_projectname = []
        list_projectweb = []
        list_clientname =[]

        for project in project_container_inner:
            # receive project name
            project_name = project.span.contents[0]
            project_name = project_name.split('- ')[2].strip()

            # receive the url to get into the page
            project_website = url + project.a['href']
            list_projectname.append(project_name)
            list_projectweb.append(project_website)
            list_clientname.append(clientname)

        print('LIST OF ALL PROJECT NAME: ',list_projectname)

        # ask for program to process 'jump' at one time, chunk the list
        list_projectname = [list_projectname[x:x + jump] for x in range(0, len(list_projectname), jump)]
        list_projectweb = [list_projectweb[x:x + jump] for x in range(0, len(list_projectweb), jump)]
        list_clientname = [list_clientname[x:x + jump] for x in range(0, len(list_clientname), jump)]

        for list_chunk_num in range(len(list_projectname)):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = executor.map(BidsTenders_Extraction_AwardedProject, list_projectname[list_chunk_num],
                                       list_clientname[list_chunk_num],list_projectweb[list_chunk_num])

                # results is a list of [list_project, [list_submitter]]
                # position 0: list_project  position 1: list_submitter


                for result in results:

                    # access and append list_project
                    print(result[0])
                    list_projects.append(result[0])

                    # access and append list_submitter
                    for item in result[1]:
                        list_projectsubmitters.append(item)

        print('list is printing:', list_projects)

        # export data to excel
        excel_generator(list_projects, '{}_projectoutput_{}.xlsx'.format(clientname,_+1))
        excel_generator(list_projectsubmitters, '{}_submitteroutput_{}.xlsx'.format(clientname, _ + 1))

        print('The page {} is completed'.format(_+1))
        end = time.time()
        print('Run time is', end-start)

    driver.quit()


# codes below us Chrome

path = 'C:/Users/PC/PycharmProjects/pythonProject/venv/geckodriver.exe'


# waterloo has issue.

client = [
    ['York Region', 'https://york.bidsandtenders.ca/'],
    ['Niagara Region', 'https://niagararegion.bidsandtenders.ca/'],
    ['Halton Region', 'https://haltonregion.bidsandtenders.ca/'],
    ['Waterloo Region', 'https://regionofwaterloo.bidsandtenders.ca/'],
    ['City of Brantford', 'https://brantford.bidsandtenders.ca/'],
    ['Brant County', 'https://brant.bidsandtenders.ca/'],
    ['Haldimand County', 'https://haldimandcounty.bidsandtenders.ca/'],
    ['City of Guelph', 'https://guelph.bidsandtenders.ca/'],
    ['Wellington County', 'https://wellington.bidsandtenders.ca/'],
    ['Dufferin County', 'https://dufferincounty.bidsandtenders.ca/'],
    ['City of Barrie', 'https://barrie.bidsandtenders.ca/'],
    ['Simcoe County', 'https://simcoecounty.bidsandtenders.ca/'],
    ['City of London', 'https://london.bidsandtenders.ca/'],
    ['City of Barrie', 'https://barrie.bidsandtenders.ca/'],
    ['City of Orillia', 'https://orillia.bidsandtenders.ca/'],
    ['Durham Region', 'https://durham.bidsandtenders.ca/'],
    ['City of Kawartha Lakes', 'https://kawarthalakes.bidsandtenders.ca/'],
    ['City Of Peterborough', 'https://cityofpeterborough.bidsandtenders.ca/'],
    ['Peterborough County', 'https://ptbocounty.bidsandtenders.ca/'],
    ['County of Northumberland', 'https://northumberlandcounty.bidsandtenders.ca/'],
    ['City of Hamilton', 'https://hamilton.bidsandtenders.ca/']
]


client_2 = [
    ['City of Orillia', 'https://orillia.bidsandtenders.ca/'],
    ['Durham Region', 'https://durham.bidsandtenders.ca/'],
    ['City of Kawartha Lakes', 'https://kawarthalakes.bidsandtenders.ca/'],
    ['City Of Peterborough', 'https://cityofpeterborough.bidsandtenders.ca/'],
    ['Peterborough County', 'https://ptbocounty.bidsandtenders.ca/'],
    ['County of Northumberland', 'https://northumberlandcounty.bidsandtenders.ca/'],
    ['City of Hamilton', 'https://hamilton.bidsandtenders.ca/']
]

BidTenders_AwardProjects(path, 'Durham Region', 'https://durham.bidsandtenders.ca/', 100, 0)

