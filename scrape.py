import requests
from bs4 import BeautifulSoup
import time
import streamlit as st
from requests_html import HTMLSession
import random

def scrape_website(website: str) -> str:
    """
    Permanent scraping solution without ChromeDriver dependencies
    Uses multiple fallback strategies for maximum reliability
    """
    print(f"Scraping: {website}")
    
    # Strategy 1: Try requests-html with JavaScript rendering
    html_content = try_requests_html(website)
    if html_content and is_valid_content(html_content):
        print("✅ Success with requests-html + JavaScript")
        return html_content
    
    # Strategy 2: Try requests-html without JavaScript
    html_content = try_requests_html(website, render_js=False)
    if html_content and is_valid_content(html_content):
        print("✅ Success with requests-html (no JavaScript)")
        return html_content
    
    # Strategy 3: Try direct requests with proper headers
    html_content = try_direct_requests(website)
    if html_content and is_valid_content(html_content):
        print("✅ Success with direct requests")
        return html_content
    
    # Strategy 4: Final fallback - selenium only if absolutely necessary
    try:
        html_content = try_selenium_fallback(website)
        if html_content and is_valid_content(html_content):
            print("✅ Success with Selenium fallback")
            return html_content
    except Exception as e:
        print(f"Selenium fallback also failed: {e}")
    
    raise Exception("All scraping methods failed. Site may be blocking requests.")

def try_requests_html(url: str, render_js: bool = True) -> str:
    """Try requests-html approach"""
    try:
        session = HTMLSession()
        
        # Rotating user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = session.get(url, headers=headers, timeout=30)
        
        if render_js:
            # Render JavaScript with retry logic
            try:
                response.html.render(timeout=20, sleep=2)
            except:
                # If JavaScript rendering fails, continue with basic HTML
                print("JavaScript rendering failed, using basic HTML")
        
        return response.html.html
        
    except Exception as e:
        print(f"requests-html failed: {e}")
        return None

def try_direct_requests(url: str) -> str:
    """Try direct requests approach"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
        
    except Exception as e:
        print(f"Direct requests failed: {e}")
        return None

def try_selenium_fallback(url: str) -> str:
    """
    Selenium as LAST RESORT only - with maximum compatibility
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Multiple initialization strategies
        try:
            # Strategy 1: Use system Chrome
            driver = webdriver.Chrome(options=chrome_options)
        except:
            # Strategy 2: Use webdriver-manager
            driver_path = ChromeDriverManager().install()
            driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        
        driver.get(url)
        time.sleep(3)
        content = driver.page_source
        driver.quit()
        return content
        
    except Exception as e:
        print(f"Selenium fallback failed: {e}")
        return None

def is_valid_content(html_content: str, min_length: int = 100) -> bool:
    """Check if content is valid and not a blocking page"""
    if not html_content or len(html_content) < min_length:
        return False
    
    # Check for common blocking indicators
    blocking_indicators = [
        'access denied', 'cloudflare', 'captcha', 'security check',
        'enable javascript', 'bot detected', 'permission denied'
    ]
    
    content_lower = html_content.lower()
    
    # If it's clearly a blocking page, consider it invalid
    if any(indicator in content_lower for indicator in blocking_indicators):
        return False
    
    return True

def extract_body_content(html_content: str) -> str:
    """Extract body content from HTML"""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        body_content = soup.body
        if body_content:
            return str(body_content)
        return html_content  # Return original if no body found
    except:
        return html_content

def clean_body_content(body_content: str) -> str:
    """Clean and extract text from body content"""
    try:
        soup = BeautifulSoup(body_content, "html.parser")

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
            element.extract()

        # Get clean text
        cleaned_content = soup.get_text(separator="\n")
        cleaned_content = "\n".join(
            line.strip() for line in cleaned_content.splitlines() if line.strip()
        )

        return cleaned_content
    except:
        return body_content

def split_dom_content(dom_content: str, max_length: int = 6000):
    """Split content into chunks for processing"""
    return [
        dom_content[i : i + max_length]
        for i in range(0, len(dom_content), max_length)
    ]
