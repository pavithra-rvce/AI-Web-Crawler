# scrape.py
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc

def scrape_website(website: str) -> str:
    """
    Open the given website with Chrome via undetected-chromedriver and return the fully rendered HTML.
    """

    print("Launching Chrome browser...")

    options = uc.ChromeOptions()
    options.headless = True  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    # Launch Chrome
    driver = uc.Chrome(version_main=114, options=options)


    try:
        driver.get(website)
        print("Page loaded")

        # Wait a few seconds for dynamic content to load
        time.sleep(5)

        # Scroll slowly to trigger lazy loading
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        html = driver.page_source
        return html

    finally:
        driver.quit()


def extract_body_content(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    return str(body_content) if body_content else ""


def clean_body_content(body_content: str) -> str:
    soup = BeautifulSoup(body_content, "html.parser")
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )
    return cleaned_content


def split_dom_content(dom_content: str, max_length: int = 6000):
    return [
        dom_content[i : i + max_length]
        for i in range(0, len(dom_content), max_length)
    ]
