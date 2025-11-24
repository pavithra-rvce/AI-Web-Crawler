import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from webdriver_manager.chrome import ChromeDriverManager  # Add this import


def scrape_webiste(website: str) -> str:
    """
    Open the given website with Chrome via Selenium and return the full HTML
    after the page has finished loading (as much as Selenium can see).

    It also scrolls the page to trigger some dynamic / lazy-loaded content.
    """
    print("launching chrome browser....")

    # Remove the chrome_driver_path line and use ChromeDriverManager instead
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")   # Add headless for deployment
    options.add_argument("--no-sandbox")  # Add for deployment
    options.add_argument("--disable-dev-shm-usage")  # Add for deployment

    # Use ChromeDriverManager to automatically handle driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(website)
        print("page loaded")

        # 1️⃣ Wait until <body> is present
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 2️⃣ Scroll the page slowly to load dynamic content
        last_height = driver.execute_script("return document.body.scrollHeight")

        for _ in range(5):  # you can increase loops if you want more scrolling
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # wait for new content to load

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # no more new content
                break
            last_height = new_height

        # 3️⃣ Now grab full page source
        html = driver.page_source
        return html

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

    for script_or_style in soup(["script", "style"]):
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
