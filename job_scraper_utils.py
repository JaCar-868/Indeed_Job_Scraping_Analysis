import time
import pandas as pd
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def configure_webdriver(headless: bool = True) -> webdriver.Chrome:
    """
    Initializes and returns a Chrome WebDriver with optional headless mode.
    """
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver


def search_jobs(driver: webdriver.Chrome, base_url: str, job_position: str,
                job_location: str, date_posted: int = 7) -> None:
    """
    Navigates to the Indeed search results page for the given position and location,
    filtering by postings within the last `date_posted` days.
    """
    query = urllib.parse.quote(job_position)
    location = urllib.parse.quote(job_location)
    url = f"{base_url}/jobs?q={query}&l={location}&fromage={date_posted}"
    driver.get(url)
    time.sleep(2)  # allow page to load


def scrape_job_data(driver: webdriver.Chrome, base_url: str) -> pd.DataFrame:
    """
    Scrapes the current search results page for job details and returns a DataFrame.
    Columns: Title, Company, Location, Summary, Link
    """
    jobs = []
    # Indeed uses <a class="tapItem"> for each job card
    cards = driver.find_elements(By.CSS_SELECTOR, 'a.tapItem')
    for card in cards:
        try:
            title = card.find_element(By.CSS_SELECTOR, 'h2.jobTitle').text.strip()
        except:
            title = ''
        try:
            company = card.find_element(By.CSS_SELECTOR, 'span.companyName').text.strip()
        except:
            company = ''
        try:
            location = card.find_element(By.CSS_SELECTOR, 'div.companyLocation').text.strip()
        except:
            location = ''
        try:
            summary = card.find_element(By.CSS_SELECTOR, 'div.job-snippet').text.replace("\n", " ").strip()
        except:
            summary = ''
        try:
            link = card.get_attribute('href')
        except:
            link = None
        jobs.append({
            'Title': title,
            'Company': company,
            'Location': location,
            'Summary': summary,
            'Link': link
        })
    return pd.DataFrame(jobs)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the scraped DataFrame by dropping duplicates and null links,
    then resetting the index.
    """
    df = df.drop_duplicates(subset=['Link'])
    df = df.dropna(subset=['Link'])
    df = df.reset_index(drop=True)
    return df