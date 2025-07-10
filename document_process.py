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


def count_value_characters(data):
    total_chars = 0

    if isinstance(data, str):
        total_chars += len(data)
    elif isinstance(data, list):
        for item in data:
            total_chars += count_value_characters(item)
    elif isinstance(data, dict):
        for value in data.values():
            total_chars += count_value_characters(value)

    return total_chars


def get_page_size(characters):
    if characters >= 5000 and characters <= 6000:
        print("characters >= 5000 and characters <= 6000")
        return 380
    elif characters >= 4700 and characters < 5000:
        print("characters >= 4700 and characters < 5000")
        return 350
    elif characters >= 4500 and characters < 4700:
        print("characters >= 4500 and characters < 4700")
        return 300
    elif characters >= 4200 and characters < 4500:
        print("characters >= 4200 and characters < 4500")
        return 280
    elif characters >= 4000 and characters < 4200:
        print("characters >= 4000 and characters < 4200")
        return 260
    elif characters >= 3500 and characters < 4000:
        print("characters >= 3500 and characters < 4000")
        return 240
    elif characters >= 3000 and characters < 3500:
        print("characters >= 3000 and characters < 3500")
        return 220
    elif characters >= 2500 and characters < 3000:
        print("characters >= 2500 and characters < 3000")
        return 200
    elif characters >= 2000 and characters < 2500:
        print("characters >= 2000 and characters < 2500")
        return 180
    elif characters >= 1500 and characters < 2000:
        print("characters >= 1500 and characters < 2000")
        return 160
    elif characters >= 1000 and characters < 1500:
        print("characters >= 1000 and characters < 1500")
        return 140
    elif characters >= 500 and characters < 1000:
        print("characters >= 500 and characters < 1000")
        return 120
    elif characters > 0 and characters < 500:
        print("characters > 0 and characters < 500")
        return 100
    return 80  # Fallback for 0 or invalid input

def calculate_resume_page_height(resume_data):
    """
    Calculate dynamic page height for resume PDF to fit all content on one page.
    
    Args:
        basic_details (dict): Basic information like name, email, phone, linkedin
        resume_data (dict): Complete resume data including work experience, skills, etc.
    
    Returns:
        int: Calculated page height in millimeters
    """
    
    # Base measurements 
    BASE_HEIGHT = 50  # Minimum height for basic sections
    LINE_HEIGHT_MM = 3.5  # Approximate line height in mm
    SECTION_SPACING = 1  # Space between sections
    MARGIN_HEIGHT = 0  # Top and bottom margins
    
    total_height = BASE_HEIGHT
    
    # Header section (name, contact info)
    header_lines = 3  # Name, contact info, spacing
    total_height += header_lines * LINE_HEIGHT_MM
    
    # Summary section
    if resume_data.get('Professional_Summary'):
        summary_chars = len(resume_data['Professional_Summary'])
        # Estimate lines based on character count
        summary_lines = max(1, summary_chars // 140 + 1)
        total_height += summary_lines * LINE_HEIGHT_MM + SECTION_SPACING
    
    # Skills section
    if resume_data.get('skills'):
        skills_lines = len(resume_data['skills'])  # One line per skill category
        total_height += skills_lines * LINE_HEIGHT_MM + SECTION_SPACING
    
    # Work Experience section (usually the largest)
    if resume_data.get('work_experiences'):
        for job in resume_data['work_experiences']:
            # Job header (company, location, position, dates) = 2 lines
            total_height += 2 * LINE_HEIGHT_MM
            
            # Job description bullets
            description_count = len(job.get('description', []))
            # Each bullet point, accounting for text wrapping
            for desc in job.get('description', []):
                desc_chars = len(desc)
                # Estimate lines per bullet
                bullet_lines = max(1, desc_chars // 120 + 1)
                total_height += bullet_lines * LINE_HEIGHT_MM
            
            # Spacing between jobs
            total_height += SECTION_SPACING
    
    # Projects section
    if resume_data.get('projects') and len(resume_data['projects']) > 0:
        for project in resume_data['projects']:
            # Project name = 1 line
            total_height += LINE_HEIGHT_MM
            
            # Technologies line (if any)
            if project.get('technologies') and len(project['technologies']) > 0:
                total_height += LINE_HEIGHT_MM
            
            # Project description bullets
            if project.get('description'):
                for desc_item in project['description']:
                    desc_chars = len(desc_item)
                    # Estimate lines per bullet (assuming ~75 chars per line for bullet text)
                    bullet_lines = max(1, desc_chars // 120 + 1)
                    total_height += bullet_lines * LINE_HEIGHT_MM
            
            total_height += SECTION_SPACING
    
    # Education section
    if resume_data.get('education'):
        for edu in resume_data['education']:
            # Each education entry = 2 lines (institution/location, degree/dates)
            total_height += 2 * LINE_HEIGHT_MM
        total_height += SECTION_SPACING
    
    # Certifications section
    if resume_data.get('certifications'):
        for cert in resume_data['certifications']:
            # Title + description
            cert_lines = 1  # Title line
            if cert.get('description'):
                desc_chars = len(cert['description'])
                cert_lines += max(1, desc_chars // 120 + 1)
            total_height += cert_lines * LINE_HEIGHT_MM
        total_height += SECTION_SPACING
    
    # Key Achievements section
    if resume_data.get('keyAchievements'):
        for achievement in resume_data['keyAchievements']:
            # Title + description
            achievement_lines = 1  # Title line
            if achievement.get('description'):
                desc_chars = len(achievement['description'])
                achievement_lines += max(1, desc_chars // 120 + 1)
            total_height += achievement_lines * LINE_HEIGHT_MM
        total_height += SECTION_SPACING
    
    # Add margins
    total_height += MARGIN_HEIGHT
    
    # Ensure minimum height and add buffer
    # min_height = 200  # Minimum A4-like height
    buffer = 5  # Extra buffer for safety
    
    # calculated_height = max(min_height, total_height + buffer)
    calculated_height = total_height + buffer
    print(calculated_height)
    # Round up to nearest 10mm for cleaner page size
    return int((calculated_height + 9) // 10 * 10)

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

    # Get the Total characters count of resume data and pass it to get_page_size function
    # complete_resume["pageSize"] = get_page_size(count_value_characters(resume_data))
    complete_resume["pageSize"] = calculate_resume_page_height(resume_data)

    # Add watermark to the resume if it is True need to decide if user is paid or free 
    complete_resume["watermark"] = False

    # Render template with the provided data
    html_content = templates.get_template("resume/resume_dynamic.html").render(
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
