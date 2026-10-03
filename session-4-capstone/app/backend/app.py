import os
import socket
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/info")
def info():
    return jsonify(
        message="Hello from the backend!",
        host=socket.gethostname(),
        env=os.environ.get("APP_ENV", "unknown"),
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
