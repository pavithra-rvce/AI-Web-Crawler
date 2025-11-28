import requests
from bs4 import BeautifulSoup
import time
import random
import re

def scrape_website(website: str) -> str:
    """
    Enhanced scraping with better anti-block measures
    """
    print(f"🔍 Scraping: {website}")
    
    # Validate URL format
    if not website.startswith(('http://', 'https://')):
        website = 'https://' + website
    
    strategies = [
        try_scrape_stealth,
        try_scrape_with_retry,
        try_scrape_simple,
        try_scrape_minimal
    ]
    
    for i, strategy in enumerate(strategies, 1):
        print(f"🔄 Trying strategy {i}/{len(strategies)}...")
        html_content = strategy(website)
        
        if html_content and is_valid_content(html_content):
            print(f"✅ Success with strategy {i}")
            return html_content
        
        time.sleep(1)  # Brief delay between strategies
    
    # Final attempt with error details
    return try_final_attempt(website)

def try_scrape_stealth(url: str) -> str:
    """Stealth scraping with realistic browser headers"""
    try:
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Add random delay to mimic human behavior
        time.sleep(random.uniform(1, 3))
        
        response = requests.get(
            url, 
            headers=headers, 
            timeout=20,
            allow_redirects=True
        )
        response.raise_for_status()
        
        return response.text
            
    except Exception as e:
        print(f"❌ Stealth approach failed: {e}")
        return None

def try_scrape_with_retry(url: str) -> str:
    """Retry strategy with exponential backoff"""
    for attempt in range(3):
        try:
            if attempt > 0:
                delay = 2 ** attempt  # Exponential backoff: 2, 4 seconds
                print(f"⏳ Retry {attempt + 1}/3 after {delay}s delay...")
                time.sleep(delay)
                
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Retry {attempt + 1} failed: {e}")
            if attempt == 2:  # Last attempt
                return None

def try_scrape_simple(url: str) -> str:
    """Simple approach for basic sites"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Bot)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
        
    except Exception as e:
        print(f"❌ Simple approach failed: {e}")
        return None

def try_scrape_minimal(url: str) -> str:
    """Minimal headers approach"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
        
    except Exception as e:
        print(f"❌ Minimal approach failed: {e}")
        return None

def try_final_attempt(url: str) -> str:
    """Final attempt with detailed error information"""
    try:
        response = requests.get(url, timeout=5)
        status_code = response.status_code
        
        if status_code == 403:
            raise Exception(f"Access Forbidden (403). Website is blocking our requests.")
        elif status_code == 404:
            raise Exception(f"Page not found (404). Please check the URL.")
        elif status_code == 429:
            raise Exception(f"Too many requests (429). Website rate limiting detected.")
        elif status_code >= 500:
            raise Exception(f"Server error ({status_code}). Website may be down.")
        else:
            response.raise_for_status()
            
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if "SSL" in error_msg:
            raise Exception("SSL certificate error. Try http:// instead of https://")
        elif "Connection" in error_msg:
            raise Exception("Connection failed. Website may be down or unreachable.")
        elif "Timeout" in error_msg:
            raise Exception("Request timeout. Website is taking too long to respond.")
        else:
            raise Exception(f"Website unavailable: {error_msg}")
    
    raise Exception("All scraping methods failed. The website may have strong anti-bot protection.")

def is_valid_content(html_content: str, min_length: int = 150) -> bool:
    """Enhanced content validation"""
    if not html_content or len(html_content.strip()) < min_length:
        return False
    
    content_lower = html_content.lower()
    
    # Blocking indicators
    blocking_indicators = [
        'access denied', 'cloudflare', 'captcha', 'security check',
        'enable javascript', 'bot detected', 'permission denied',
        'distil', 'incapsula', 'blocked', 'forbidden'
    ]
    
    # Check for blocking pages
    for indicator in blocking_indicators:
        if indicator in content_lower:
            print(f"🚫 Blocking detected: {indicator}")
            return False
    
    # Check for actual content indicators
    content_indicators = [
        '<body', '<div', '<p', '<span', '<h1', '<h2', '<article', '<main'
    ]
    
    has_content = any(indicator in content_lower for indicator in content_indicators)
    
    return has_content

def extract_body_content(html_content: str) -> str:
    """Extract body content from HTML"""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style", "noscript"]):
            script.extract()
            
        body_content = soup.body
        if body_content:
            return str(body_content)
        return html_content
    except Exception as e:
        print(f"⚠️ Error extracting body: {e}")
        return html_content

def clean_body_content(body_content: str) -> str:
    """Clean and extract text from body content"""
    try:
        soup = BeautifulSoup(body_content, "html.parser")

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside", "meta", "link", "button", "form"]):
            element.extract()

        # Get clean text with better formatting
        cleaned_content = soup.get_text(separator="\n")
        
        # Clean up extra whitespace but preserve paragraph structure
        lines = [line.strip() for line in cleaned_content.splitlines() if line.strip()]
        cleaned_content = "\n".join(lines)

        return cleaned_content
    except Exception as e:
        print(f"⚠️ Error cleaning content: {e}")
        return body_content

def split_dom_content(dom_content: str, max_length: int = 6000):
    """Split content into chunks for processing"""
    return [
        dom_content[i : i + max_length]
        for i in range(0, len(dom_content), max_length)
    ]
