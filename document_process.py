import asyncio
import os
import uuid
from weasyprint import HTML, CSS
from fastapi.templating import Jinja2Templates


async def generate_resume_from_json(resume_data): 
    templates = Jinja2Templates(directory="templates")
    
    PDF_DIR = "generated_pdfs"
    os.makedirs(PDF_DIR, exist_ok=True)
    
    # Generate a unique filename for the PDF
    filename = f"resume_{uuid.uuid4().hex}.pdf"
    pdf_path = os.path.join(PDF_DIR, filename)
    
    # First, ensure resume_data is a dictionary
    if not isinstance(resume_data, dict):
        raise TypeError("resume_data must be a dictionary")
    
    # Render template with the provided data
    html_content = templates.get_template("resume/resume.html").render(
        resume=resume_data
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
