import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import etree, html

def analyze_url(url_data):
    try:
        start_time = time.time()
        response = requests.get(url_data['feedUrl'], timeout=10)  # Tiempo de espera de 10 segundos
        duration = time.time() - start_time
        content_type = response.headers.get("Content-Type", "").lower()
        error_type = None
        if content_type.startswith("text/xml") or content_type.startswith("application/xml"):
            try:
                root = etree.fromstring(response.content)
            except etree.XMLSyntaxError as e:
                error_type = "XML_SYNTAX_ERROR"
            except Exception as e:
                if len(response.content) < 1200:
                    error_type = "XML_SMALL"
                else:
                    error_type = "NOT_XML"
        elif content_type.startswith("text/html"):
            try:
                html_root = html.fromstring(response.content)
                error_type = "HTML_CONTENT"
            except Exception as e:
                error_type = "HTML_PARSE_ERROR"
        result = {
            "_id": url_data["_id"],
            "feedUrl": url_data["feedUrl"],
            "status": url_data["status"],
            "type": "HTTP_" + str(response.status_code),
            "pageSizeInBytes": len(response.content),
            "durationInfoInMilliseconds": int(duration * 1000),
            "error": error_type
        }
        return result
    except requests.exceptions.RequestException as e:
        error_code = "REQUEST_ERROR"
        return {
            "_id": url_data["_id"],
            "feedUrl": url_data["feedUrl"],
            "status": "NOT_AVAILABLE",
            "type": "REQUEST_ERROR",
            "pageSizeInBytes": 0,
            "durationInfoInMilliseconds": 0,
            "error": error_code
        }

# Cargar los datos de entrada
with open("data.json", "r") as f:
    url_data = json.load(f)

# Analizar cada URL de forma concurrente
max_workers = 20  # Reducir el número de hilos máximo
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

# Modificar el error para los XML pequeños
for result in results:
    if result['pageSizeInBytes'] < 1200:
        result['error'] = "XML_SMALL"

# Escribir los resultados en un archivo JSON
with open("output.json", "w") as f:
    json.dump(results, f, indent=2)