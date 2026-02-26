from flask import Flask, request, Response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Service registry (routing only)
SERVICES = {
    "books": "http://books:5000/books",
    "users": "http://users:5000/users",
    "loans": "http://loans:5000/loans"
}


# All routes must start with /api
@app.route('/api/<service>', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/api/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(service, path):

    if service not in SERVICES:
        return {"error": "Service not found"}, 404

    target_url = f"{SERVICES[service]}/{path}" if path else SERVICES[service]

    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            json=request.get_json(silent=True),
            headers={key: value for key, value in request.headers if key != 'Host'}
        )

        return Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type')
        )

    except requests.exceptions.RequestException:
        return {"error": "Service unavailable"}, 503


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)