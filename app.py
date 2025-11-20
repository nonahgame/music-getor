# ... (existing)

from flask import send_from_directory
import os
from dotenv import load_dotenv
load_dotenv()

# LangSmith in routes
from langsmith import traceable  # Decorator for custom traces

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory("output", filename)

"""
@app.route("/generate", methods=["POST"])
@traceable  # Traces endpoint runs
def generate():
    # ... (existing)
    # In stream: Traces graph invocations
    #return jsonify({... , "trace_id": "view in LangSmith"})  # Optional
    return jsonify({"message": "Generation started", "status": "processing"})
"""

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    # Just a dummy response for now — real agent will be added next
    import time, random, string
    time.sleep(2)
    v1 = ''.join(random.choices(string.ascii_lowercase, k=10)) + ".mp3"
    v2 = ''.join(random.choices(string.ascii_lowercase, k=10)) + ".mp4"
    return jsonify({
        "version1": v1,
        "version2": v2,
        "message": "Generation complete!",
        "trace_url": "https://smith.langchain.com"
    })

if __name__ == "__main__":

    app.run(debug=True)

