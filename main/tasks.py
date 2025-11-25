from celery_app import cel
from doc_reader import process_segment
import joblib
import os

base_path = r"Document Metrics Identifier\Backup"
model_path = os.path.join(base_path, "model.pkl")
mlb_path = os.path.join(base_path, "mlb.pkl")

clf = joblib.load(model_path)
mlb = joblib.load(mlb_path)

@cel.task(name='tasks.process_seg_task')
def process_seg_task(seg):
    return process_segment(seg, clf, mlb)
