import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random
from urllib import robotparser

def get_headings(driver):
    headings_h = driver.find_elements(
        By.XPATH, "//h1 | //h2 | //h3 | //h4 | //h5 | //h6")
    headings = [heading.text.strip()
                for heading in headings_h if len(heading.text) > 1]
    subheadings_h = driver.find_elements(
        By.XPATH, "//h2 | //h3 | //h4 | //h5 | //h6")
    paragraphs = driver.find_elements(By.XPATH, "//p")
    subheadings = [subheading.text.strip()
                   for subheading in subheadings_h if len(subheading.text) > 1]
    for paragraph in paragraphs:
        font_size = paragraph.value_of_css_property("font-size")
        font_weight = paragraph.value_of_css_property("font-weight")
        text = paragraph.text.strip()
        # headings
        if (
            font_size and font_weight
            and (font_weight == "bold" or float(font_size[:-2]) > 15)
            and len(text) > 4
        ):
            headings.append(text)
        # subheadings
        elif (
            font_size
            and (float(font_size[:-2]) > 12 and float(font_size[:-2]) <= 15)
            and len(text) > 4
        ):
            subheadings.append(text)
    return headings[:10], subheadings[:10]

def scrape_page(url, driver, word_limit = 2000):
    driver.get(url)
    time.sleep(5)

    # close popups
    try:
        driver.switch_to.active_element.click()
    except:
        pass    
    
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    #headings & subheadings
    headings_text, subheadings_text = get_headings(driver)
    
    # meta description
    meta_description = soup.find('meta', attrs={'name': 'description'})

    # body text
    body_text = soup.get_text(separator=' ')
    body_text = re.sub(r'\s+', ' ', body_text).strip()
    
    words = body_text.split()[:word_limit]
    limited_body_text = ' '.join(words)

    return meta_description, limited_body_text, headings_text, subheadings_text    

def convert_to_structured_url(url):
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    parsed_url = urlparse(url)
    structured_url = urljoin(
        parsed_url.scheme + '://' + parsed_url.netloc, parsed_url.path)

    return structured_url


def scrape_web(url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(600)
    url = convert_to_structured_url(url)
    meta_description, limited_body_text, headings_text, subheadings_text = scrape_page(url, driver)
    driver.quit()
    return {'meta_description': meta_description, 'website_text': limited_body_text, 'website_headings': headings_text, 'website_subheadings': subheadings_text}