import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer

data_aadhaar = pd.read_json(r'Document Metrics Identifier\Data\pii_aadhaar_sen.jsonl', lines=True)
data_pan = pd.read_json(r'Document Metrics Identifier\Data\pii_pan_sen.jsonl', lines=True)
data_number = pd.read_json(r'Document Metrics Identifier\Data\pii_phone_sen.jsonl', lines=True)
data_multi = pd.read_json(r'Document Metrics Identifier\Data\synthetic_multilabel.jsonl', lines=True)
data_address = pd.read_json(r'Document Metrics Identifier\Data\pii_address_sen.jsonl', lines=True)
data_credit = pd.read_json(r'Document Metrics Identifier\Data\pii_credit_sen.jsonl', lines=True)
data_email = pd.read_json(r'Document Metrics Identifier\Data\pii_email_sen.jsonl', lines=True)
data_safe = pd.read_json(r'Document Metrics Identifier\Data\pii_safe_sen.jsonl', lines=True)
data_pass = pd.read_json(r'Document Metrics Identifier\Data\pii_pass_sen_2.jsonl', lines=True)
data_url = pd.read_json(r'Document Metrics Identifier\Data\pii_url_sen.jsonl', lines=True)

df = pd.concat([
    data_aadhaar,
    data_pan,
    data_number,
    data_multi,
    data_address,
    data_credit,
    data_email,
    data_safe,
    data_pass,
    data_url
], axis=0)

df = pd.concat([data_aadhaar, data_pan, data_number, data_multi], axis=0)
def clean_label(x):
    if isinstance(x, list):
        return x
    elif pd.isna(x):
        return []
    else:
        return [x]

df["label"] = df["label"].apply(clean_label)

Xtrain, Xtest, ytrain, ytest = train_test_split(
    df["text"], df["label"], test_size=0.2, random_state=42
)

mlb = MultiLabelBinarizer()
ytrain_bin = mlb.fit_transform(ytrain)
ytest_bin = mlb.transform(ytest)

clf = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
    ("clf", OneVsRestClassifier(LogisticRegression(max_iter=1000, class_weight="balanced")))
])

clf.fit(Xtrain, ytrain_bin)

joblib.dump(clf, "model.pkl")
joblib.dump(mlb, "mlb.pkl")

