def split_doc(text):
    import spacy
    nlp = spacy.load("en_core_web_sm")  
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]

def aggregator(results):
    aggregated_solution = []
    for result in results:
        aggregated_solution.extend(result["Extracted Data"])
    return {"Extracted Data": aggregated_solution}