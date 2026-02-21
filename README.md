# BrowserStack Selenium Assignment

## 📌 Overview
This project demonstrates Selenium automation, web scraping, API integration, and cross-browser execution using BrowserStack.

## ✅ Features
- Scrapes first 5 Opinion articles from El País
- Extracts Spanish titles & content
- Downloads cover images
- Translates titles to English
- Performs repeated word analysis
- Runs locally & on BrowserStack
- Executes 5 parallel BrowserStack sessions

## 🛠 Tech Stack
- Python
- Selenium
- BeautifulSoup
- Requests
- deep-translator
- BrowserStack

## ⚙️ Setup

### 1️⃣ Install dependencies
pip install -r requirements.txt

### 2️⃣ Create `.env` file
BROWSERSTACK_USERNAME=your_username
BROWSERSTACK_ACCESS_KEY=your_access_key

## ▶️ Run Locally
python main.py

## ☁️ Run on BrowserStack
browserstack-sdk python main.py

## 🌐 BrowserStack Execution
### Tests run in parallel across:
  
✔ Chrome (Windows)
✔ Firefox (Windows)
✔ Safari (macOS)
✔ Samsung Galaxy
✔ iPhone

## 👨‍💻 Author
Atharva Chourikar
