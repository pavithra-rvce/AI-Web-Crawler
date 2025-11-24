import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType


def scrape_webiste(website: str) -> str:
    """
    Advanced scraping with anti-detection measures for production
    """
    print("launching chrome browser with anti-detection...")

    options = webdriver.ChromeOptions()
    
    # Essential options for deployment
    options.add_argument("--headless")  # Keep headless for deployment
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # Advanced anti-detection options
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-extensions")
    
    # Realistic browser behavior
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Exclude automation indicators
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)

    try:
        driver_path = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        driver = webdriver.Chrome(service=Service(driver_path), options=options)
    except Exception as e:
        print(f"Error with ChromeDriverManager: {e}")
        driver = webdriver.Chrome(options=options)

    try:
        # Execute advanced anti-detection scripts
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Remove automation traces
        driver.execute_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        """)
        
        print(f"Navigating to: {website}")
        driver.get(website)
        
        # Wait for initial load
        time.sleep(3)
        
        print("Page loaded, checking for challenges...")

        # Wait for page to load completely with longer timeout
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Check for blocking pages
        page_source = driver.page_source.lower()
        
        challenge_indicators = [
            'cloudflare', 'challenge', 'verification', 'captcha',
            'enable javascript', 'security check', 'please wait'
        ]
        
        if any(indicator in page_source for indicator in challenge_indicators):
            print("Anti-bot challenge detected, attempting to bypass...")
            
            # Wait longer and try to refresh
            time.sleep(10)
            driver.refresh()
            time.sleep(5)

        # Human-like scrolling
        print("Simulating human-like behavior...")
        
        # Multiple scroll actions with delays
        scroll_points = [0.2, 0.5, 0.8, 1.0]  # Scroll to different positions
        
        for point in scroll_points:
            driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {point});")
            time.sleep(2)
        
        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        # Final page source
        html = driver.page_source
        
        # Content validation
        if len(html.strip()) < 1000:
            print(f"Warning: Limited content retrieved ({len(html)} chars)")
            
        print(f"Successfully retrieved content: {len(html)} characters")
        return html

    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        # Return whatever content we can get
        try:
            return driver.page_source
        except:
            raise Exception(f"Scraping failed: {str(e)}")
    finally:
        driver.quit()


def extract_body_content(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""


def clean_body_content(body_content: str) -> str:
    soup = BeautifulSoup(body_content, "html.parser")

    for script_or_style in soup(["script", "style", "nav", "header", "footer"]):
        script_or_style.extract()

    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content


def split_dom_content(dom_content: str, max_lenght: int = 6000):
    return [
        dom_content[i : i + max_lenght]
        for i in range(0, len(dom_content), max_lenght)
    ]
