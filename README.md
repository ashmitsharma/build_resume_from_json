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

### Start Redis Server
Make sure Redis is installed and running on localhost:6379 (default port).

### Start Celery Worker
```
celery -A tasks worker --loglevel=info
```

### Start FastAPI Server
```
python main.py
```
The server will start on http://0.0.0.0:8000 by default.

## API Usage

### Generate Resume
Send a POST request to `/generate-resume` with a JSON body matching the expected format.

```bash
curl -X POST http://localhost:8000/generate-resume \
  -H "Content-Type: application/json" \
  -d @expected_resume_format.json
```

Response:
```json
{
  "task_id": "task-uuid-here"
}
```

### Check Task Status
Send a GET request to `/task-status/{task_id}`:

```bash
curl http://localhost:8000/task-status/task-uuid-here
```

Response:
```json
{
  "task_id": "task-uuid-here",
  "status": "SUCCESS",
  "result": {
    "pdf": {
      "download_url": "/resume/download/resume_filename.pdf"
    }
  }
}
```

### Download PDF
Once the task is successful, use the download URL from the result:

```bash
curl -O http://localhost:8000/resume/download/resume_filename.pdf
```

## Expected JSON Format

See the `expected_resume_format.json` file for the complete structure. Here's a simplified example:

```json
{
  "basicDetails": {
    "name": "John Doe",
    "position": "Software Engineer",
    "email": "john.doe@example.com",
    "linkedin": "linkedin.com/in/johndoe",
    "location": "New York, NY",
    "phone": "(123) 456-7890"
  },
  "summary": "Experienced software engineer...",
  "skills": ["JavaScript", "Python", "React"],
  "experience": [
    {
      "company": "Tech Company",
      "position": "Senior Developer",
      "location": "San Francisco, CA",
      "startDate": "Jan 2020",
      "endDate": "Present",
      "description": "Led development of microservices..."
    }
  ],
  "education": [
    {
      "institution": "University of Technology",
      "degree": "Bachelor of Computer Science",
      "location": "Boston, MA",
      "startDate": "Sep 2012",
      "endDate": "Jun 2016"
    }
  ]
}
```
