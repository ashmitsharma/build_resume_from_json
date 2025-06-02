# Resume Builder API

## Setup

1. Create and activate a virtual environment:
```
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```
pip install -r requirements.txt
```

## Running the Application

```
uvicorn main:app --reload
```
or
```
python main.py
```

The server will start on http://127.0.0.1:8000 by default.

## API Usage

### Generate Resume
Send a POST request to `/generate-resume` with JSON containing `basic_details` and `resume_data`:

```bash
curl -X POST http://localhost:8000/generate-resume \
  -H "Content-Type: application/json" \
  -d @expected_resume_format.json
```

Response:
```json
{
  "pdf": {
    "download_url": "/resume/download/resume_filename.pdf"
  }
}
```

### Download PDF
Send a GET request to the download URL:

```bash
curl -OJ http://localhost:8000/resume/download/resume_filename.pdf
```

This will download the generated PDF file.

## PDF Cleanup

Generated PDFs are automatically deleted after 30 minutes to save storage space.

## Expected JSON Format

See the `expected_resume_format.json` file for the complete structure.
