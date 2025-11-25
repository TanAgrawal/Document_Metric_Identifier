from flask import Flask, request, jsonify, render_template
import joblib
from main.document_extracter import extract_text_with_tika_client
import os 
from celery_app import cel
import tasks
from split_aggregate import split_doc, aggregator

app = Flask(__name__)

base_path = r"Document Metrics Identifier\Backup"
model_path = os.path.join(base_path, "model.pkl")
mlb_path = os.path.join(base_path, "mlb.pkl")
clf = joblib.load(model_path)
mlb = joblib.load(mlb_path)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

from celery import group
from tasks import process_seg_task

@app.route("/extract", methods=["POST"])
def document_reader():
    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Pass filename to the extraction function for proper loader selection
        text = extract_text_with_tika_client(file.stream, filename=file.filename)
        results = document_extractor(text)
        return render_template("index.html", text=text, results=results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def document_extractor(text):
    segments = split_doc(text)

    task_group = group(process_seg_task.s(seg) for seg in segments)
    async_result = task_group.apply_async()
    segment_outputs = async_result.get(timeout=60)

    final_result = aggregator(segment_outputs)
    return final_result

if __name__ == "__main__":
    app.run(debug=True)