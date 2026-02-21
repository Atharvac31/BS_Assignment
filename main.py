from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import requests
import os
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

# ---------------- LOAD ENV ---------------- #
load_dotenv()

BROWSERSTACK_USERNAME = os.getenv("BROWSERSTACK_USERNAME")
BROWSERSTACK_ACCESS_KEY = os.getenv("BROWSERSTACK_ACCESS_KEY")

translated_titles = []

# ---------------- LOCAL DRIVER ---------------- #
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.implicitly_wait(2)

    print("✅ Local driver initialized")
    return driver

# ---------------- BROWSERSTACK DRIVER ---------------- #
def setup_browserstack_driver(capabilities):
    url = f"https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}" \
          "@hub-cloud.browserstack.com/wd/hub"

    driver = webdriver.Remote(
        command_executor=url,
        desired_capabilities=capabilities
    )

    driver.implicitly_wait(2)
    print(f"🚀 BrowserStack session started: {driver.session_id}")
    return driver

# ---------------- CAPABILITIES ---------------- #
def get_browserstack_caps():
    return [
        {
            "browserName": "Chrome",
            "browserVersion": "latest",
            "bstack:options": {
                "os": "Windows",
                "osVersion": "11",
                "sessionName": "Chrome Windows"
            }
        },
        {
            "browserName": "Firefox",
            "browserVersion": "latest",
            "bstack:options": {
                "os": "Windows",
                "osVersion": "11",
                "sessionName": "Firefox Windows"
            }
        },
        {
            "browserName": "Safari",
            "browserVersion": "latest",
            "bstack:options": {
                "os": "OS X",
                "osVersion": "Ventura",
                "sessionName": "Safari macOS"
            }
        },
        {
            "browserName": "Chrome",
            "bstack:options": {
                "deviceName": "Samsung Galaxy S22",
                "osVersion": "12.0",
                "realMobile": "true",
                "sessionName": "Samsung Galaxy"
            }
        },
        {
            "browserName": "Safari",
            "bstack:options": {
                "deviceName": "iPhone 14",
                "osVersion": "16",
                "realMobile": "true",
                "sessionName": "iPhone"
            }
        }
    ]

# ---------------- TRANSLATION ---------------- #
def translate_to_english(text):
    try:
        return GoogleTranslator(source='es', target='en').translate(text)
    except Exception as e:
        print(f"⚠️ Translation error: {e}")
        return "Translation failed"

# ---------------- NAVIGATION ---------------- #
def open_opinion_section(driver):
    driver.get("https://elpais.com/opinion/")

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
    )

    print("✅ Opinion section ready")

# ---------------- ARTICLE LINKS ---------------- #
def get_first_five_articles(driver):
    articles = driver.find_elements(By.CSS_SELECTOR, "article h2 a")
    links = []

    for article in articles:
        link = article.get_attribute("href")

        if link and link not in links:
            links.append(link)

        if len(links) == 5:
            break

    return links

# ---------------- IMAGE DOWNLOAD ---------------- #
def download_image(url, index):
    try:
        os.makedirs("images", exist_ok=True)

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)

        with open(f"images/article_{index}.jpg", "wb") as f:
            f.write(response.content)

        print(f"✅ Image saved: article_{index}.jpg")

    except Exception as e:
        print(f"ℹ️ Image download failed: {e}")

# ---------------- REQUESTS SCRAPER ---------------- #
def fetch_article_content(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "Title not found"

        paragraphs = soup.select("article p, div.a_c p")

        content = "\n".join(
            p.get_text(strip=True)
            for p in paragraphs
            if p.get_text(strip=True)
        )

        if not content:
            content = "Content not found"

        return title, content

    except Exception as e:
        print(f"❌ Requests parsing error: {e}")
        return "Title not found", "Content not found"

# ---------------- WORD ANALYSIS ---------------- #
def analyze_repeated_words(titles):
    print("\n" + "=" * 60)
    print("REPEATED WORD ANALYSIS (English Titles)")
    print("=" * 60)

    all_words = []

    for title in titles:
        words = re.findall(r"\b[a-zA-Z']+\b", title.lower())
        all_words.extend(words)

    word_counts = Counter(all_words)

    repeated = {
        word: count for word, count in word_counts.items()
        if count > 2
    }

    if repeated:
        for word, count in repeated.items():
            print(f"{word} → {count} times")
    else:
        print("No words repeated more than twice.")

# ---------------- ARTICLE SCRAPER ---------------- #
def scrape_article(driver, url, index):
    print(f"\n🔎 Scraping: {url}")

    title, content = fetch_article_content(url)

    try:
        driver.get(url)
        images = driver.find_elements(By.CSS_SELECTOR, "figure img")

        if images:
            img_url = images[0].get_attribute("src")
            if img_url:
                download_image(img_url, index)

    except Exception as e:
        print(f"ℹ️ Image issue: {e}")

    print("=" * 60)
    print(f"ARTICLE {index}")
    print("=" * 60)
    print("TITLE (Spanish):")
    print(title)

    translated_title = translate_to_english(title)
    translated_titles.append(translated_title)

    print("\nTITLE (English):")
    print(translated_title)

    print("\nCONTENT (Spanish):")
    print(content[:1000])

# ---------------- BROWSERSTACK TEST ---------------- #
def run_test(capabilities):
    driver = setup_browserstack_driver(capabilities)

    try:
        open_opinion_section(driver)
        article_links = get_first_five_articles(driver)

        for i, link in enumerate(article_links, start=1):
            scrape_article(driver, link, i)

    finally:
        driver.quit()

# ---------------- MAIN ---------------- #
def main():
    driver = setup_driver()

    try:
        open_opinion_section(driver)
        article_links = get_first_five_articles(driver)

        print(f"\nFound {len(article_links)} articles.\n")

        for i, link in enumerate(article_links, start=1):
            scrape_article(driver, link, i)

        analyze_repeated_words(translated_titles)

    finally:
        driver.quit()

    print("\n🚀 Running 5 parallel BrowserStack sessions...\n")

    caps_list = get_browserstack_caps()

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(run_test, caps_list)


if __name__ == "__main__":
    main()