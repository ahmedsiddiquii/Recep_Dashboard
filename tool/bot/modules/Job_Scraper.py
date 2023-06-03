from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import csv
import pandas as pd
import requests
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import re
import openai

import openai
import pickle

# Set up your OpenAI API credentials
openai.api_key = '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'
all_history=[]
#similarity between two company names
def calculate_similarity(company_name_1, company_name_2):
    prompt = f"Company 1: {company_name_1}\nCompany 2: {company_name_2}\nCalculate similarity percentage:"

    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=1,
        n=1,
        stop=None,
        temperature=0.0
    )

    similarity_percentage = response.choices[0].text.strip()
    return similarity_percentage


# this function extract email address from the website html body
def extract_emails(text):
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(pattern, text)
    return emails

#this function open website and go into contact page them extact html body and email
def scrape_contact_info(url):
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(2)
    try:

        # Check header and footer links for "Impressum" or "Imprint"
        header_links = driver.find_element("xpath", "//a[contains(text(), 'Impressum') or contains(text(), 'Imprint') or contains(text(), 'Contact') or contains(text(), 'contact')]")
        # footer_links = driver.find_elements('footer a')
        links = header_links.get_attribute("href")
        driver.get(links)
        time.sleep(0.8)

        # Extract email addresses from the page
        email_addresses = extract_emails(driver.page_source)
        if len(email_addresses) > 0:
            email_addresses = list(set(email_addresses))
            email_addresses = ', '.join(email_addresses)
            print(email_addresses)

            # driver.quit()
            driver.close()
            return email_addresses
        driver.close()
        return "-"
    except:
        driver.close()
        return "-"


#Linkedin Job Scraper class
class Linkedin:
    # Iniialize the driver and go on the specific filtered URL
    def initilize_driver(self,link):
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-infobars')
        # options.add_argument('--disable-extensions')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-browser-side-navigation')
        options.add_argument('--remote-debugging-address=0.0.0.0')
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--remote-debugging-port=0')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        driver = uc.Chrome(options=options)
        driver.get(link)
        time.sleep(5)
        driver.maximize_window()
        return driver

    #scrape the jobs and iterates untill reached the limit define by the user
    def scrap(self,driver,no_of_jobs):
        data = []
        keyword=driver.find_element("xpath","//input[@aria-controls='job-search-bar-keywords-typeahead-list']").get_attribute("value")
        location = driver.find_element("xpath", "//input[@name='location']").get_attribute("value")
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        all_div = driver.find_elements(by='xpath', value='//ul[@class="jobs-search__results-list"]//li')
        history=[]
        while True:
            all_div = driver.find_elements(by='xpath', value='//ul[@class="jobs-search__results-list"]//li')
            if len(data) >= no_of_jobs:
                break
            for i,elem in enumerate(all_div):
                if len(data)>=no_of_jobs:
                    break
                if i in history:
                    continue
                actions=ActionChains(driver)
                actions.move_to_element(elem).click().perform()
                # i.click()
                time.sleep(2)
                try:
                    tit = driver.find_element(by='xpath', value='//div//a[@class="topcard__link"]//h2').text
                    print(tit)

                    comp = driver.find_element(by='xpath', value='//div[@class="topcard__flavor-row"]//span//a').text
                    if {"keword": keyword, 'company_name': comp, 'job_title': tit} in all_history:
                        continue
                    # time.sleep(2)
                    driver.find_element(by='xpath',
                                        value='//button[@aria-label="Show more, visually expands previously read content above"]').click()
                    time.sleep(1)
                    try:
                        desc = driver.find_element(by='xpath',
                                                   value='//div[@class="decorated-job-posting__details"]//section[@class="core-section-container my-3 description"]').text
                    except:
                        desc=""
                    link = self.get_first_google_link(comp)
                    email=scrape_contact_info(link)
                    source_url=driver.current_url
                    data.append(
                        {"keword": keyword, 'company_name': comp, 'job_title': tit, 'description': desc,
                         'company_website': link,
                         "source_link": source_url, "source_website": "Linkedin", "company_email": str(email),
                         "company_phone_number": "-","location":location})
                    all_history.append({"keword": keyword, 'company_name': comp, 'job_title': tit})
                    history.append(i)
                except:
                    pass
            try:
                driver.find_element("xpath","//button[@aria-label='Show more jobs']").click()
                time.sleep(2)
            except:
                pass
        return data


    # search company name on google and fetch first link by skiping sponsored links
    def get_first_google_link(self, query):
        query = query.replace(' ', '+')
        url = f"https://www.google.com/search?q={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.1234.5678 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all search result links using CSS selectors
        search_results = soup.select('div.yuRUbf a')

        # Extract the URLs from the links
        links = [result['href'] for result in search_results]
        first_link = links[0]

        # Check if the link contains unwanted domains
        unwanted_domains = ['wikipedia', 'instagram', 'facebook', 'linkedin', 'indeed', 'twitter', 'pinterest',
                            'youtube']
        for domain in unwanted_domains:
            if domain in first_link:
                return None

        return first_link

class GlassDoor:
    def initilize_driver(self,link):
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-infobars')
        # options.add_argument('--disable-extensions')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-browser-side-navigation')
        options.add_argument('--remote-debugging-address=0.0.0.0')
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--remote-debugging-port=0')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        driver = uc.Chrome(options=options)
        driver.get(link)
        driver.maximize_window()
        time.sleep(5)
        # try:
        #     cookies = pickle.load(open("cookies.pkl", "rb"))
        #     for cookie in cookies:
        #         driver.add_cookie(cookie)
        #     driver.get("https://www.glassdoor.de/member/home/index.html/")
        # except:
        #     driver.get("https://www.glassdoor.de/member/home/index.html/")
        #     time.sleep(5)
        #     self.login(driver,"")
        return driver

    def login(self,driver,keyword):
        email = driver.find_element(by='xpath', value='//div//input[@name="username"]').send_keys(
            'sak345khan@gmail.com')
        time.sleep(5)
        continue_w_e = driver.find_element(by='xpath',
                                           value='//button[@class="gd-ui-button mt-std w-100pct email-button css-1dqhu4c evpplnh0"]').click()
        continue_w_g = driver.find_element(by='xpath', value='//button[@class="google gd-btn "]').click()
        time.sleep(35)
        continue_w_g = driver.find_element(by='xpath', value='//button[@class="google gd-btn "]').click()
        time.sleep(35)




    def scrap(self,driver,search_keyword,no_of_jobs):
        data = []
        history=[]
        actions=ActionChains(driver)
        carts = driver.find_elements(by='xpath', value='//li[contains(@class,"react-job-listing css")]')
        search_keyword=driver.find_element("xpath","//input[@aria-label='Search Keyword']").get_attribute("value")
        try:
            driver.find_element("xpath","//button[@id='onetrust-accept-btn-handler']").click()
        except:
            pass
        while True:
            if len(data)>=no_of_jobs:
                break
            for i, value in enumerate(carts):
                if len(data)>=no_of_jobs:
                    break
                try:
                    actions.move_to_element(value).click().perform()
                    time.sleep(1.5)
                    company = driver.find_element(by='xpath', value='//div[@data-test="employerName"]').text

                    title = driver.find_element(by='xpath', value='//div[@data-test="jobTitle"]').text
                    print(title)
                    location=driver.find_element("xpath","//div[@data-test='location']").text
                    if {"keword": search_keyword, 'company_name': company, 'job_title': title} in all_history:
                        continue
                    try:
                        show_more = driver.find_element(by='xpath', value='//div[@class="css-t3xrds e856ufb4"]')
                        actions.move_to_element(show_more).click().perform()
                        time.sleep(1)
                    except:
                        pass
                    description = driver.find_element(by='xpath', value='//div[@class="jobDescriptionContent desc"]').text
                except Exception as e:
                    print(e)
                    pass
                try:
                    source_url=driver.find_element("xpath",f"(//a[@data-test='job-link'])[{i+1}]").get_attribute('href')
                    link = self.get_first_google_link(company)
                except:
                    link=""
                try:
                    emails=scrape_contact_info(link)
                except:
                    emails=None
                data.append({"keword":search_keyword,'company_name': company, 'job_title': title, 'description': description, 'company_website': link,
                             "source_link":source_url,"source_website":"GlassDoor",
                             "company_email":str(emails),"company_phone_number":"-","location":location})
                all_history.append({"keword": search_keyword, 'company_name': company, 'job_title': title})
            try:
                next=driver.find_element("xpath","//button[@aria-label='Next'][@disabled]")
                break

            except:
                next = driver.find_element("xpath", "//button[@aria-label='Next']")

                actions.move_to_element(next).click().perform()
        return data

    def get_first_google_link(self, query):
        query = query.replace(' ', '+')
        url = f"https://www.google.com/search?q={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.1234.5678 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all search result links using CSS selectors
        search_results = soup.select('div.yuRUbf a')

        # Extract the URLs from the links
        links = [result['href'] for result in search_results]
        first_link = links[0]

        # Check if the link contains unwanted domains
        unwanted_domains = ['wikipedia', 'instagram', 'facebook', 'linkedin', 'indeed', 'twitter', 'pinterest',
                            'youtube']
        for domain in unwanted_domains:
            if domain in first_link:
                return None

        return first_link

class Talent:
    def initialize(self,link):
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-infobars')
        # options.add_argument('--disable-extensions')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-browser-side-navigation')
        options.add_argument('--remote-debugging-address=0.0.0.0')
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--remote-debugging-port=0')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        driver = uc.Chrome(options=options)
        driver.get(link)
        driver.maximize_window()

        return driver

    def get_first_google_link(self, query):
        query = query.replace(' ', '+')
        url = f"https://www.google.com/search?q={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.1234.5678 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all search result links using CSS selectors
        search_results = soup.select('div.yuRUbf a')

        # Extract the URLs from the links
        links = [result['href'] for result in search_results]
        first_link = links[0]

        # Check if the link contains unwanted domains
        unwanted_domains = ['wikipedia', 'instagram', 'facebook', 'linkedin', 'indeed', 'twitter', 'pinterest',
                            'youtube']
        for domain in unwanted_domains:
            if domain in first_link:
                return None

        return first_link

    def scrape(self,driver,keyword,no_of_jobs):
        data = []

        keyword=driver.find_element("xpath","//input[@placeholder='Job title, company']").get_attribute("value")



        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        while True:
            if len(data) >= no_of_jobs:
                break
            all_div = driver.find_elements(by='xpath', value='//div[@class="link-job-wrap"]')
            for i,elem in enumerate(all_div):
                if len(data)>=no_of_jobs:
                    break
                try:
                    elem.click()
                except:

                    pass
                time.sleep(2)
                tit = driver.find_element(by='xpath',
                                          value='//div[@class="jobPreview__header--title"]').text
                comp = driver.find_element(by='xpath', value='//div[@class="jobPreview__header--company"]').text
                if {"keword": keyword, 'company_name': comp, 'job_title': tit} in all_history:
                    continue
                desc = driver.find_element(by='xpath', value='//div[@class="jobPreview__body--description"]').text
                location=driver.find_element("xpath","//div[@class='jobPreview__header--location']").text
                try:
                    link = self.get_first_google_link(comp)
                    emails = scrape_contact_info(link)
                except:
                    link=""
                    emails=""
                source_url=driver.current_url

                data.append(
                    {"keword": keyword, 'company_name': comp, 'job_title': tit, 'description': desc,
                     'company_website': link,
                     "source_link": source_url, "source_website": "Talent", "company_email": str(emails),
                     "company_phone_number": "-","location":location})
                all_history.append({"keword": keyword, 'company_name': comp, 'job_title': tit})
            try:
                driver.find_element("xpath","//span[@class='page-next page ']//parent::a").click()
                time.sleep(2)
            except:
                break
        return data

class Indeed:
    def initialize(self,link):

        options = webdriver.ChromeOptions()
        options.add_argument('--disable-infobars')
        # options.add_argument('--disable-extensions')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-browser-side-navigation')
        options.add_argument('--remote-debugging-address=0.0.0.0')
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--remote-debugging-port=0')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        driver = uc.Chrome(options=options)
        driver.get(link)
        driver.maximize_window()
        time.sleep(9)
        try:
            driver.switch_to.frame(driver.find_element("xpath","//iframe"))
            time.sleep(1)
            driver.find_element("xpath","//input[@type='checkbox']").click()
            time.sleep(3)
            driver.switch_to.default_content()
        except Exception as e:
            driver.switch_to.default_content()
            pass
        return driver

    def get_first_google_link(self,query):
        query = query.replace(' ', '+')
        url = f"https://www.google.com/search?q={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.1234.5678 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all search result links using CSS selectors
        search_results = soup.select('div.yuRUbf a')

        # Extract the URLs from the links
        links = [result['href'] for result in search_results]
        first_link = links[0]

        # Check if the link contains unwanted domains
        unwanted_domains = ['wikipedia', 'instagram', 'facebook', 'linkedin', 'indeed', 'twitter', 'pinterest',
                            'youtube']
        for domain in unwanted_domains:
            if domain in first_link:
                return None

        return first_link

    def scrape(self, driver,filter_url,no_of_jobs):
        data = []
        time.sleep(7)
        try:
            driver.find_element("xpath","//button[@id='onetrust-accept-btn-handler']").click()
        except:
            pass
        keyword=filter_url.split("&l=")[0].split("q=")[1].replace("+"," ")
        location = filter_url.split("&from=")[0].split("l=")[1].replace("+"," ")
        all_div = driver.find_elements(by='xpath', value='//div[@class="slider_container css-77eoo7 eu4oa1w0"]')
        last_height = driver.execute_script("return document.body.scrollHeight")
        actions=ActionChains(driver)
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        while True:
            if len(data) >= no_of_jobs:
                break
            all_div = driver.find_elements(by='xpath', value='//div[@class="slider_container css-77eoo7 eu4oa1w0"]')
            for i,elem in enumerate(all_div):
                if len(data)>=no_of_jobs:
                    break
                try:
                    actions.move_to_element(elem).click().perform()

                except:
                    pass
                time.sleep(2)
                source_url=driver.find_element("xpath",f'(//div[@class="slider_container css-77eoo7 eu4oa1w0"])[{i+1}]//a').get_attribute('href')
                print(source_url)
                try:
                    tit = driver.find_element(by='xpath',
                                              value='//div[contains(@class,"jobsearch-JobInfoHeader-title-container ")]').text
                    comp = driver.find_element(by='xpath', value='//div[@data-company-name="true"]//a').text
                    desc = driver.find_element(by='xpath', value='//div[@id="jobDescriptionText"]').text
                    print(comp)
                    if {"keword": keyword, 'company_name': comp, 'job_title': tit} in all_history:
                        continue
                    try:
                        link = self.get_first_google_link(comp)
                        print(link)
                        email = scrape_contact_info(link)
                        print(email)
                    except Exception as e:
                        print(e)
                        link=""
                        email=""

                    data.append(
                        {"keword": keyword, 'company_name': comp, 'job_title': tit, 'description': desc,
                         'company_website': link,
                         "source_link": source_url, "source_website": "Indeed", "company_email": str(email),
                         "company_phone_number": "-","location":location})
                    all_history.append({"keword": keyword, 'company_name': comp, 'job_title': tit})
                except Exception as e:

                    pass
            try:
                driver.find_element("xpath","//a[@aria-label='Next Page']").click()
                time.sleep(2)
            except:
                break
        return data