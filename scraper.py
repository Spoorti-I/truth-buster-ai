import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

class ArticleScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_article(self, url: str) -> Dict[str, Any]:
        """
        Scrapes headline, body text, meta description, and domain info from article URL.
        """
        try:
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc or parsed_url.path

            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url

            response = requests.get(url, headers=self.headers, timeout=8)
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: Unable to reach website.",
                    "domain": domain,
                    "headline": "",
                    "text": ""
                }

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title / headline
            headline = ""
            if soup.find('h1'):
                headline = soup.find('h1').get_text(strip=True)
            elif soup.title:
                headline = soup.title.get_text(strip=True)

            # Extract meta description
            meta_desc = ""
            meta = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
            if meta and meta.get('content'):
                meta_desc = meta['content']

            # Extract body paragraphs
            paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if len(p.get_text(strip=True)) > 25]
            body_text = "\n\n".join(paragraphs[:8])

            combined_text = f"{meta_desc}\n\n{body_text}".strip()

            return {
                "success": True,
                "domain": domain,
                "headline": headline or "Web Article Title",
                "text": combined_text or meta_desc or headline,
                "error": None
            }

        except Exception as e:
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc or "Unknown Domain"
            return {
                "success": False,
                "error": f"Could not scrape URL: {str(e)}",
                "domain": domain,
                "headline": "",
                "text": ""
            }
