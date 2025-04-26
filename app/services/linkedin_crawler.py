import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, Any, Optional

class LinkedInCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    
    def extract_job_id(self, url: str) -> Optional[str]:
        """Extract LinkedIn job ID from URL."""
        match = re.search(r'jobs/view/(\d+)', url)
        if match:
            return match.group(1)
        return None
    
    async def get_job_details(self, url: str) -> Dict[str, Any]:
        """
        Crawl LinkedIn job page and extract relevant information.
        
        Note: This is a simplified version and may need adjustments
        based on LinkedIn's actual structure and any anti-scraping measures.
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract job title
            job_title_elem = soup.select_one('.top-card-layout__title')
            job_title = job_title_elem.get_text(strip=True) if job_title_elem else None
            
            # Extract company name
            company_elem = soup.select_one('.topcard__org-name-link')
            company = company_elem.get_text(strip=True) if company_elem else None
            
            # Extract location
            location_elem = soup.select_one('.topcard__flavor--bullet')
            location = location_elem.get_text(strip=True) if location_elem else None
            
            # Extract job description
            description_elem = soup.select_one('.description__text')
            description = description_elem.get_text(strip=True) if description_elem else None
            
            # Extract date posted (this is approximate as LinkedIn usually shows relative time)
            date_elem = soup.select_one('.posted-time-ago__text')
            date_posted = None
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                # This would need parsing logic based on the format LinkedIn uses
                # For now, just use current date
                date_posted = datetime.utcnow()
            
            job_id = self.extract_job_id(url)
            
            return {
                "linkedin_job_id": job_id,
                "title": job_title,
                "company": company,
                "location": location,
                "job_description": description,
                "date_posted": date_posted,
                "linkedin_url": url
            }
            
        except Exception as e:
            print(f"Error scraping LinkedIn job: {str(e)}")
            # Return minimal information
            return {
                "linkedin_job_id": self.extract_job_id(url),
                "linkedin_url": url
            }