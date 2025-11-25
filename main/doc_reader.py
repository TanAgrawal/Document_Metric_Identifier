import re
import numpy as np
import spacy
from spacy.matcher import PhraseMatcher
import joblib

nlp = spacy.load("en_core_web_sm")

regex_patterns = {
    "AADHAAR_NUMBER": r"(?<!\d)(?:\d{4}[-\s]?){2}\d{4}(?!\d)",
    "PAN_NUMBER": r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    "PHONE_NUMBER": r"(?<!\d)(?:\+91|0091|91|\(91\))?[\s\-\.]*[6-9]\d{2}[\s\-\.]*\d{3}[\s\-\.]*\d{4}(?!\d)"

}

keyword_aliases = {
    "AADHAAR_NUMBER": ["aadhaar", "aadhar", "uidai", "aadhaar number", "aadhaar no", "aadhaar id"],
    "PAN_NUMBER": ["pan", "pan number", "pan no", "income tax id"],
    "PHONE_NUMBER": ["phone", "mobile", "mobile number", "registered mobile", "reach out", "call"]
}

matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
for label, keywords in keyword_aliases.items():
    patterns = [nlp.make_doc(kw) for kw in keywords]
    matcher.add(label, patterns)

def detect_keyword(segment):
    doc = nlp(segment)
    matches = matcher(doc)

    matched_keywords, keyword_labels = [], []
    for match_id, start, end in matches:
        span = doc[start:end]
        label = nlp.vocab.strings[match_id]
        matched_keywords.append(span.text)
        keyword_labels.append(label)

    return matched_keywords, keyword_labels

def extract_with_regex(label, text):
    if label not in regex_patterns:
        return []
    return [m for m in re.finditer(regex_patterns[label], text, flags=re.IGNORECASE)]

def segment_text(text):
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]

def process_segment(seg, clf, mlb, threshold=0.1):
    results = []
    seg = seg.strip()
    if not seg:
        return {"Extracted Data": []}

    probs = clf.predict_proba([seg])[0]
    labels = mlb.classes_

    matched_keywords, keyword_labels = detect_keyword(seg)

    for idx, lbl in enumerate(labels):
        conf = float(probs[idx])

        if conf < threshold:
            continue

        if lbl not in keyword_labels:
            continue

        if lbl in regex_patterns:
            matches = extract_with_regex(lbl, seg)
            for match in matches:
                start, end = match.span()
                results.append({
                    "segment": seg,
                    "detected_label": lbl,
                    "matched_keyword": [
                        kw for kw, kw_lbl in zip(matched_keywords, keyword_labels)
                        if kw_lbl == lbl
                    ],
                    "extracted_value": match.group().strip(),
                    "offset": {"start": start, "end": end},
                    "confidence": round(conf, 3)
                })

    return {"Extracted Data": results}


clf, mlb = joblib.load(r"Document Metrics Identifier\Backup\model.pkl")
