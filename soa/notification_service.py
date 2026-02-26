# notification_service.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/notifications', methods=['POST'])
def send_notification():
    data = request.json
    # Simulate sending notification
    print(f"Notification sent to user {data['user_id']}: {data['message']}")
    return jsonify({"status": "notification sent"}), 200

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')