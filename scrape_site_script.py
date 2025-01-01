from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin, urlparse
import os
import time
from bs4 import BeautifulSoup
import tldextract 

visited_urls = set()

def setup_driver():
    """
    Setting up Selenium WebDriver.
    """
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = Service(executable_path="C:\\Users\\artem\\Downloads\\chromedriver\\chromedriver-win64\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_site(driver, base_url, domain, output_dir="scraped_data", combined_file="combined_text.txt", max_depth=3, current_depth=0):
    """
    Recursively visit all pages of the site and save text information.
    """
    if base_url in visited_urls or current_depth > max_depth:
        return

    visited_urls.add(base_url)
    print(f"Visiting: {base_url}")

    try:
        driver.get(base_url)
        time.sleep(2) 
        page_source = driver.page_source
    except Exception as e:
        print(f"Error accessing {base_url}: {e}")
        return

    soup = BeautifulSoup(page_source, "html.parser")

    page_text = save_page_text(base_url, soup, output_dir)

    save_to_combined_file(base_url, page_text, combined_file)

    for link in soup.find_all("a", href=True):
        href = link["href"]
        full_url = urljoin(base_url, href)
        if is_valid_url(full_url) and is_same_domain(full_url, domain):
            scrape_site(driver, full_url, domain, output_dir, combined_file, max_depth, current_depth + 1)

def save_page_text(url, soup, output_dir):
    """
    Save the text from the page to a file and return the text.
    """
    filename = os.path.join(output_dir, f"{hash(url)}.txt")

    page_text = soup.get_text(separator="\n", strip=True)

    os.makedirs(output_dir, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"URL: {url}\n\n{page_text}")

    print(f"Text saved: {filename}")
    return page_text

def save_to_combined_file(url, page_text, combined_file):
    """
    Append the page text to the combined file.
    """
    with open(combined_file, "a", encoding="utf-8") as file:
        file.write(f"\n\n=== URL: {url} ===\n\n{page_text}")

def is_valid_url(href):
    """
    Check if the link is processable.
    """
    parsed = urlparse(href)
    return parsed.scheme in {"http", "https", ""}

def is_same_domain(url, domain):
    """
    Check if the URL belongs to the specified domain.
    """
    parsed_domain = tldextract.extract(domain)
    parsed_url = tldextract.extract(url)
    return parsed_domain.domain == parsed_url.domain and parsed_domain.suffix == parsed_url.suffix

if __name__ == "__main__":
    start_url = "https://www.udelphi.com/" 
    domain = "www.udelphi.com"

    driver = setup_driver()
    try:
        scrape_site(driver, start_url, domain)
    finally:
        driver.quit()
