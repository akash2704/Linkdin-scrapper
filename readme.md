# LinkedIn Company Data Scraper

This is a Python-based web scraper designed to extract detailed company information from LinkedIn, including data from the About section (e.g., Overview, Industry, Headquarters, Founded, Specialties, Website) and the People section (e.g., "Where they live" and "What they do"). The project uses Selenium for dynamic web navigation and BeautifulSoup for efficient HTML parsing. Credentials are managed securely via a `.env` file.

## Features
- Automates login to LinkedIn using credentials from a `.env` file.
- Scrapes comprehensive company data from the About and People sections.
- Handles pagination and "Show More" buttons to retrieve all available data.
- Saves results to a CSV file (`linkedin_data_output.csv`).
- Includes detailed logging in `linkedin_scraper.log` for debugging.

## Requirements
- **Python**: 3.12
- **Poetry**: For dependency management and virtual environment setup

### Dependencies
- `selenium==4.29.0` (for web automation)
- `pandas==2.2.3` (for CSV handling)
- `webdriver-manager==4.0.2` (for automatic ChromeDriver installation)
- `beautifulsoup4==4.12.3` (for HTML parsing)
- `python-dotenv==1.0.1` (for loading environment variables)

## Setup Instructions

### 1. Clone the Repository
If you have a GitHub repository set up, clone it:
```
git clone https://github.com/akash2704/Linkdin-scrapper.git
cd linkdin-scrapper
```
### Set Up a Virtual Environment
Initialize and activate a virtual environment using Poetry:
```
poetry init  # If pyproject.toml doesn't exist yet
poetry env use 3.12
poetry shell
```
### 3. Install Dependencies
Install the required packages:
```
poetry install --no-root
```
### 5. Create a .env File
Create a .env file to store your LinkedIn credentials securely. Example content:
```
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-secure-password
```
- Replace your-email@example.com and your-secure-password with your actual LinkedIn credentials.
- Important: Do not commit the .env file to version control. Add it to .gitignore (create a .gitignore file with .env if not present).
### 6. Install ChromeDriver
The script uses webdriver-manager to automatically install ChromeDriver compatible with your installed Google Chrome version (e.g., version 133 or 134 as of March 2025). Ensure Google Chrome is installed on your system.
## Usage Guidelines
### 1. Run the Script
Execute the scraper from the project directory:
```
poetry run linkedin-scrapper.py
```
### 2. Output
The scraped data will be saved to linkedin_data_output.csv in the project directory.
Detailed logs, including errors or warnings, are written to linkedin_scraper.log.
### 3. Expected Output Format
The CSV will contain columns like:
| company_name | linkedin_company_url            | overview                     | website        | industry    | company_size | headquarters   | founded | specialties          | what_they_do_(dict)                 | where_they_live_(dict)              |
|--------------|---------------------------------|--------------------------------|----------------|-------------|--------------|----------------|---------|-----------------------|-------------------------------------|-------------------------------------|
| MobiKwik     | https://www.linkedin.com/...    | Fintech platform...          | mobikwik.com   | Financial Services | 147K followers | Gurugram, Haryana | 2009    | Payments, Fintech     | {"Engineer": "X", "Manager": "Y"}   | {"India": "1,308", ...}             |
### 4. Troubleshooting
#### No Output
- Verify `data.csv` exists and contains valid company names.
- Check `linkedin_scraper.log` for errors (e.g., login failures or page load issues).

#### About Section Empty
- Ensure the About page loads correctly. Inspect the HTML (F12 on `https://www.linkedin.com/company/mobikwik/about/`) if needed.
- If the section isn’t found, the selectors in `scrape_about_section` may need adjustment.

#### People Section Issues
- If "What they do" or "Where they live" is missing, confirm the pagination button (`artdeco-pagination__button--next`) is clicked and the section loads.
- Add a scroll if necessary
### Contributing
Contributions are welcome! Please submit issues or pull requests on the GitHub repository. Suggestions for improving selectors, error handling, or performance are encouraged.
### Contact
#!/bin/bash

echo "Contact Information"
echo "-------------------"
echo "For questions or support, contact Akash at <a href=\"mailto:akashkallai27@gmail.com\">akashkallai27@gmail.com</a>