from celery import Celery
import os
import asyncio
from typing import Dict
from document_process import generate_resume_from_json as gen_resume

celery_app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0', result_expires=300)

@celery_app.task(name='tasks.generate_resume_from_json')
def generate_resume_from_json(resume_data: Dict):
    # Use the imported function with a different name to avoid name conflict
    try:
        pdf_result = asyncio.run(gen_resume(resume_data))
    
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