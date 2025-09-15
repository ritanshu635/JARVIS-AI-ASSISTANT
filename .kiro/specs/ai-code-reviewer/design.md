# Design Document

## Overview

The AI Code Reviewer & Auto-Fixer feature will be integrated into the existing `final_jarvis.py` system following the same architectural pattern as other features like `TAKE_SCREENSHOT`, `DESCRIBE_SCREEN`, etc. The feature will add a new task type `HELP_WITH_CODE` that captures screenshots, uses OCR to extract code, analyzes it with OpenAI API, and automatically fixes the code in the editor.

## Architecture

### Integration Points

The feature integrates with the existing JARVIS architecture at these points:

1. **AI Router Integration**: Extends the existing `AIRouter` class to include OpenAI API calls
2. **Task Classification**: Adds new task type `HELP_WITH_CODE` to the AI classification system  
3. **Command Processing**: Follows the same pattern as existing tasks in `execute_task()` method
4. **Voice Response**: Uses existing `speak()` function for conversational responses

### Component Structure

```
final_jarvis.py
├── JarvisAssistant class
│   ├── execute_task() - Add HELP_WITH_CODE case
│   ├── help_with_code() - New method for code analysis
│   ├── extract_code_from_screen() - OCR functionality
│   ├── analyze_code_with_openai() - OpenAI API integration
│   └── auto_fix_code() - Automated code replacement
├── AIRouter (engine/ai_router.py)
│   └── Enhanced with OpenAI client initialization
└── Dependencies
    ├── pyautogui (existing) - Screen capture & automation
    ├── pytesseract (new) - OCR for code extraction
    ├── openai (new) - Code analysis API
    └── PIL (new) - Image processing
```

## Components and Interfaces

### 1. Task Classification Enhancement

**Location**: `AIRouter.classify_intent()` method
**Enhancement**: Add recognition for "help with code" commands

### 2. Code Analysis Pipeline

**Method**: `help_with_code()`
**Flow**:
1. Take screenshot using existing `pyautogui.screenshot()`
2. Extract code from right side of screen using OCR
3. Send code to OpenAI API for analysis
4. Parse response for mistakes and corrected code
5. Provide 3-line explanation via `speak()`
6. Auto-replace code using `pyautogui` automation

### 3. OCR Code Extraction

**Method**: `extract_code_from_screen(screenshot)`
**Implementation**:
- Crop screenshot to focus on code editor area (right side)
- Use pytesseract to extract text
- Clean and format extracted code
- Handle common OCR errors in code context

### 4. OpenAI Integration

**Method**: `analyze_code_with_openai(code_text)`
**API Configuration**:
- Use existing environment variable pattern from `.env`
- Add `OPENAI_API_KEY` to environment configuration
- Implement error handling and fallback responses

### 5. Automated Code Fixing

**Method**: `auto_fix_code(corrected_code)`
**Automation Steps**:
1. `pyautogui.hotkey('ctrl', 'a')` - Select all code
2. `pyautogui.press('backspace')` - Delete existing code  
3. `pyautogui.write(corrected_code)` - Type corrected code
4. Handle timing and focus issues

## Data Models

### Code Analysis Request
```python
{
    "code_text": str,           # Extracted code from screen
    "language": str,            # Detected programming language
    "timestamp": datetime,      # When analysis was requested
    "screenshot_path": str      # Path to captured screenshot
}
```

### OpenAI Response Structure
```python
{
    "mistakes": [str],          # List of 3 mistake explanations
    "corrected_code": str,      # Fixed version of code
    "confidence": float,        # Analysis confidence score
    "language_detected": str    # Programming language identified
}
```

## Error Handling

### OCR Extraction Errors
- **Issue**: Poor text recognition from screenshot
- **Handling**: Retry with different image preprocessing
- **Fallback**: Ask user to manually paste code

### OpenAI API Errors
- **Issue**: API key invalid, rate limits, network issues
- **Handling**: Use existing error patterns from `AIRouter`
- **Fallback**: Provide generic coding tips without specific analysis

### Code Automation Errors
- **Issue**: Focus issues, timing problems with editor
- **Handling**: Add delays and focus verification
- **Fallback**: Copy corrected code to clipboard and inform user

## Testing Strategy

### Unit Tests
1. **OCR Accuracy**: Test code extraction with sample screenshots
2. **OpenAI Integration**: Mock API responses for different code scenarios
3. **Automation Reliability**: Test keyboard/mouse automation sequences
4. **Error Handling**: Verify graceful degradation for each failure mode

### Integration Tests
1. **End-to-End Flow**: Complete "help with code" command execution
2. **Voice Response Timing**: Ensure proper speech synthesis timing
3. **Editor Compatibility**: Test with different code editors
4. **Multi-language Support**: Test with various programming languages