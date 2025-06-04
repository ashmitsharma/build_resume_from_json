import asyncio
import os
import uuid
import time
import datetime
from weasyprint import HTML, CSS
from fastapi.templating import Jinja2Templates
from typing import Dict, Any, List


def format_resume_data(data: Dict[str, Any]) -> Dict[str, Any]:
    formatted_data = {}
    
    # Format summary
    if "Professional_Summary" in data:
        formatted_data["summary"] = data["Professional_Summary"]
    
    # Format skills - ensure we're not passing dictionaries with 'items' method
    if "skills" in data:
        formatted_data["skills"] = []
        for skill_category in data["skills"]:
            formatted_skill = {
                "category": skill_category.get("category", ""),
                "skill_items": skill_category.get("items", [])
            }
            formatted_data["skills"].append(formatted_skill)
    
    # Format work experience
    if "work_experiences" in data:
        formatted_data["experience"] = []
        for job in data["work_experiences"]:
            formatted_job = {
                "company": job.get("company", ""),
                "position": job.get("job_title", ""),
                "location": job.get("location", ""),  # Location might not be in the input data
                "description": "\n".join(job.get("description", [])) if isinstance(job.get("description"), list) else job.get("description", "")
            }
            
            # Parse duration into startDate and endDate
            duration = job.get("duration", "")
            if duration and " – " in duration:
                start_date, end_date = duration.split(" – ")
                formatted_job["startDate"] = start_date
                formatted_job["endDate"] = end_date
            else:
                formatted_job["startDate"] = ""
                formatted_job["endDate"] = duration
                
            formatted_data["experience"].append(formatted_job)
    
    # Format projects
    if "projects" in data:
        formatted_data["projects"] = []
        for project in data["projects"]:
            technologies = ", ".join(project.get("technologies", []))
            tech_str = f" ({technologies})" if technologies else ""
            
            formatted_project = {
                "title": project.get("name", "") + tech_str,
                "description": "\n".join(project.get("description", [])) if isinstance(project.get("description"), list) else project.get("description", "")
            }
            formatted_data["projects"].append(formatted_project)
    
    # Add education if present 
    if "education" in data:
        formatted_data["education"] = data["education"]
    else:
        formatted_data["education"] = []
    
    # Add certifications if present
    if "certifications" in data:
        formatted_data["certifications"] = data["certifications"]
    
    # # Add key achievements if present (not in the sample data)
    # if "key_achievements" in data:
    #     formatted_data["keyAchievements"] = data["key_achievements"]
    
    return formatted_data


def cleanup_old_pdfs(pdf_dir: str, ttl_minutes: int = 30):
    current_time = time.time()
    ttl_seconds = ttl_minutes * 60
    
    try:
        # Check if directory exists
        if not os.path.exists(pdf_dir):
            return
            
        # Get all files in the directory
        for filename in os.listdir(pdf_dir):
            file_path = os.path.join(pdf_dir, filename)
            
            # Skip directories and non-PDF files
            if os.path.isdir(file_path) or not filename.endswith('.pdf'):
                continue
                
            # Check file age
            file_age = current_time - os.path.getmtime(file_path)
            
            # Remove file if older than TTL
            if file_age > ttl_seconds:
                try:
                    os.remove(file_path)
                    print(f"Removed old PDF: {filename}, age: {datetime.timedelta(seconds=int(file_age))}")
                except Exception as e:
                    print(f"Error removing {filename}: {str(e)}")
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")


async def generate_resume_from_json(basic_details, resume_data): 
    templates = Jinja2Templates(directory="templates")
    
    PDF_DIR = "generated_pdfs"
    os.makedirs(PDF_DIR, exist_ok=True)
    
    # Clean up old PDF files
    cleanup_old_pdfs(PDF_DIR)
    
    # Generate a unique filename for the PDF
    filename = f"resume_{uuid.uuid4().hex}.pdf"
    pdf_path = os.path.join(PDF_DIR, filename)
    
    # First, ensure resume_data is a dictionary
    if not isinstance(resume_data, dict):
        raise TypeError("resume_data must be a dictionary")
    
    # Ensure basic_details is a dictionary
    if not isinstance(basic_details, dict):
        raise TypeError("basic_details must be a dictionary")
    
    # Format the data according to our template's expected structure
    formatted_data = format_resume_data(resume_data)
    
    # Create a complete resume object with basicDetails
    complete_resume = formatted_data
    complete_resume["basicDetails"] = basic_details
    
    # Render template with the provided data
    html_content = templates.get_template("resume/resume.html").render(
        resume=complete_resume
    )
    
    try:  
        # Save the HTML content to a temporary file
        temp_html_path = os.path.join(PDF_DIR, f"temp_{uuid.uuid4().hex}.html")
        with open(temp_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"Temporary HTML file created at {temp_html_path}")

        HTML(filename=temp_html_path).write_pdf(
            pdf_path,
        )
        
        # Verify PDF was created and has content
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            print(f"PDF generated successfully at {pdf_path}")
        else:
            print(f"PDF generation failed or created empty file at {pdf_path}")
            return None
            
        # Clean up the temporary HTML file
        try:
            os.remove(temp_html_path)
            print(f"Temporary HTML file removed: {temp_html_path}")
        except Exception as e:
            print(f"Warning: Could not remove temporary HTML file: {str(e)}")
            
        # Return the PDF filename and path
        return {
            "download_url": f"/resume/download/{filename}"
        }
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return None
