RSS Feed Analyzer
This project contains a Python script that parses RSS feed URLs and determines different types of errors based on the content of the HTTP response. The script uses the requests, BeautifulSoup and concurrent.futures libraries to perform HTTP requests, parse the content of the responses and process multiple URLs concurrently.
Features

Parses RSS feed URLs in parallel using a thread pool.
Determines different types of errors based on status code and response content.
Handles common errors such as 404, 500, 403, 400 and 402.
Detects specific error cases related to RSS feeds, such as RSS_FETCHRSS_NOT_FOUND and RSS_RSSAPP_NOT_FOUND.
Identifies whether the response content is XML or HTML in case of a 404 error.

Requirements

Python 3.x
Libraries: requests, beautifulsoup4

Usage

Clone this repository or download the script.py file.
Make sure you have the required libraries installed. You can install them with pip:

pip install requests beautifulsoup4

Prepare a data.json file with a list of RSS feed URLs you want to parse. Each URL must have an _id, feedUrl and status. 

Execute the script:

python script.py

The script will load the URLs from data.json, parse them and save the results in an output.json file.
Code structure

check_response_status(response): Checks the HTTP response status code and determines the corresponding error type.
analyze_xml_content(response): Analyze the XML content of the response and determine the corresponding error type.
analyze_url(url_data): Performs an HTTP request to the provided URL, parses the response and formats the result.
process_urls(url_data): Creates a thread pool and processes multiple URLs concurrently.
main(): Main function that loads the input data, processes the URLs and saves the results.



