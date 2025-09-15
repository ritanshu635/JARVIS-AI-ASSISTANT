#!/usr/bin/env python3
"""
Create a test PDF file for testing PDF reading functionality
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_test_pdf():
    """Create a test PDF file named 'amazon.pdf'"""
    
    # Create PDF in Desktop folder
    desktop_path = os.path.expanduser("~/Desktop")
    pdf_path = os.path.join(desktop_path, "amazon.pdf")
    
    # Create PDF content
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Add content to the PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Amazon Business Report")
    
    c.setFont("Helvetica", 12)
    y_position = height - 150
    
    content = [
        "Executive Summary:",
        "",
        "Amazon is a multinational technology company focusing on e-commerce,",
        "cloud computing, digital streaming, and artificial intelligence.",
        "",
        "Key Points:",
        "• Founded by Jeff Bezos in 1994",
        "• Headquarters in Seattle, Washington",
        "• One of the world's largest online retailers",
        "• Amazon Web Services (AWS) is a major cloud provider",
        "• Prime membership program with over 200 million subscribers",
        "",
        "Financial Performance:",
        "Amazon has shown consistent growth over the years with revenue",
        "reaching hundreds of billions of dollars annually.",
        "",
        "Future Outlook:",
        "The company continues to expand into new markets including",
        "healthcare, logistics, and space exploration through Blue Origin.",
    ]
    
    for line in content:
        c.drawString(100, y_position, line)
        y_position -= 20
    
    c.save()
    print(f"✅ Created test PDF: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    try:
        create_test_pdf()
    except ImportError:
        print("❌ reportlab not installed. Installing...")
        import subprocess
        subprocess.run(["pip", "install", "reportlab"])
        create_test_pdf()