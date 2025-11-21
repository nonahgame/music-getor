from flask import Flask, render_template, request, jsonify, send_from_directory
import threading
import os

app = Flask(__name__)
OUTPUT_DIR = "output"
PUBLIC_DIR = "public_downloads"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)

from agent import run_agent

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

@app.route("/public/<filename>")
def public(filename):
    return send_from_directory(PUBLIC_DIR, filename, as_attachment=True)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    threading.Thread(target=run_agent, args=(data,)).start()
    return jsonify({"message": "Generating real music video... (2–6 minutes)", "status": "working"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
