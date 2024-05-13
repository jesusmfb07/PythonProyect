import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import etree
import feedparser
from bs4 import BeautifulSoup
import re

def check_rss_fetchrss_not_found(response_text):
    if "Feed does not exists" in response_text:
        return "RSS_FETCHRSS_NOT_FOUND"
    else:
        return None

def check_rss_rssapp_not_found(response_text):
    if "RSS.app - Feed Generator" in response_text:
        return "RSS_RSSAPP_NOT_FOUND"
    else:
        return None

def check_response_status(response):
    status_code = response.status_code
    error_type = None

    if status_code == 404:
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tags = soup.find_all('title')
        for title_tag in title_tags:
            title_text = title_tag.get_text()
            if "Feed does not exists" in title_text:
                error_type = "RSS_FETCHRSS_NOT_FOUND"
                break
            elif "RSS.app - Feed Generator" in response.text:
                error_type = "RSS_RSSAPP_NOT_FOUND"
                break

        if not error_type:
            error_type = "ERROR_404"

    elif status_code == 500:
        error_type = "ERROR_500"
    elif status_code == 502:
        error_type = "ERROR_502"
    elif status_code == 503:
        error_type = "ERROR_503"
    elif status_code == 403:
        error_type = "ERROR_403"
    elif status_code == 400:
        error_type = "ERROR_400"
    elif status_code == 402:
        error_type = "ERROR_402"

    return error_type, status_code

def analyze_content(response):
    try:
        content_type = response.headers.get("Content-Type", "").lower()
        content_text = response.text.strip()

        if '!doctype html' not in response.text.lower():
          if content_text.startswith('<?xml') or ('xmlns'in response.text) or ('<?xml'in response.text)or ('rss'in response.text)or ('rss version="2.0"'in response.text):
            soup = BeautifulSoup(content_text, 'xml')
            rss = soup.find('rss')
            if rss or('<rss version'in response.text):
                channel = rss.find('channel')
                if channel:
                    items = channel.find_all('item')
                    num_items = len(items)
                    if num_items > 0:
                        # Verificar si el contenido es un feed RSS válido
                        if all(item.find('title') and item.find('link') for item in items):
                            return "RSS_OK"
                        else:
                            return "RSS_OK"
                    else:
                        return "RSS_NO_ITEMS"
                else:
                    return "XML_CONTENT"
            else:
                return "XML_CONTENT"

        # Verificar si el contenido es HTML válido
        elif content_type.startswith("text/html")or ('<!doctype html'in response.text.lower()) or ('html'in response.text) :
            try:
                soup = BeautifulSoup(content_text, 'html.parser')
                if soup.find('html'):
                    return "HTML_CONTENT"
            except Exception:
                pass

        # Si no es HTML ni XML/RSS válido, devolver un error
        return " REVIEW_CONTENT "

    except Exception as e:
        return "REQUEST_NOT_FOUND"

def analyze_url(url_data):
    try:
        start_time = time.time()
        response = requests.get(url_data['feedUrl'], timeout=10)
        duration = (time.time() - start_time) * 1000

        error_type, status_code = check_response_status(response)
        if not error_type:
            error_type = analyze_content(response)

        result = {
            "_id": url_data["_id"],
            "feedUrl": url_data["feedUrl"],
            "status": url_data["status"],
            "type": status_code,
            "pageSizeInBytes": len(response.content),
            "durationInfoInMilliseconds": int(duration),
            "error": error_type if error_type else None
        }
    except requests.exceptions.RequestException as e:
            error_code = "REQUEST_NOT_FOUND"
            result = {
            "_id": url_data["_id"],
            "feedUrl": url_data["feedUrl"],
            "status": url_data["status"],
            "type": error_code,
            "pageSizeInBytes": 0,
            "durationInfoInMilliseconds": 0,
            "error": error_code
        }

    return result 

def load_input_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def write_output_data(results, file_path):
    with open(file_path, "w") as f:
        json.dump(results, f, indent=2)

def process_urls(url_data):
    max_workers = 20
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(analyze_url, data) for data in url_data]
        results = []
        for future in as_completed(futures):
            result = future.result()
            print(f"URL: {result['feedUrl']}, Error: {result['error']}")
            results.append(result)

    return results

def main():
    input_data = load_input_data("data.json")
    results = process_urls(input_data)
    write_output_data(results, "output.json")

if __name__ == "__main__":
   main()