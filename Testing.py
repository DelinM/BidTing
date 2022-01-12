from bs4 import BeautifulSoup as soup
import smtplib, ssl
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
from bs4 import BeautifulSoup as soup
import lxml
import html5lib

import concurrent.futures
import pandas as pd

def dy_pageextraction(url, sleeptime):
    """
    Extract HTML for dynamic website, aka JS
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--incognito')
    options.add_argument('--ignore_certificate-error')
    drive = webdriver.Chrome(executable_path='C:/Users/Delin/Desktop/BidAlert/venv/Lib/chromedriver', options=options)
    drive.get(url)
    time.sleep(sleeptime)
    html = drive.page_source
    drive.close()
    return html


def COT_Extraction_AwardedProject():
    '''
    Start Development: March 17th, 2021
    End Developmenbt: ?????

    Purpose: Extract awarded project information from the City of Toronto since it is not
    use bid and tender system
    '''

    from bs4 import BeautifulSoup as soup
    url = 'https://wx.toronto.ca/inter/pmmd/callawards.nsf/postedawards?OpenView&Start=1&Count=1000&ExpandView'
    project_inital_url = 'https://wx.toronto.ca'
    html = dy_pageextraction(url, 0)
    soup_ob =soup(html, 'html.parser')

    projects_links = []
    project_info_list =[]

    for link in soup_ob.find_all('a', href=True):
        if 'OpenDocument' in str(link):
            projects_links.append(project_inital_url + link['href'])

    for i in range(len(projects_links)):
        project_html = dy_pageextraction(projects_links[i], 0)
        project_soup = soup(project_html, 'html.parser')

        project_table = project_soup.find_all('table', {'width':'770',
                                                        'cellpadding':'0',
                                                        'cellspacing':'0',
                                                        'border': '0'})

        # The third (3) table contains the information I need. Location: 2

        if len(project_table) == 3:
            project_spec_table = project_table[2].find_all('td',{'width':'631',
                                                                 'valign':'top',
                                                                 'align':'left'})[0]

            project_info = project_spec_table.find_all('font', {'face':'Arial',
                                                                'size':'2'})


            for i, content in enumerate(project_info):
                if content.contents != []:
                    project_info_list.append(content.contents)

            project_info_list.remove([', '])
            #
            # for item in project_info_list:
            #     print(item)
            #     print('\n')

            #initial value
            project_category = ''
            project_subcategory = ''
            project_name = ''
            project_id = ''
            project_winner = ''
            project_price = ''
            project_date = ''
            project_year = ''

            for i, item in enumerate(project_info_list):
                if 'Commodity:' in item:
                    project_category = project_info_list[i+1][0]
                    project_subcategory = project_info_list[i+2][0]
                    project_subcategory = project_subcategory.capitalize()

                if 'Description:' in item:
                    project_name = project_info_list[i+1][0]

                if 'Call number:' in item:
                    project_id = project_info_list[i+1][0] + project_info_list[i+2][0]
                    project_id = project_id.strip(' ')

                if 'and contract amount:' in item:
                    project_winner = project_info_list[i+1][0]
                    project_winner = project_winner.capitalize()

                if '$' in item and len(item[0]) > 1:
                    project_price = project_info_list[i]

                if 'Date awarded:' in item:
                    project_dateyear = project_info_list[i+1][0]
                    project_dateyear = project_dateyear.split(',')
                    project_date = project_dateyear[0]
                    project_year = project_dateyear[1].strip('')


            final_list = ['City of Toronto',
                          project_category,
                          project_subcategory,
                          project_id,
                          project_name,
                          project_winner,
                          project_price,
                          project_date,
                          project_year]


            print(final_list)


        else:
            print('error')






    # projects_table = soup_ob.find_all('table', {'border': '0', 'cellpadding':'2','cellspacing':'0'})[0]
    # projects_container = projects_table.find_all('tr')
    # print(len(projects_container))
    #
    #
    # for _ in range(len(projects_container)):
    #     project_container = projects_container[_].find_all('td')
    #
    #     if len(project_container) == 12:
    #         project_heart = projects_container[4].find_all('a')
    #         if len(project_heart) >=1:
    #             if len(project_heart[0].contents) >= 1:
    #                 project_id = project_heart[0].contents[0]
    #                 print(project_id)
    #             elif len(project_heart[0].contents) == 0:
    #                 project_id = ''
    #                 print('blank')
    #

    # for content in project_container:
    #     if len(content.contents) >=1:
    #         print(content.contents[0])


    #projects_table = projects_fonttable.find_all('table')





COT_Extraction_AwardedProject()




# project_name = 'Sudbury'
# client_name = 'Niagara'
# url = 'https://brantford.bidsandtenders.ca/Module/Tenders/en/Tender/Detail/edd05dbc-cd94-4789-97c9-c47945a7c1d1'
#
# list = BidsTenders_Extraction_AwardedProject(project_name, client_name, url)
# print(list)

