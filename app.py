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

@app.route("/generate", methods=["POST"])
@traceable  # Traces endpoint runs
def generate():
    # ... (existing)
    # In stream: Traces graph invocations
    #return jsonify({... , "trace_id": "view in LangSmith"})  # Optional
    return jsonify({"message": "Generation started", "status": "processing"})

if __name__ == "__main__":

    app.run(debug=True)
