import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from collections import Counter
import re
import csv
from datetime import datetime

# Function to fetch and parse job listings from Indeed
def fetch_job_listings(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

# Function to extract job requirements from parsed HTML
def extract_job_requirements(soup):
    job_requirements = []
    for job_card in soup.find_all('div', class_='job_seen_beacon'):
        description = job_card.find('div', class_='job-snippet').get_text(separator=' ').strip()
        job_requirements.append(description)
    return job_requirements

# Function to process and analyze job requirements
def analyze_requirements(requirements):
    all_requirements = ' '.join(requirements)
    # Use regex to find all words
    words = re.findall(r'\b\w+\b', all_requirements.lower())
    # Use Counter to count word frequencies
    word_freq = Counter(words)
    return word_freq

# Function to save job requirements to a CSV file
def save_to_csv(requirements):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"job_requirements_{timestamp}.csv"
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Job Requirements"])
        for requirement in requirements:
            writer.writerow([requirement])
    print(f"Job requirements saved to {filename}")

# Function to visualize the most common requirements
def visualize_requirements(word_freq, num_words=20):
    common_words = word_freq.most_common(num_words)
    words, counts = zip(*common_words)
    
    plt.figure(figsize=(12, 8))
    plt.bar(words, counts, color='skyblue')
    plt.xlabel('Skills and Requirements')
    plt.ylabel('Frequency')
    plt.title('Most Common Skills and Requirements for Data Analysts')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Main function to run the steps
def main():
    url = "https://www.indeed.com/jobs?q=data+analyst&l="  # URL for data analyst job listings
    soup = fetch_job_listings(url)
    job_requirements = extract_job_requirements(soup)
    word_freq = analyze_requirements(job_requirements)
    save_to_csv(job_requirements)
    visualize_requirements(word_freq)

if __name__ == "__main__":
    main()