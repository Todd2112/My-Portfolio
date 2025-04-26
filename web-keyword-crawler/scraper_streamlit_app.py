import json
import os
import streamlit as st
import logging
import urllib.parse
import requests
from lxml import html
import time

# --- Logging Setup ---
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

logging.info("Logging has started")

# --- Helper Functions ---

def is_valid_url(url):
    parsed = urllib.parse.urlparse(url)
    return all([parsed.scheme, parsed.netloc])

def fetch_html(url, retries=3, backoff=2):
    if not is_valid_url(url):
        logging.error(f"Invalid URL: {url}")
        return None

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0 Safari/537.36'
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()
            logging.info(f"Fetched {url} successfully on attempt {attempt + 1}")
            return response.text
        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            time.sleep(backoff * (attempt + 1))

    logging.error(f"All retries failed for {url}")
    return None

def extract_links(html_content):
    if not isinstance(html_content, str):
        logging.warning("Invalid HTML content type")
        return []
    try:
        tree = html.fromstring(html_content)
        links = tree.xpath('//a/@href')
        return links
    except Exception as e:
        logging.error(f"Error parsing HTML: {e}")
        return []

def filter_internal_links(links, base_url):
    domain = urllib.parse.urlparse(base_url).netloc
    unique_links = set()

    for link in links:
        if link.startswith('#'):
            continue
        try:
            absolute_url = urllib.parse.urljoin(base_url, link)
            if domain in urllib.parse.urlparse(absolute_url).netloc:
                unique_links.add(absolute_url)
        except ValueError as e:
            logging.warning(f"Skipping invalid link: {link} | Error: {e}")
    
    return list(unique_links)

def crawl_site(url, depth=2, visited=None):
    if visited is None:
        visited = set()

    if depth < 0 or url in visited:
        return []

    visited.add(url)
    logging.info(f"Crawling: {url} | Depth: {depth}")

    html_content = fetch_html(url)
    if not html_content:
        return []

    links = extract_links(html_content)
    internal_links = filter_internal_links(links, url)

    results = [(url, html_content)]

    for link in internal_links:
        results.extend(crawl_site(link, depth=depth - 1, visited=visited))

    return results

def extract_title(html_content):
    try:
        tree = html.fromstring(html_content)
        title = tree.xpath('//title/text()')
        return title[0].strip() if title else "No Title"
    except Exception as e:
        logging.error(f"Error extracting title: {e}")
        return "No Title"

def extract_visible_text(html_content):
    try:
        tree = html.fromstring(html_content)

        # Remove unwanted elements
        for elem in tree.xpath('//script | //style | //noscript | //header | //footer | //meta | //head'):
            if elem.getparent() is not None:
                elem.getparent().remove(elem)

        text_content = tree.xpath('//body//text()[normalize-space()]')
        visible_text = " ".join(text_content).strip()
        return visible_text
    except Exception as e:
        logging.error(f"Error extracting visible text: {e}")
        return "Could not extract text snippet."

# --- Feedback System ---

FEEDBACK_FILE = "feedback_data.json"

def load_feedback():
    if not os.path.exists(FEEDBACK_FILE):
        return []
    with open(FEEDBACK_FILE, "r") as f:
        return json.load(f)

def add_feedback(url, text, label):
    data = load_feedback()
    data.append({
        "url": url,
        "text": text,
        "label": label
    })
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=2)

# --- Streamlit Interface ---

st.set_page_config(page_title="DEFCON Web Scraper", layout="wide")
st.title("🛰️ DEFCON Web Scraper")
st.markdown("**Choose your scraping level and input your target website.**")

start_url = st.text_input("🌐 Website to Scrape:", "https://example.com")
search_terms = st.text_input("🔍 Keywords or Phrases to Search (comma-separated):", "cybersecurity, AI, automation")

scraping_level = st.selectbox(
    "🚦 Choose Scraping Level (aka DEFCON Mode):",
    ["Fast Mode (Level 1)", "Level 2", "Level 3", "Level 4", "DEFCON 5"]
)

defcon_depths = {
    "Fast Mode (Level 1)": 1,
    "Level 2": 2,
    "Level 3": 3,
    "Level 4": 4,
    "DEFCON 5": 5
}
depth = defcon_depths[scraping_level]

if st.button("🔥 Launch Scrape"):
    with st.spinner(f"Engaging {scraping_level}... scanning {start_url}..."):
        results = crawl_site(start_url, depth=depth)

    if results:
        st.success(f"Scraped {len(results)} pages at {scraping_level} depth.")
        
        for idx, (url, html_content) in enumerate(results, 1):
            st.markdown(f"### {idx}. [Visit Page]({url})")

            try:
                text_snippet = extract_visible_text(html_content)[:500] + "..."
            except Exception as e:
                logging.error(f"Error extracting text: {e}")
                text_snippet = "Could not extract text snippet."

            st.write(text_snippet)

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"👍 That's Good {idx}", key=f"good_{idx}"):
                    add_feedback(url, text_snippet, 1)
                    st.success("Marked as relevant!")
            with col2:
                if st.button(f"👎 Not Relevant {idx}", key=f"bad_{idx}"):
                    add_feedback(url, text_snippet, 0)
                    st.info("Marked as not relevant.")
    else:
        st.warning("Nothing found. The site may be blocking bots, or try a shallower level.")
