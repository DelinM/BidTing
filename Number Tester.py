Superscieded equation

def BidTenders_AwardProjects_PageSpecific(webdriver_address, clientname, url, jump, page):
    '''
    start development: Match 6th, 2021
    end development: ?????

    Purpose: if data extraction process has issue, the function can be called to start to continue working on
    process. page provide the number of the page that was last page that got completed.
    from selenium.webdriver.common.keys import Keys
    '''
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import concurrent.futures
    import time
    from bs4 import BeautifulSoup as soup
    from selenium.webdriver.common.keys import Keys

    driver = webdriver.Firefox(executable_path=webdriver_address)

    # Click "Awarded" li[5] to re-filter the table
    driver.get(url)
    try:
        button_bidtype = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.btn.btn-default.dropdown-toggle.input-lg'))
        )
        button_bidtype.click()
    finally:
        li = button_bidtype.parent.find_elements_by_tag_name('li')
        li[5].click()

    time.sleep(3)
    try:
        button_limitresults = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.btn-group.selectlist.dropup'))
        )
        button_limitresults.click()
    finally:
        li_2 = button_limitresults.find_elements_by_tag_name('li')
        li_2[3].click()

    # try&final does not work here as page always have a 'repeater-pages', time.sleep() need to be forced
    # code below to find the page number`

    time.sleep(7)
    page_number = driver.find_element_by_class_name('repeater-pages')
    page_number = int(page_number.text)
    print(page_number)

    # initiate list
    list = [
        ['client_name', 'project_name', 'bid_classification', 'bid_type', 'bid_ID','awarded_date', 'awarded_year', 'no_winner',
         'winner_company_name', 'no_submitted', 'submitted_name']]

    i = 0
    # code to get to the right page
    for i in range(page):
            time.sleep(15)
            button_next = driver.find_element_by_css_selector('.btn.btn-default.repeater-next')
            button_next.click()

    for _ in range(page, page_number, 1):
        time.sleep(1)

        if _ == page:
            time.sleep(20)

        start = time.time()
        # with in the _ of page number to extract: address of each "bid detail"

        html = driver.page_source
        soup_ob = soup(html, 'html5lib')

        project_container = soup_ob.find_all('tbody')[0]
        project_container_inner = project_container.find_all('div', {'style': 'float:right;'})

        if  _ < page_number - 1:
            button_next = driver.find_element_by_css_selector('.btn.btn-default.repeater-next')
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

        # ask for program to process 8 at one time, chunk the list
        list_projectname = [list_projectname[x:x + jump] for x in range(0, len(list_projectname), jump)]
        list_projectweb = [list_projectweb[x:x + jump] for x in range(0, len(list_projectweb), jump)]
        list_clientname = [list_clientname[x:x + jump] for x in range(0, len(list_clientname), jump)]

        for list_chunk_num in range(len(list_projectname)):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = executor.map(BidsTenders_Extraction_AwardedProject, list_projectname[list_chunk_num],
                                       list_clientname[list_chunk_num],list_projectweb[list_chunk_num])

                for result in results:
                    print(result)
                    list.append(result)

        print('list is printing:', list)
        excel_generator(list, '{}_output_{}_backup.xlsx'.format(clientname,_+1))

        print('The page {} is completed'.format(_+1))
        end = time.time()
        print('Run time is', end-start)

    driver.quit()