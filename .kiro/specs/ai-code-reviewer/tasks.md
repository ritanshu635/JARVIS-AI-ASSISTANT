# Implementation Plan

- [x] 1. Setup dependencies and environment configuration



  - Add OpenAI API key to `.env` file configuration
  - Install required packages: `pip install openai pytesseract pillow`
  - Configure pytesseract path for Windows OCR functionality
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 2. Enhance AI Router with OpenAI integration


  - Add OpenAI client initialization to `engine/ai_router.py`
  - Implement `analyze_code_with_openai()` method in AIRouter class
  - Add error handling for OpenAI API calls following existing patterns
  - _Requirements: 5.1, 5.2_

- [x] 3. Add code help task classification


  - Extend `classify_intent()` method in AIRouter to recognize "help with code" commands
  - Add `HELP_WITH_CODE` task type to classification system
  - Test classification with various voice command variations
  - _Requirements: 1.1, 1.2_

- [x] 4. Implement screenshot and OCR functionality


  - Create `extract_code_from_screen()` method in JarvisAssistant class
  - Add screenshot capture using existing pyautogui integration
  - Implement OCR text extraction focusing on right side of screen (code editor area)
  - Add text cleaning and formatting for extracted code
  - _Requirements: 1.1, 1.2_

- [x] 5. Create main code analysis method


  - Add `help_with_code()` method to JarvisAssistant class following existing method patterns
  - Integrate screenshot capture, OCR extraction, and OpenAI analysis
  - Format OpenAI response to extract exactly 3 lines of mistake explanation only
  - Use existing `speak()` function to voice the 3-line analysis (no code fixing)
  - Add proper error handling for each step of the analysis pipeline
  - _Requirements: 1.3, 1.4, 1.5_

- [x] 6. Add task execution integration


  - Add `HELP_WITH_CODE` case to existing `execute_task()` method in JarvisAssistant
  - Follow same pattern as existing tasks like `TAKE_SCREENSHOT` and `DESCRIBE_SCREEN`
  - Call `help_with_code()` method and speak only the 3-line mistake analysis
  - Ensure proper async/await handling consistent with existing code
  - _Requirements: 1.5_

- [x] 7. Implement confirmation response flow

  - Add recognition for "thank you jarvis my code is running successfully now" command in classification
  - Create appropriate response "that's great to hear sir how else can i assist you?"
  - Ensure normal command listening resumes after confirmation
  - Test integration with existing voice recognition loop following other features pattern
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 8. Add comprehensive error handling


  - Implement graceful fallbacks for OCR extraction failures
  - Add proper error messages for OpenAI API issues (rate limits, network errors)
  - Handle screenshot capture failures and editor focus problems
  - Ensure all errors are communicated via existing speak() function
  - _Requirements: 5.3, 4.3_

- [x] 9. Test end-to-end functionality


  - Test complete "jarvis help me with my code" workflow (analysis only, no auto-fixing)
  - Verify OCR accuracy with C++ code examples
  - Test 3-line mistake explanation via voice
  - Validate confirmation flow "thank you jarvis" → "that's great to hear sir how else can i assist you?"
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 3.1, 3.2, 3.3_

- [x] 10. Ensure existing functionality preservation



  - Verify all existing JARVIS commands continue to work unchanged
  - Test that no existing features in `added` folder are modified
  - Confirm integration doesn't break existing voice recognition or AI routing
  - Validate that new feature integrates seamlessly with current architecture
  - _Requirements: 4.1, 4.2, 4.3, 4.4_