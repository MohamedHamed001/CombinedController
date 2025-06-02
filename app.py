from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# Configuration
DIABETES_COMPANION_URL = "http://localhost:5000"
PID_NN_URL = "http://localhost:5001"

@app.route('/diabetes-companion/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def diabetes_companion_proxy(path):
    """Proxy requests to the Diabetes Companion service."""
    url = f"{DIABETES_COMPANION_URL}/{path}"
    return proxy_request(url)

@app.route('/pid-nn/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def pid_nn_proxy(path):
    """Proxy requests to the PID-NN service."""
    url = f"{PID_NN_URL}/{path}"
    return proxy_request(url)

def proxy_request(url):
    """Proxy the request to the appropriate service."""
    try:
        # Forward the request with the same method and data
        response = requests.request(
            method=request.method,
            url=url,
            headers={key: value for key, value in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
        )
        
        # Create the response
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in response.raw.headers.items()
                  if name.lower() not in excluded_headers]
        
        return response.content, response.status_code, headers
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "services": {
            "diabetes_companion": "running",
            "pid_nn": "running"
        }
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port) 