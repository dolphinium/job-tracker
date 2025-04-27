# Updated app/services/linkedin_crawler.py
import re
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

# --- Helper function to parse relative dates ---
def parse_relative_date(date_str: str) -> Optional[datetime]:
    """Parses relative date strings like '2 days ago', '1 week ago'."""
    now = datetime.utcnow()
    date_str = date_str.lower().strip()

    try:
        if "just now" in date_str or "moments ago" in date_str:
            return now
        elif "minute" in date_str:
            minutes = int(re.search(r'\d+', date_str).group())
            return now - timedelta(minutes=minutes)
        elif "hour" in date_str:
            hours = int(re.search(r'\d+', date_str).group())
            return now - timedelta(hours=hours)
        elif "day" in date_str:
            days = int(re.search(r'\d+', date_str).group())
            return now - timedelta(days=days)
        elif "week" in date_str:
            weeks = int(re.search(r'\d+', date_str).group())
            return now - timedelta(weeks=weeks)
        elif "month" in date_str:
            months = int(re.search(r'\d+', date_str).group())
            # Approximate month as 30 days
            return now - timedelta(days=months * 30)
        elif "year" in date_str:
            years = int(re.search(r'\d+', date_str).group())
            # Approximate year as 365 days
            return now - timedelta(days=years * 365)
        else:
            # Attempt to parse as a fixed date if possible (less common on LinkedIn)
            # This part might need refinement based on actual date formats encountered
            return datetime.strptime(date_str, "%Y-%m-%d") # Example format
    except Exception:
        # If parsing fails, return None
        return None
# -------------------------------------------------

class LinkedInCrawler:
    def __init__(self):
        self.headers = {
            # Using a realistic User-Agent is important
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            # Add other headers that might help mimic a real browser visit
            'Sec-Ch-Ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin', # Or 'none' if coming from external site
            'Upgrade-Insecure-Requests': '1',
        }
        self.logger = logging.getLogger("linkedin_crawler")
        logging.basicConfig(level=logging.INFO) # Basic logging config

    def extract_job_id(self, url: str) -> Optional[str]:
        """Extract LinkedIn job ID from URL."""
        # More robust regex to handle different URL formats
        match = re.search(r'(?:jobs/view/|currentJobId=)(\d+)', url)
        if match:
            return match.group(1)
        self.logger.warning(f"Could not extract job ID from URL: {url}")
        return None

    def get_element_text(self, soup: BeautifulSoup, selector: str, attribute: Optional[str] = None) -> Optional[str]:
        """Safely find an element and return its text or attribute."""
        try:
            element = soup.select_one(selector)
            if element:
                if attribute:
                    return element.get(attribute, '').strip()
                # Handle cases where text might be split across multiple tags (e.g., within spans)
                text_parts = [part.strip() for part in element.stripped_strings]
                return ' '.join(text_parts) if text_parts else None
        except Exception as e:
            self.logger.error(f"Error extracting text with selector '{selector}': {e}")
        return None

    def get_job_description_text(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        """Safely find the job description element and extract formatted text."""
        try:
            description_div = soup.select_one(selector)
            if not description_div:
                return None

            # Attempt to preserve some formatting (paragraphs, lists)
            content = []
            for element in description_div.children:
                if isinstance(element, NavigableString):
                    text = element.strip()
                    if text:
                        content.append(text)
                elif isinstance(element, Tag):
                    if element.name == 'ul':
                        items = ["- " + li.get_text(strip=True) for li in element.find_all('li')]
                        content.append("\n".join(items))
                    elif element.name in ['p', 'div', 'br']:
                        text = element.get_text(strip=True)
                        if text:
                            content.append(text + "\n") # Add newline after paragraphs/divs
                    else:
                        text = element.get_text(strip=True)
                        if text:
                            content.append(text)

            return "\n".join(content).strip() # Join paragraphs with single newline

        except Exception as e:
            self.logger.error(f"Error extracting job description with selector '{selector}': {e}")
        return None

    async def get_job_details(self, url: str) -> Dict[str, Any]:
        """
        Crawl LinkedIn job page and extract relevant information.
        NOTE: This uses synchronous 'requests'. For high-concurrency applications,
        consider using an async HTTP client like 'httpx' or running this
        in a separate thread pool executor (e.g., FastAPI's run_in_executor).
        """
        job_id = self.extract_job_id(url)
        details = {
            "linkedin_job_id": job_id,
            "linkedin_url": url,
            "title": None,
            "company": None,
            "location": None,
            "job_description": None,
            "date_posted": None,
            # Add more fields if needed later
            # "company_url": None,
            # "seniority_level": None,
            # "employment_type": None,
            # "job_function": None,
            # "industries": None,
        }

        try:
            self.logger.info(f"Attempting to crawl LinkedIn job at: {url}")
            # Add a small delay to be polite
            # time.sleep(random.uniform(1, 3)) # Consider adding random delays

            # --- Perform the HTTP GET request ---
            # Using a session object can potentially handle cookies if needed later
            session = requests.Session()
            session.headers.update(self.headers)
            response = session.get(url, timeout=15) # Add a timeout
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

            self.logger.info(f"Successfully fetched URL: {url}. Status code: {response.status_code}")

            # --- Parse the HTML content ---
            soup = BeautifulSoup(response.text, 'html.parser')

            # --- Extract Job Details ---
            # NOTE: These selectors are based on common LinkedIn structures (as of late 2023/early 2024)
            # AND ARE LIKELY TO CHANGE. They require inspection and adjustment.

            # Title: Often in an <h1> tag within the top card
            details["title"] = self.get_element_text(soup, 'h1.top-card-layout__title, h1.job-title, .job-details-jobs-unified-top-card__job-title')

            # Company Name: Often a link within the top card or a specific span
            details["company"] = self.get_element_text(soup, 'a.topcard__org-name-link, span.job-details-jobs-unified-top-card__company-name, .topcard__flavor a')
            if not details["company"]: # Fallback selector
                 details["company"] = self.get_element_text(soup, '.job-card-container__company-name, .job-details-jobs-unified-top-card__primary-description-without-tagline a')


            # Location: Often a span within the top card
            details["location"] = self.get_element_text(soup, 'span.topcard__flavor--bullet, span.job-details-jobs-unified-top-card__bullet, .job-details-jobs-unified-top-card__primary-description-without-tagline span:first-of-type') # Take the first span if multiple

            # Job Description: Usually within a specific div
            # Look for common description container classes
            details["job_description"] = self.get_job_description_text(soup, 'div.description__text--rich, div.show-more-less-html__markup, .jobs-description-content__text')

            # Date Posted: Often relative time in a span
            date_str = self.get_element_text(soup, 'span.posted-time-ago__text, span.job-details-jobs-unified-top-card__posted-date')
            if date_str:
                details["date_posted"] = parse_relative_date(date_str)
                self.logger.info(f"Parsed relative date string '{date_str}' to {details['date_posted']}")
            else:
                 self.logger.warning(f"Could not find date posted element for {url}")


            # --- Log extracted details ---
            self.logger.info(f"Extracted details for {url}:")
            for key, value in details.items():
                 # Log shorter version of description
                 if key == "job_description" and value:
                     self.logger.info(f"  {key}: {value[:100]}...")
                 else:
                     self.logger.info(f"  {key}: {value}")

            return details

        except requests.exceptions.HTTPError as http_err:
            self.logger.error(f"HTTP error occurred while scraping {url}: {http_err} - Status Code: {http_err.response.status_code}")
            # You might want specific handling for 404 (Not Found) vs 429 (Too Many Requests) etc.
        except requests.exceptions.ConnectionError as conn_err:
            self.logger.error(f"Connection error occurred while scraping {url}: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            self.logger.error(f"Timeout error occurred while scraping {url}: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            self.logger.error(f"An ambiguous request error occurred while scraping {url}: {req_err}")
        except Exception as e:
            # Catch any other unexpected errors during scraping/parsing
            self.logger.error(f"An unexpected error occurred scraping LinkedIn job {url}: {str(e)}", exc_info=True) # Include stack trace

        # Return the partially filled or empty details dictionary in case of errors
        # Ensures the API endpoint still gets a dictionary back, even if scraping fails.
        return details