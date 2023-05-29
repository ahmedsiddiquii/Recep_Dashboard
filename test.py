from selenium import webdriver
import time
import re
import csv
import pandas as pd
from selenium.webdriver.chrome.options import Options

def extract_emails(text):
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(pattern, text)
    return emails
def scrape_contact_info(url):
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(3)
    try:

        # Check header and footer links for "Impressum" or "Imprint"
        header_links = driver.find_element("xpath","//a[contains(text(), 'Impressum') or contains(text(), 'Imprint')]")
        # footer_links = driver.find_elements('footer a')
        links = header_links.get_attribute("href")
        driver.get(links)
        time.sleep(0.8)

        # Extract email addresses from the page
        email_addresses = extract_emails(driver.page_source)
        if len(email_addresses)>0:
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
print(scrape_contact_info("https://www.lunar-x.com/"))