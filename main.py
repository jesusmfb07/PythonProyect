import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import etree, html

def find_items(element):
    items = []
    if element.tag == "item":
        items.append(element)
    for child in element:
        items.extend(find_items(child))
    return items

def analyze_url(url_data):
    try:
        start_time = time.time()
        response = requests.get(url_data['feedUrl'], timeout=10)
        content_type = response.headers.get("Content-Type", "").lower()
        error_type = None
        if content_type.startswith("text/xml") or content_type.startswith("application/xml"):
            try:
                root = etree.fromstring(response.content)
                items = find_items(root)
                if items:
                    error_type = None
                else:
                    error_type = "XML_NO_ITEM"
                if len(response.content) < 80:
                    error_type = "XML_INCOMPLETE"
            except etree.XMLSyntaxError:
                error_type = "XML_SYNTAX_ERROR"
            except Exception as e:
                if "Document is empty" in str(e) or len(response.content) < 80:
                    error_type = "XML_INCOMPLETE"
                else:
                    error_type = "NOT_XML"
        elif content_type.startswith("text/html"):
            if response.status_code == 404:
                error_type = "NOT_FOUND"
            else:
                error_type = "HTML_CONTENT"
        if "www.limber.io" in url_data['feedUrl'] or "feeds-twitter.limber.io" in url_data['feedUrl']:
            return None
        duration = (time.time() - start_time) * 1000  # Convertir el tiempo a milisegundos
        result = {
            "_id": url_data["_id"],
            "feedUrl": url_data["feedUrl"],
            "status": url_data["status"],
            "type": response.status_code,
            "pageSizeInBytes": len(response.content),
            "durationInfoInMilliseconds": int(duration),
            "error": error_type if error_type else None
        }
        return result
    except requests.exceptions.RequestException as e:
        error_code = "REQUEST_ERROR"
        return {
            "_id": url_data["_id"],
            "feedUrl": url_data["feedUrl"],
            "status": url_data["status"],
            "type": error_code,
            "pageSizeInBytes": 0,
            "durationInfoInMilliseconds": 0,
            "error": error_code
        }

# Cargar los datos de entrada
with open("data.json", "r") as f:
    url_data = json.load(f)

# Analizar cada URL de forma concurrente
max_workers = 20
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = [executor.submit(analyze_url, data) for data in url_data]
    results = []
    for index, future in enumerate(as_completed(futures), start=1):
        try:
            result = future.result()
            if result is not None:
                results.append(result)
            print(f"Analizando URL {index}/{len(url_data)}: {url_data[index-1]['feedUrl']}")
        except Exception as e:
            print(f"Error al procesar la URL {index}: {e}")

# Ordenar los resultados por el campo "type"
def sort_key(result):
    try:
        return int(result["type"])
    except ValueError:
        return float('inf')  # Trata los valores no numéricos como infinito

results.sort(key=sort_key)

# Escribir los resultados en un archivo JSON
with open("output.json", "w") as f:
    json.dump(results, f, indent=2)