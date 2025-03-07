import time
import random
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(filename='linkedin_scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Chrome options for anti-detection and disabling WebRTC
chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
chrome_options.add_argument("--disable-webrtc")  # Disable WebRTC to avoid STUN errors
# chrome_options.add_argument("--headless")  # Uncomment for headless mode

# Initialize WebDriver with webdriver-manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def login_to_linkedin():
    """Log in to LinkedIn using credentials from .env."""
    try:
        # Retrieve credentials from environment variables
        username = os.getenv("LINKEDIN_EMAIL")
        password = os.getenv("LINKEDIN_PASSWORD")
        
        if not username or not password:
            raise ValueError("LinkedIn email or password not found in .env file")
        
        driver.get("https://www.linkedin.com/login")
        time.sleep(random.uniform(2, 5))
        
        username_field = driver.find_element(By.ID, "username")
        username_field.send_keys(username)
        time.sleep(random.uniform(1, 3))
        
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)
        time.sleep(random.uniform(1, 3))
        
        password_field.send_keys(Keys.RETURN)
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "global-nav__me"))
        )
        logging.info("Logged in to LinkedIn")
    except Exception as e:
        logging.error(f"Login failed: {str(e)}")
        raise

def scrape_about_section(company_url):
    """Scrape data from the About section using BeautifulSoup with updated selectors."""
    about_data = {}
    try:
        driver.get(f"{company_url}/about")
        time.sleep(random.uniform(5, 10))  # Increased wait for page load
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "org-top-card-summary-info-list"))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        logging.info(f"Page source length for {company_url}/about: {len(driver.page_source)}")  # Debug page load
        
        # Find the main about section
        about_section = soup.find('section', class_='artdeco-card org-page-details-module__card-spacing artdeco-card org-about-module__margin-bottom')
        if not about_section:
            logging.warning(f"About section not found for {company_url}")
            return about_data
        
        # Overview
        overview = about_section.find('p', class_='break-words white-space-pre-wrap t-black--light text-body-medium')
        about_data["Overview"] = overview.text.strip() if overview else ""
        
        # Find the dl containing details
        details_list = about_section.find('dl', class_='overflow-hidden')
        if details_list:
            dt_dd_pairs = details_list.find_all(['dt', 'dd'], recursive=False)
            for i in range(0, len(dt_dd_pairs), 2):
                if i + 1 < len(dt_dd_pairs):
                    dt = dt_dd_pairs[i]
                    dd = dt_dd_pairs[i + 1]
                    key = dt.text.strip().lower().replace(" ", "_")
                    value = dd.text.strip() if not dd.find('a') else dd.find('a')['href']
                    if key:
                        about_data[key] = value
        
        # Explicitly handle Website if it's an <a> tag
        website_link = about_section.find('a', href=True, text=lambda t: t and 'http' in t)
        if website_link and "website" not in about_data:
            about_data["website"] = website_link['href']
        
        # Log the scraped data for debugging
        logging.info(f"Scraped About section for {company_url}: {about_data}")
        
    except Exception as e:
        logging.error(f"About section scrape failed for {company_url}: {str(e)}")
        for key in ["overview", "website", "industry", "company_size", "headquarters", "founded", "specialties"]:
            about_data[key] = about_data.get(key, "")
    return about_data

def scrape_people_section(company_url):
    """Scrape data from the People section using BeautifulSoup with pagination handling."""
    people_data = {"What they do": {}, "Where they live": {}}
    try:
        driver.get(f"{company_url}/people")
        time.sleep(random.uniform(5, 10))
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "org-people__insights-container"))
        )
        
        # Expand "Show More" buttons
        for _ in range(3):
            try:
                show_more = driver.find_element(By.CLASS_NAME, "artdeco-button--tertiary")
                show_more.click()
                time.sleep(random.uniform(1, 3))
            except Exception:
                try:
                    show_more = driver.find_element(By.CLASS_NAME, "artdeco-button--secondary")
                    show_more.click()
                    time.sleep(random.uniform(1, 3))
                except Exception:
                    break
        
        # Step 1: Scrape "Where they live" from the initial page
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        logging.info(f"Initial page source length for {company_url}/people: {len(driver.page_source)}")
        
        where_they_live_container = soup.find(class_='org-people-bar-graph-module__geo-region')
        if where_they_live_container:
            insight_container = where_they_live_container.find(class_='insight-container')
            if insight_container:
                buttons = insight_container.find_all('button', class_='org-people-bar-graph-element mt2 text-align-left full-width org-people-bar-graph-element--is-selectable')
                for button in buttons:
                    info_div = button.find(class_='org-people-bar-graph-element__percentage-bar-info')
                    if info_div:
                        value = info_div.find('strong').text.strip() if info_div.find('strong') else "0"
                        key = info_div.find('span', class_='org-people-bar-graph-element__category').text.strip() if info_div.find('span', class_='org-people-bar-graph-element__category') else ""
                        if key and value:
                            people_data["Where they live"][key] = value
            logging.info(f"Scraped 'Where they live' for {company_url}: {people_data['Where they live']}")
        
        # Step 2: Click the "Next" button exactly once to load "What they do"
        try:
            next_button = driver.find_element(By.CLASS_NAME, "artdeco-pagination__button--next")
            next_button.click()
            time.sleep(random.uniform(5, 10))  # Wait for the next section to load
            logging.info(f"Clicked 'Next' button on {company_url}/people")
        except Exception as e:
            logging.warning(f"Could not click 'Next' button on {company_url}/people: {str(e)}")
        
        # Step 3: Check for "What they do" section
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        logging.info(f"Page source length after 'Next' click for {company_url}/people: {len(driver.page_source)}")
        
        what_they_do_container = soup.find(class_='org-people-bar-graph-module__current-function')
        if what_they_do_container:
            insight_container = what_they_do_container.find(class_='insight-container')
            if insight_container:
                buttons = insight_container.find_all('button', class_='org-people-bar-graph-element mt2 text-align-left full-width org-people-bar-graph-element--is-selectable')
                for button in buttons:
                    info_div = button.find(class_='org-people-bar-graph-element__percentage-bar-info')
                    if info_div:
                        value = info_div.find('strong').text.strip() if info_div.find('strong') else "0"
                        key = info_div.find('span', class_='org-people-bar-graph-element__category').text.strip() if info_div.find('span', class_='org-people-bar-graph-element__category') else ""
                        if key and value:
                            people_data["What they do"][key] = value
                logging.info(f"Scraped 'What they do' for {company_url}: {people_data['What they do']}")
        else:
            logging.warning(f"'org-people-bar-graph-module__current-function' not found for {company_url}")
        
        logging.info(f"Scraped People section for {company_url}")
    except Exception as e:
        logging.error(f"People section scrape failed for {company_url}: {str(e)}")
    return people_data

def main():
    # Login to LinkedIn
    login_to_linkedin()
    all_data = []
    
    # Read company names from data.csv
    try:
        company_df = pd.read_csv("data.csv")
        company_names = company_df["Company_Name"].tolist()
    except Exception as e:
        logging.error(f"Failed to read data.csv: {str(e)}")
        return
    
    for company in company_names:
        try:
            driver.get("https://www.linkedin.com/search/results/companies/")
            time.sleep(random.uniform(2, 5))
            search_bar = driver.find_element(By.CLASS_NAME, "search-global-typeahead__input")
            search_bar.send_keys(company)
            search_bar.send_keys(Keys.RETURN)
            time.sleep(random.uniform(2, 5))
            
            company_link = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/company/')]"))
            )
            company_url = company_link.get_attribute("href").split("?")[0]
            
            about_data = scrape_about_section(company_url)
            people_data = scrape_people_section(company_url)
            
            company_data = {
                "company_name": company,
                "Linkedin_company_url": company_url,
                **about_data,
                "What they do (dict)": json.dumps(people_data["What they do"]),
                "Where they live (dict)": json.dumps(people_data["Where they live"])
            }
            all_data.append(company_data)
            
            time.sleep(random.uniform(10, 30))  # Anti-detection delay
        except Exception as e:
            logging.error(f"Error processing {company}: {str(e)}")
            continue
    
    # Save to DataFrame and CSV
    df = pd.DataFrame(all_data)
    df.to_csv("linkedin_data_output.csv", index=False)
    logging.info("Data saved to linkedin_data_output.csv")
    
    driver.quit()

if __name__ == "__main__":
    main()