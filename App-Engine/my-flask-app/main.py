from flask import Flask, jsonify
import os
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    current_time = datetime.datetime.now(datetime.UTC).isoformat()

    return jsonify({
        "message": "Hello from App Engine (Flask)!",
        "time": current_time,
        "env": os.environ.get("GAE_SERVICE", "local-dev")
    })

@app.route('/health')
def health():
    return "ok", 200


if __name__ == '__main__':
    # Runs locally on MacBook Air
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
