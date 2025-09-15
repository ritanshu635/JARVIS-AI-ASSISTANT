#!/usr/bin/env python3
"""
Test script for new PDF reading and screen description features
"""

import asyncio
from engine.pdf_reader import PDFReader
from engine.screen_analyzer import ScreenAnalyzer

async def test_pdf_reader():
    """Test PDF reading functionality"""
    print("🧪 Testing PDF Reader...")
    
    pdf_reader = PDFReader()
    
    # Test finding a PDF (this will search for any PDF in common directories)
    test_filename = "test"  # Will look for any PDF with "test" in the name
    
    print(f"Searching for PDF with name containing: {test_filename}")
    pdf_path = pdf_reader.find_pdf(test_filename)
    
    if pdf_path:
        print(f"✅ Found PDF: {pdf_path}")
        
        # Test reading the PDF
        text = pdf_reader.read_pdf(test_filename)
        if text:
            print(f"✅ Successfully read PDF ({len(text)} characters)")
            print(f"First 200 characters: {text[:200]}...")
        else:
            print("❌ Could not read PDF content")
    else:
        print("❌ No PDF found for testing")
        print("💡 To test PDF reading, place a PDF file in your Desktop, Documents, or Downloads folder")

async def test_screen_analyzer():
    """Test screen description functionality"""
    print("\n🧪 Testing Screen Analyzer...")
    
    try:
        screen_analyzer = ScreenAnalyzer()
        
        print("Taking screenshot and analyzing...")
        description = screen_analyzer.get_screen_text_description()
        
        if description:
            print(f"✅ Screen analysis successful!")
            print(f"Description: {description}")
        else:
            print("❌ Screen analysis failed")
            print("💡 Make sure you have a valid OpenAI API key")
            
    except Exception as e:
        print(f"❌ Error testing screen analyzer: {e}")

async def main():
    """Run all tests"""
    print("🚀 Testing New JARVIS Features\n")
    
    await test_pdf_reader()
    await test_screen_analyzer()
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    asyncio.run(main())