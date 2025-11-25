# Document Metrics Identifier 

A Flask-based web application that automatically extracts and identifies Aadhaar number, pan number and mobile number from various document formats using Machine Learning and Natural Language Processing.

##  Features

- **Multi-Format Document Support**: PDF, Word (.doc/.docx), Excel, PowerPoint, Text, CSV
- **OCR Capability**: Automatic text extraction from scanned documents and image-based PDFs
- **PII Detection**: Identifies Aadhaar numbers, PAN cards, phone numbers, and more
- **Distributed Processing**: Celery-based task queue for handling large documents efficiently
- **ML-Powered Classification**: Multi-label text classification using scikit-learn
- **RESTful API**: Easy integration with other systems
- **Web Interface**: User-friendly interface for document upload and results visualization

##  Detected Metrics

Currently supports detection of:

-  **Aadhaar Numbers** (Indian national ID)
-  **PAN Numbers** (Permanent Account Number)
-  **Phone Numbers** (with Indian format support)

## Tech Stack

### Backend
- **Flask** - Web framework for API and routing
- **Celery** - Distributed task queue for async processing
- **Redis** - Message broker and result backend for Celery
- **scikit-learn** - Machine learning for text classification
- **spaCy** - NLP for text processing and sentence segmentation

### Document Processing
- **LangChain** - Document loaders and text extraction
- **PyMuPDF** - Advanced PDF parsing
- **Unstructured** - Multi-format document parsing with OCR
- **Tesseract OCR** - Optical character recognition for scanned documents
- **python-docx** - Word document processing
- **openpyxl** - Excel file handling

### Machine Learning
- **TF-IDF Vectorization** - Text feature extraction
- **Logistic Regression** - Multi-label classification
- **MultiLabelBinarizer** - Label encoding
- **Regex + NLP** - Pattern matching and context validation

## Prerequisites

- Python 3.8 or higher
- Redis Server (for Celery)
- Tesseract OCR (optional, for scanned documents)
- 4GB RAM minimum (8GB recommended for large documents)

##  Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/document-metrics-identifier.git
cd document-metrics-identifier
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install System Dependencies

#### For OCR Support (Optional but Recommended)

**Windows:**
1. Download Tesseract from [here](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install and add to PATH

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr libtesseract-dev poppler-utils
```

**MacOS:**
```bash
brew install tesseract poppler
```

### 5. Download spaCy Model
```bash
python -m spacy download en_core_web_sm
```

### 6. Install and Start Redis

**Windows:**
- Download from [Redis Windows](https://github.com/microsoftarchive/redis/releases)
- Or use Docker: `docker run -d -p 6379:6379 redis`

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**MacOS:**
```bash
brew install redis
brew services start redis
```

### 7. Train the Model (First Time Setup)
```bash
python train_model.py
```

This will create `model.pkl` and `mlb.pkl` files in the `Document Metrics Identifier\Backup` directory.

## Usage

### Starting the Application

You need to run three components:

#### 1. Start Redis (if not already running)
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

#### 2. Start Celery Workers
```bash
# In a new terminal
python start_workers.py
```

This starts 4 worker processes to handle document processing tasks.

#### 3. Start Flask Application
```bash
# In another terminal
python app.py
```

The application will be available at `http://localhost:5000`

### Using the Web Interface

1. Open your browser and go to `http://localhost:5000`
2. Click "Choose File" and select a document
3. Click "Upload" to process the document
4. View extracted text and detected PII metrics

### Using the API

#### Extract Metrics from Document
```bash
curl -X POST http://localhost:5000/extract \
  -F "file=@/path/to/your/document.pdf"
```

#### Response Format
```json
{
  "Extracted Data": [
    {
      "segment": "My Aadhaar number is 1234 5678 9012",
      "detected_label": "AADHAAR_NUMBER",
      "matched_keyword": ["aadhaar"],
      "extracted_value": "1234 5678 9012",
      "offset": {"start": 23, "end": 37},
      "confidence": 0.956
    },
    {
      "segment": "Contact me at +91-9876543210",
      "detected_label": "PHONE_NUMBER",
      "matched_keyword": ["contact"],
      "extracted_value": "+91-9876543210",
      "offset": {"start": 14, "end": 28},
      "confidence": 0.892
    }
  ]
}
```

## Architecture

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       ↓
┌─────────────────┐
│  Flask App      │
│  (app.py)       │
└────────┬────────┘
         │
         ↓
┌─────────────────────────┐
│  Document Extraction    │
│  (document_extracter.py)      │
│  - LangChain Loaders    │
│  - OCR (if available)   │
└────────┬────────────────┘
         │
         ↓
┌─────────────────────────┐
│  Text Segmentation      │
│  (split_aggregate.py)   │
│  - spaCy sentence split │
└────────┬────────────────┘
         │
         ↓
┌─────────────────────────┐
│  Celery Task Queue      │
│  - Distributed workers  │
│  - Parallel processing  │
└────────┬────────────────┘
         │
         ↓
┌─────────────────────────┐
│  ML Classification      │
│  (doc_reader.py)        │
│  - TF-IDF features      │
│  - Logistic Regression  │
│  - Regex extraction     │
└────────┬────────────────┘
         │
         ↓
┌─────────────────────────┐
│  Results Aggregation    │
│  (split_aggregate.py)   │
└────────┬────────────────┘
         │
         ↓
┌─────────────────┐
│  JSON Response  │
└─────────────────┘
```

##  Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Redis Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216  # 16MB
```

### Celery Configuration

Edit `celery_app.py` to customize:
```python
cel = Celery(
    'doc_reader',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

# Optional: Add configurations
cel.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
)
```

### Model Configuration

Adjust detection threshold in `doc_reader.py`:
```python
def process_segment(seg, clf, mlb, threshold=0.1):
    # Lower threshold = more detections (may include false positives)
    # Higher threshold = fewer detections (more conservative)
```

##  How It Works

### 1. Document Upload
User uploads a document through the web interface or API.

### 2. Text Extraction
The system uses LangChain loaders to extract text:
- For PDFs: Tries UnstructuredPDF (OCR) → PyMuPDF → PyPDF
- For Word: Docx2txt → UnstructuredWord
- Falls back to appropriate loaders for each format

### 3. Text Segmentation
Text is split into sentences using spaCy's sentence segmentation.

### 4. Distributed Processing
Each sentence is sent to Celery workers for parallel processing.

### 5. ML Classification
For each segment:
- TF-IDF vectorization extracts features
- Logistic Regression predicts PII labels
- Keyword matching validates context
- Regex patterns extract actual values

### 6. Result Aggregation
All worker results are collected and combined into a final response.

##  Testing

### Test Single Document
```python
from document_extracter import extract_text_with_tika_client
from doc_reader import process_segment
import joblib

# Load model
clf = joblib.load("Document Metrics Identifier/Backup/model.pkl")
mlb = joblib.load("Document Metrics Identifier/Backup/mlb.pkl")

# Test extraction
with open("test.pdf", "rb") as f:
    text = extract_text_with_tika_client(f, filename="test.pdf")
    result = process_segment(text, clf, mlb)
    print(result)
```

### Test API Endpoint
```python
import requests

files = {'file': open('document.pdf', 'rb')}
response = requests.post('http://localhost:5000/extract', files=files)
print(response.json())
```

## Troubleshooting

### Issue: Redis Connection Error
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
sudo systemctl start redis-server  # Linux
brew services start redis           # Mac
```

### Issue: Celery Workers Not Starting
```bash
# Check Redis connection
redis-cli ping

# Try starting single worker
celery -A celery_app.cel worker --loglevel=INFO
```

### Issue: Model Not Found
```bash
# Train the model first
python train_model.py
```

### Issue: OCR Not Working
- Verify Tesseract installation: `tesseract --version`
- Install system dependencies (see Installation section)
- The system will still work for text-based PDFs

### Issue: Out of Memory
- Reduce number of workers in `start_workers.py`
- Process smaller documents
- Increase system RAM

