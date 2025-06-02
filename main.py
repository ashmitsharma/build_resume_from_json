from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, Body, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from document_process import cleanup_old_pdfs, generate_resume_from_json
import os
import asyncio
import threading
import schedule
import time

app = FastAPI()

# PDF cleanup configuration
PDF_DIR = "generated_pdfs"
PDF_TTL_MINUTES = 30

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/generate-resume")
async def generate_resume(
    basic_details: Dict[str, Any] = Body(..., embed=True),
    resume_data: Dict[str, Any] = Body(..., embed=True)
    ):
    # task = generate_resume_from_json.delay(resume_data)
    try:
        # Directly await the coroutine instead of using asyncio.run()
        pdf_result = await generate_resume_from_json(basic_details, resume_data)
    
        if pdf_result:
            return {
                "pdf": {
                    "download_url": pdf_result["download_url"]
                }
            }
        else:
            return {
                "status": "error",
                "error_message": "Failed to generate PDF resume"
            }
    except Exception as e:
        # Return error information
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e)
        }



@app.get("/resume/download/{filename}")
async def download_pdf(filename: str):
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


# Schedule periodic cleanup of old PDF files
def start_cleanup_scheduler():
    import schedule
    import time
    
    # Schedule cleanup to run every 30 minutes
    schedule.every(30).minutes.do(cleanup_old_pdfs, pdf_dir=PDF_DIR, ttl_minutes=PDF_TTL_MINUTES)
    
    # Run an initial cleanup
    cleanup_old_pdfs(PDF_DIR, PDF_TTL_MINUTES)
    
    # Keep running the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)

# Event handler for application startup
@app.on_event("startup")
async def startup_event():
    # Start the cleanup scheduler in a background thread
    cleanup_thread = threading.Thread(target=start_cleanup_scheduler, daemon=True)
    cleanup_thread.start()
    print(f"Started PDF cleanup scheduler (TTL: {PDF_TTL_MINUTES} minutes)")


# Run the application with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)