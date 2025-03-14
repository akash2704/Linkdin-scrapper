import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(filename='startupweekly_scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Chrome options for anti-detection
chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
# chrome_options.add_argument("--headless")  # Uncomment for headless mode

# Initialize WebDriver with webdriver-manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def scrape_march_tables(url):
    """
    Scrape tables for March 2025 from the Startup Weekly website.
    
    Args:
        url (str): The URL of the Startup Weekly page to scrape.
    
    Returns:
        list: A list of dictionaries containing table data for March 2025.
    """
    all_data = []
    try:
        # Navigate to the Startup Weekly page
        driver.get(url)
        time.sleep(random.uniform(5, 10))  # Wait for the page to load
        
        # Wait for the page to load and ensure the content is present
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "gh-table"))
        )
        
        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        logging.info(f"Page source length for {url}: {len(driver.page_source)}")
        
        # Find all h2 tags to identify sections
        h2_tags = soup.find_all('h2')
        target_h2 = None
        
        # Look for the h2 tag for March 2025
        for h2 in h2_tags:
            if "March 2025" in h2.text:
                target_h2 = h2
                break
        
        if not target_h2:
            logging.warning("March 2025 section not found on the page.")
            return all_data
        
        # Find the next div with class="gh-table" after the March 2025 h2
        target_div = target_h2.find_next('div', class_='gh-table')
        if not target_div:
            logging.warning("Table for March 2025 not found.")
            return all_data
        
        # Extract the table within the target div
        table = target_div.find('table')
        if not table:
            logging.warning("Table element not found in the gh-table div for March 2025.")
            return all_data
        
        # Extract headers from thead
        thead = table.find('thead')
        if not thead:
            logging.warning("Table headers (thead) not found for March 2025.")
            return all_data
        
        headers = [th.text.strip() for th in thead.find_all('th')]
        logging.info(f"Table headers for March 2025: {headers}")
        
        # Extract rows from tbody
        tbody = table.find('tbody')
        if not tbody:
            logging.warning("Table body (tbody) not found for March 2025.")
            return all_data
        
        rows = tbody.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            row_data = [cell.text.strip() for cell in cells]
            
            # Ensure the row has the same number of columns as headers
            if len(row_data) == len(headers):
                row_dict = dict(zip(headers, row_data))
                all_data.append(row_dict)
            else:
                logging.warning(f"Row data length ({len(row_data)}) does not match headers length ({len(headers)}): {row_data}")
        
        logging.info(f"Scraped {len(all_data)} rows for March 2025 from {url}")
        
    except Exception as e:
        logging.error(f"Error scraping March 2025 tables from {url}: {str(e)}")
    
    return all_data

def main():
    # URL of the Startup Weekly page (replace with the actual URL)
    startup_weekly_url = "https://startuptalky.com/indian-startups-funding-investors-data-2025/"  # Replace with the actual URL
    
    # Scrape tables for March 2025
    march_data = scrape_march_tables(startup_weekly_url)
    
    if march_data:
        # Convert to DataFrame and save to CSV
        df = pd.DataFrame(march_data)
        df.to_csv("startupweekly_march_2025.csv", index=False)
        logging.info("March 2025 data saved to startupweekly_march_2025.csv")
    else:
        logging.info("No data found for March 2025.")
    
    # Close the driver
    driver.quit()

if __name__ == "__main__":
    main()