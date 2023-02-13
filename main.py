# Import libraries
import pandas as pd
from datetime import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
import time

def get_url():
    """Generate url from position and location"""
    url = 'https://www.indeed.com'
    return url


def seachJob(position, location, driver):
    """ search name job and job location"""
    driver.find_element_by_id("text-input-what").send_keys(position)
    driver.find_element_by_id("text-input-where").send_keys(location)
    driver.find_element_by_xpath("//button[@class='yosegi-InlineWhatWhere-primaryButton']").click()


def save_data_to_file(records):
    """Save data to csv file"""
    col = ['JobTitle', 'Company', 'Location', 'PostDate', 'ExtractDate', 'Summary', 'JobUrl']
    df = pd.DataFrame(records, columns = col)
    return df


def get_record(card, targLink, NameJob):
    """Extract job data from single card"""
    driver = webdriver.Chrome('C:\\Users\\Tran Huu An\\Desktop\\chromedriver_win32\\chromedriver.exe')
    driver.get(targLink)

    summary = driver.find_element_by_class_name('jobsearch-jobDescriptionText').text
    job_title = card.find_element_by_class_name('jobTitle').text
    company = card.find_element_by_class_name('companyName').text
    location = card.find_element_by_class_name('companyLocation').text
    post_date = card.find_element_by_class_name('date').text
    extract_date = datetime.today().strftime('%Y-%m-%d')
    driver.close()
    return (job_title, company, location, post_date, extract_date, summary, NameJob)


def get_page_records(cards, tagLinks, job_list, url_set, driver, NameJob):
    """Extract all cards from the page"""
    for (card, tagLink) in zip(cards, tagLinks):
        record = get_record(card, str(tagLink.get_attribute('href')), NameJob)
        # add if job title exists and not duplicate
#         if record[0] and record[-1] not in url_set:
        job_list.append(record)


df = pd.DataFrame(columns=['JobTitle', 'Company', 'Location', 'PostDate', 'ExtractDate', 'Summary', 'JobUrl'])


def main(position, location, df):
    """Run the main program routine"""
    scraped_jobs = []
    scraped_urls = set()
    numberHeightPage = 0
    url = get_url()

    # setup web driver
    driver = webdriver.Chrome('C:\\Users\\Tran Huu An\\Desktop\\chromedriver_win32\\chromedriver.exe')
    driver.implicitly_wait(5)
    driver.get(url)

    # search Job

    seachJob(position, location, driver)
    try:
        driver.find_element_by_xpath('//button[@aria-label="close"]').click()
    except:
        pass
    # extract the job data
    while True:
        numberHeightPageStart = numberHeightPage
        numberHeightPage += 1000
        scrollPage = "window.scrollBy(" + str(numberHeightPageStart) + "," + str(numberHeightPage) + ")"
        driver.execute_script(scrollPage, "")
        cards = driver.find_elements_by_class_name('job_seen_beacon')
        #         get_page_records(cards, scraped_jobs, scraped_urls, driver, position)
        tagLinks = driver.find_elements_by_class_name("jcs-JobTitle")

        get_page_records(cards, tagLinks, scraped_jobs, scraped_urls, driver, position)

        try:
            driver.find_element_by_xpath('//a[@data-testid="pagination-page-next"]').click()
        except NoSuchElementException:
            break
        except ElementNotInteractableException:
            driver.find_element_by_id('popover-x').click()  # to handle job notification popup
            get_page_records(cards, tagLinks, scraped_jobs, scraped_urls, driver, position)
            continue

        try:
            driver.find_element_by_xpath('//button[@aria-label="close"]').click()
        except:
            pass

    # close driver and save records
    driver.quit()
    dataFrame = save_data_to_file(scraped_jobs)
    df = pd.concat([df, dataFrame])
    return df


resultData  = pd.DataFrame(columns = ['JobTitle', 'Company', 'Location', 'PostDate', 'ExtractDate', 'Summary', 'JobUrl'])
with open('nameJob.txt', 'r', encoding = 'utf-8') as name:
    for i in range(35):
        string = str(name.readline())
        if string != '\n':
            dataFrame = main(string, 'Việt Nam', df)
            resultData = pd.concat([resultData, dataFrame])