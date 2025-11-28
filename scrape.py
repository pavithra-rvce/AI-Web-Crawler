import requests
from bs4 import BeautifulSoup
import time
import random

def scrape_website(website: str) -> str:
    """
    Reliable scraping using only requests + BeautifulSoup
    No external dependencies that break on Streamlit Cloud
    """
    print(f"Scraping: {website}")
    
    # Strategy 1: Try with rotating user agents
    html_content = try_scrape_with_headers(website)
    if html_content and is_valid_content(html_content):
        print("✅ Success with headers rotation")
        return html_content
    
    # Strategy 2: Try with different approach
    html_content = try_scrape_simple(website)
    if html_content and is_valid_content(html_content):
        print("✅ Success with simple approach")
        return html_content
    
    # Strategy 3: Try with delays and retries
    html_content = try_scrape_with_retry(website)
    if html_content and is_valid_content(html_content):
        print("✅ Success with retry approach")
        return html_content
    
    raise Exception("All scraping methods failed. Site may be blocking requests or unavailable.")

def try_scrape_with_headers(url: str) -> str:
    """Try scraping with proper headers and user agent rotation"""
    try:
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Check if content is HTML
        if 'text/html' in response.headers.get('content-type', ''):
            return response.text
        else:
            return None
            
    except Exception as e:
        print(f"Header rotation failed: {e}")
        return None

def try_scrape_simple(url: str) -> str:
    """Simple scraping approach with basic headers"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
        
    except Exception as e:
        print(f"Simple approach failed: {e}")
        return None

def try_scrape_with_retry(url: str, retries: int = 2) -> str:
    """Try scraping with retry logic and delays"""
    for attempt in range(retries):
        try:
            # Add delay between retries
            if attempt > 0:
                time.sleep(2)
                
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            print(f"Retry attempt {attempt + 1} failed: {e}")
            if attempt == retries - 1:
                return None

def is_valid_content(html_content: str, min_length: int = 200) -> bool:
    """Check if content is valid and not a blocking page"""
    if not html_content or len(html_content) < min_length:
        return False
    
    # Check for common blocking indicators
    blocking_indicators = [
        'access denied', 'cloudflare', 'captcha', 'security check',
        'enable javascript', 'bot detected', 'permission denied',
        'distil', 'incapsula'
    ]
    
    content_lower = html_content.lower()
    
    # If it's clearly a blocking page, consider it invalid
    blocking_keywords = [indicator for indicator in blocking_indicators if indicator in content_lower]
    if blocking_keywords:
        print(f"Blocking detected: {blocking_keywords}")
        return False
    
    return True

def extract_body_content(html_content: str) -> str:
    """Extract body content from HTML"""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        body_content = soup.body
        if body_content:
            return str(body_content)
        return html_content  # Return original if no body found
    except Exception as e:
        print(f"Error extracting body: {e}")
        return html_content

def clean_body_content(body_content: str) -> str:
    """Clean and extract text from body content"""
    try:
        soup = BeautifulSoup(body_content, "html.parser")

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside", "meta", "link"]):
            element.extract()

        # Get clean text
        cleaned_content = soup.get_text(separator="\n")
        cleaned_content = "\n".join(
            line.strip() for line in cleaned_content.splitlines() if line.strip()
        )

        return cleaned_content
    except Exception as e:
        print(f"Error cleaning content: {e}")
        return body_content

def split_dom_content(dom_content: str, max_length: int = 6000):
    """Split content into chunks for processing"""
    return [
        dom_content[i : i + max_length]
        for i in range(0, len(dom_content), max_length)
    ]
