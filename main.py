from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, Body
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from celery.result import AsyncResult
from typing import Dict, Any
from tasks import celery_app, generate_resume_from_json
import os

app = FastAPI()


# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/generate-resume")
async def generate_resume(resume_data: Dict[str, Any] = Body(...)):
    task = generate_resume_from_json.delay(resume_data)
    
    return {"task_id": task.id}


@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
    }
    
    # If the task is complete, include the result
    if task_result.status == "SUCCESS":
        response["result"] = task_result.result
    elif task_result.status == "FAILURE":
        response["error"] = str(task_result.result)
        
    return response


@app.get("/resume/download/{filename}")
async def download_pdf(filename: str):
    PDF_DIR="generated_pdfs"
    file_path = os.path.join(PDF_DIR, filename)
    if os.path.exists(file_path):
        # Check if file is not empty
        if os.path.getsize(file_path) > 0:
            return FileResponse(
                path=file_path,
                filename="resume.pdf", 
                media_type="application/pdf",
                headers={
                    "Content-Disposition": "attachment; filename=resume.pdf",
                    "Content-Type": "application/pdf"
                }
            )
        else:
            return JSONResponse(content={"error": "PDF file is empty"}, status_code=500)
    else:
        print(f"PDF file not found: {file_path}")
        return JSONResponse(content={"error": "File not found"}, status_code=404)


# Run the application with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)