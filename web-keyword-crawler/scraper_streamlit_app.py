# Core functionality 
import re 
import time 
import urllib.parse 
import requests 

# HTML parsing
from lxml import html 

import streamlit as st
import io
import logging 

# Set up logging 
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

logging.info("Logging has started")

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
    
    return list(unique_links)  # Convert back to list for consistency

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

# --- Streamlit Interface ---

st.title("🌐 Simple Recursive Web Crawler")
st.markdown("Crawls internal links from a starting URL up to a specified depth.")

# User Inputs
start_url = st.text_input("Enter a URL to start crawling:", "https://example.com")
max_depth = st.slider("Crawl Depth", min_value=1, max_value=5, value=2)

if st.button("Start Crawl"):
    with st.spinner("Crawling in progress..."):
        crawl_results = crawl_site(start_url, depth=max_depth)
    
    if crawl_results:
        st.success(f"Crawled {len(crawl_results)} pages.")
        for idx, (url, html_content) in enumerate(crawl_results, 1):
            st.markdown(f"### {idx}. [{url}]({url})")
            st.code(html_content[:500] + "...", language="html")  # Preview first 500 chars
    else:
        st.warning("No results returned. Check the URL or try a shallower depth.")
