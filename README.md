# Indeed Job Data Scraping

This repository contains a Python script to scrape job listings from Indeed.com and analyze the job requirements for Data Analyst positions. The script fetches job listings, extracts job requirements, analyzes the frequency of various skills and requirements, saves the data to a CSV file, and visualizes the most common requirements.

## Features

- Fetch job listings from Indeed.com
- Extract job requirements from job postings
- Analyze the frequency of job requirements
- Save job requirements to a CSV file
- Visualize the most common job requirements

## Requirements

- Python 3.x
- Requests
- BeautifulSoup4
- Matplotlib

You can install the required libraries using:

pip install requests beautifulsoup4 matplotlib

## Usage
1. Clone the repository:

git clone https://github.com/yourusername/indeed-job-data-scraping.git
cd indeed-job-data-scraping

2. Run the script:

python indeed_job_data_scraping.py

The script will perform the following steps:

Fetch job listings from Indeed.com for Data Analyst positions.
Extract job requirements from the job listings.
Analyze the frequency of job requirements.
Save the job requirements to a CSV file.
Display a bar chart of the most common job requirements.

## Functions
fetch_job_listings(url): Fetches and parses job listings from Indeed.
extract_job_requirements(soup): Extracts job requirements from parsed HTML.
analyze_requirements(requirements): Processes and analyzes job requirements.
save_to_csv(requirements): Saves job requirements to a CSV file.
visualize_requirements(word_freq, num_words=20): Visualizes the most common job requirements.

## Example
Example CSV output file name format:

job_requirements_YYYYMMDD_HHMMSS.csv

Example bar chart of the most common job requirements:
![image](https://github.com/JaCar-868/Indeed_Job_Scraping_Analysis/assets/172214426/0d1403de-1c54-479f-960f-0873687c51c5)


## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any changes or improvements.

## License
This project is licensed under the MIT License; see the [LICENSE](https://github.com/JaCar-868/Disease-Progression/blob/main/LICENSE) file for details.
