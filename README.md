# Contract Analyzer

## Introduction
Contract Analyzer is an advanced document analysis system powered by Large Language Models (LLM) that automates the compliance review process for legal contracts. It helps organizations ensure their contracts meet various regulatory requirements by extracting, analyzing, and providing detailed compliance insights.

The system uses state-of-the-art natural language processing to understand contract clauses, identify potential risks, and provide actionable recommendations. Whether you're dealing with data protection regulations, financial compliance, or industry-specific requirements, Contract Analyzer streamlines the review process and helps reduce compliance risks.

## Features

### Document Processing
- **Multi-format Support**: 
  - PDF documents with text extraction
  - Microsoft Word documents (.doc, .docx)
  - Plain text files (.txt)
- **Batch Processing**: Analyze multiple contracts simultaneously
- **Automatic Text Extraction**: Intelligent extraction of text from various document formats

### Clause Analysis
- **Automated Clause Extraction**: Automatically identifies and separates distinct clauses
- **Semantic Categorization**: Categorizes clauses into predefined types:
  - Data Privacy
  - Security
  - Liability
  - Termination
  - Payment
  - Confidentiality
  - Intellectual Property
  - Compliance
  - Force Majeure
  - Dispute Resolution

### Regulatory Compliance
- **Multi-regulation Support**:
  - GDPR (General Data Protection Regulation)
  - HIPAA (Health Insurance Portability and Accountability Act)
  - CCPA (California Consumer Privacy Act)
  - SOX (Sarbanes-Oxley Act)
  - PCI DSS (Payment Card Industry Data Security Standard)
  - FERPA (Family Educational Rights and Privacy Act)
- **Compliance Checking**:
  - Requirements validation
  - Gap analysis
  - Risk assessment
  - Compliance scoring

### Risk Assessment
- **Risk Scoring**: Each clause is assigned a risk score
- **Risk Categorization**: High, Medium, Low risk classification
- **Risk Factors Analysis**: Identifies specific risk factors in each clause
- **Mitigation Recommendations**: Provides actionable recommendations for risk mitigation

### Reporting
- **Comprehensive Analysis Reports**: Detailed insights into compliance status
- **Summary Statistics**: Overview of compliance metrics
- **Actionable Recommendations**: Specific steps for improving compliance
- **Export Capabilities**: Reports can be accessed via API response

## Examples

### 1. Single Contract Analysis

## Example Request

```python
import requests

# Analyze a single contract for GDPR compliance
url = "http://localhost:8000/api/v1/contracts/analyze"
files = {
    "file": ("contract.pdf", open("contract.pdf", "rb"), "application/pdf")
}
data = {
    "regulations": ["gdpr"]
}

response = requests.post(url, files=files, data=data)
results = response.json()
```

## Example Response
```json
{
    "file_name": "contract.pdf",
    "analysis_timestamp": "2024-12-19T20:38:18.491735",
    "regulations": ["gdpr"],
    "clauses": [...],
    "compliance_results": {...},
    "summary": {
        "total_clauses": 5,
        "analyzed_regulations": ["gdpr"],
        "timestamp": "2024-12-19T20:38:18.491735",
        "compliance_metrics": {...},
        "risk_assessment": {...},
        "key_issues": [...]
    }
}
```

### 2. Batch Analysis

```python
# Analyze multiple contracts
url = "http://localhost:8000/api/v1/contracts/analyze-batch"
files = [
    ("files", ("contract1.pdf", open("contract1.pdf", "rb"), "application/pdf")),
    ("files", ("contract2.pdf", open("contract2.pdf", "rb"), "application/pdf"))
]
data = {
    "regulations": ["gdpr", "hipaa"]
}

response = requests.post(url, files=files, data=data)
results = response.json()
```


## Project Structure

```
contract_analyzer/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── core/
│   │   ├── analyzer.py
│   │   ├── parser.py
│   │   ├── compliance.py
│   │   └── report.py
│   ├── models/
│   │   ├── enums.py
│   │   └── schemas.py
│   ├── api/
│   │   ├── routes/
│   │   │   └── contracts.py
│   │   └── dependencies.py
│   ├── services/
│   │   ├── llm.py
│   │   └── storage.py
│   └── utils/
│       └── helpers.py
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Ujwal0404/CONTRACT-ANALYZER_AGENT.git
cd contract-analyzer
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

Required environment variables:
- `GROQ_API_KEY`: Your Groq API key
- `MODEL_NAME`: LLM model name (default: "mixtral-8x7b-32768")
- `UPLOAD_DIR`: Directory for temporary file storage
- `APP_NAME`: Application name
- `ENVIRONMENT`: Development/production environment

## Usage

1. Start the server:
```bash
uvicorn app.main:app --reload
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

3. API Endpoints:
- POST `/api/v1/contracts/analyze`: Analyze a single contract
- POST `/api/v1/contracts/analyze-batch`: Analyze multiple contracts


## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Dependencies

- FastAPI
- Uvicorn
- Python-Multipart
- PyPDF2
- Python-docx
- Langchain
- Groq
- Pydantic
- Python-dotenv

## Authors

Ujwal Tandon

## Acknowledgments

- Groq for LLM API access
- FastAPI team for the excellent web framework
- Document processing libraries contributors
