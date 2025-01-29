from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json
import os

visited = set()
data_content = {}  # Dictionary to store {data-link: content}

def scrape_with_content(base_url, driver):
    if base_url in visited:
        return
    visited.add(base_url)

    try:
        # Load the page with Selenium
        driver.get(base_url)
        time.sleep(2)  # Wait for the page to load dynamically
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract data-link attributes and their content
        elements = soup.find_all(attrs={'data-link': True})
        for el in elements:
            data_link = el['data-link']
            if data_link.startswith("#"):
                data_link = urljoin(base_url, data_link)
            content = el.get_text(separator="\n", strip=True)
            data_content[data_link] = content

        # Find internal links and scrape recursively
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                scrape_with_content(full_url, base_url, driver)
    except Exception as e:
        print(f"Error scraping {base_url}: {e}")

if __name__ == "__main__":
    # Setup Selenium WebDriver with headless option
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    # Define the starting URL
    start_url = 'https://www.udelphi.com/'

    try:
        # Start scraping
        scrape_with_content(start_url, driver)
    finally:
        driver.quit()

    # Define the output file path
    output_dir = './data'
    os.makedirs(output_dir, exist_ok=True) 
    output_file = os.path.join(output_dir, 'data_links_with_content.json')

    # Save the data to a JSON file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data_content, file, ensure_ascii=False, indent=4)

    # Print summary
    print(f"Scraping complete. Found {len(data_content)} data-links.")
    print(f"Data saved to {output_file}")
