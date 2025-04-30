"""
indeed_job_data_scraping.py: Scrape Indeed job listings for a given role and location,
analyze the most common skills/requirements, and visualize them interactively with Plotly.
"""

import argparse
import concurrent.futures
import logging
import random
import re
import time
from collections import Counter
from datetime import datetime
from typing import List, Tuple

import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup

# Constants
BASE_URL = "https://www.indeed.com/jobs"
STOP_WORDS = {
    'the', 'and', 'for', 'with', 'that', 'this', 'from', 'are', 'was', 'were',
    'will', 'have', 'has', 'had', 'but', 'not', 'you', 'your', 'all', 'any',
    'can', 'their', 'they', 'our', 'us', 'use', 'using', 'required', 'requirements'
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def fetch_job_listings(url: str, session: requests.Session, max_retries: int = 3) -> BeautifulSoup:
    """
    Fetch HTML content for a given URL and return a BeautifulSoup object.
    Retries up to `max_retries` times with exponential backoff.
    """
    for attempt in range(1, max_retries + 1):
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            wait = 2 ** attempt
            logging.warning(f"Request failed ({e}), retrying in {wait}s...")
            time.sleep(wait)
    logging.error(f"Failed to fetch URL after {max_retries} attempts: {url}")
    return BeautifulSoup("", 'html.parser')


def extract_job_requirements(soup: BeautifulSoup) -> List[str]:
    """
    Parse job cards in the BeautifulSoup object and extract requirement snippets.
    """
    requirements = []
    for card in soup.find_all('div', class_='job_seen_beacon'):
        snippet = card.find('div', class_='job-snippet')
        if snippet:
            text = snippet.get_text(separator=' ').strip()
            requirements.append(text)
    return requirements


def analyze_requirements(requirements: List[str]) -> Counter:
    """
    Analyze word frequency in the list of requirement strings, filtering out stop words.
    """
    counter = Counter()
    pattern = re.compile(r'\b\w{3,}\b')
    for text in requirements:
        words = pattern.findall(text.lower())
        filtered = [w for w in words if w not in STOP_WORDS]
        counter.update(filtered)
    return counter


def save_data(requirements: List[str], word_freq: Counter, output_prefix: str) -> Tuple[str, str]:
    """
    Save raw requirements and word frequencies to CSV files.
    Returns filenames of saved CSVs.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    req_df = pd.DataFrame(requirements, columns=['requirement'])
    req_filename = f"{output_prefix}_requirements_{timestamp}.csv"
    req_df.to_csv(req_filename, index=False)

    freq_df = pd.DataFrame(word_freq.most_common(), columns=['word', 'count'])
    freq_filename = f"{output_prefix}_word_freq_{timestamp}.csv"
    freq_df.to_csv(freq_filename, index=False)

    logging.info(f"Saved requirements to {req_filename}")
    logging.info(f"Saved word frequencies to {freq_filename}")
    return req_filename, freq_filename


def visualize_requirements(word_freq: Counter, num_words: int = 20) -> None:
    """
    Create an interactive horizontal bar chart of the most common words using Plotly.
    """
    most_common = word_freq.most_common(num_words)
    if not most_common:
        logging.warning("No data to visualize.")
        return
    words, counts = zip(*most_common)
    df = pd.DataFrame({'word': words, 'count': counts})
    fig = px.bar(
        df,
        x='count',
        y='word',
        orientation='h',
        title='Top Indeed Job Requirement Keywords',
        labels={'count': 'Frequency', 'word': 'Keyword'}
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    fig.show()


def build_page_urls(query: str, location: str, pages: int, per_page: int = 10) -> List[str]:
    """
    Construct Indeed search URLs for pagination.
    """
    urls = []
    for page in range(pages):
        start = page * per_page
        params = {'q': query, 'l': location, 'start': start}
        req = requests.Request('GET', BASE_URL, params=params).prepare()
        urls.append(req.url)
    return urls


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Indeed Job Scraper and Analyzer")
    parser.add_argument('--query', '-q', type=str, default='data analyst', help='Job search query')
    parser.add_argument('--location', '-l', type=str, default='', help='Job location')
    parser.add_argument('--pages', '-p', type=int, default=1, help='Number of pages to scrape')
    parser.add_argument('--output', '-o', type=str, default='indeed_data', help='Output file prefix')
    parser.add_argument('--delay', '-d', type=float, default=1.0, help='Base delay between requests (seconds)')
    parser.add_argument('--workers', '-w', type=int, default=5, help='Number of concurrent workers')
    return parser.parse_args()


def main() -> None:
    """
    Main entry point: orchestrates scraping, analysis, saving, and visualization.
    """
    args = parse_args()
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
    })

    urls = build_page_urls(args.query, args.location, args.pages)
    all_requirements: List[str] = []

    # Fetch pages concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_url = {executor.submit(fetch_job_listings, url, session): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                soup = future.result()
            except Exception as e:
                logging.error(f"Error fetching {url}: {e}")
                continue
            reqs = extract_job_requirements(soup)
            all_requirements.extend(reqs)
            # rate limit between completed tasks
            time.sleep(args.delay + random.uniform(0, args.delay))

    if not all_requirements:
        logging.warning("No job requirements found. Exiting.")
        return

    word_freq = analyze_requirements(all_requirements)
    save_data(all_requirements, word_freq, args.output)
    visualize_requirements(word_freq, num_words=20)


if __name__ == '__main__':
    main()
