# scrape.py
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time


def scrape_webiste(website: str) -> str:
    """
    Open the given website with Chrome via undetected_chromedriver
    and return the full HTML after the page has finished loading.
    """
    print("launching chrome browser....")

    options = uc.ChromeOptions()
    options.headless = True  # Run without GUI
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = uc.Chrome(options=options)

    try:
        driver.get(website)
        print("page loaded")

        # Wait until <body> is present
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Scroll the page slowly to load dynamic content
        last_height = driver.execute_script("return document.body.scrollHeight")

        for _ in range(5):  # adjust number of scrolls if needed
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # wait for new content to load

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Grab full page source
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


def split_dom_content(dom_content: str, max_lenght: int = 6000):
    return [
        dom_content[i: i + max_lenght]
        for i in range(0, len(dom_content), max_lenght)
    ]
