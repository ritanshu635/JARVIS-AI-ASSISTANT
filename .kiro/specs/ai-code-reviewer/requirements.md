# Requirements Document

## Introduction

This feature adds AI-powered code analysis and auto-correction capabilities to the existing Jarvis voice assistant. When the user says "Jarvis help me with my code", Jarvis will take a screenshot of the screen, analyze the code visible in the editor (right side of screen), identify errors using OpenAI API, provide a concise 3-line explanation of mistakes, and automatically replace the incorrect code with the corrected version. The feature maintains all existing Jarvis functionality while adding this new code assistance capability.

## Requirements

### Requirement 1

**User Story:** As a developer using Jarvis, I want to ask for code help via voice command so that I can get instant feedback on my coding mistakes without interrupting my workflow.

#### Acceptance Criteria

1. WHEN the user says "Jarvis help me with my code" THEN the system SHALL capture a screenshot of the current screen
2. WHEN the screenshot is captured THEN the system SHALL extract code text from the right side of the screen using OCR
3. WHEN code is extracted THEN the system SHALL send it to OpenAI API for analysis
4. WHEN OpenAI responds THEN the system SHALL provide exactly 3 lines explaining the mistakes
5. WHEN explanation is complete THEN the system SHALL say "hopefully the code will run now"

### Requirement 2

**User Story:** As a developer, I want Jarvis to automatically fix my code after analysis so that I don't have to manually type corrections.

#### Acceptance Criteria

1. WHEN code analysis is complete THEN the system SHALL automatically select all code in the editor using Ctrl+A
2. WHEN code is selected THEN the system SHALL delete it using backspace
3. WHEN code is deleted THEN the system SHALL paste the corrected code from OpenAI response
4. WHEN code replacement is complete THEN the system SHALL wait for user confirmation

### Requirement 3

**User Story:** As a developer, I want to confirm successful code execution and continue using Jarvis normally so that the workflow feels natural and conversational.

#### Acceptance Criteria

1. WHEN the user says "thank you jarvis my code is running successfully now" THEN the system SHALL respond with "that's great to hear sir how else can i assist you?"
2. WHEN the confirmation response is given THEN the system SHALL resume normal voice command listening
3. WHEN resuming normal operation THEN the system SHALL maintain all existing Jarvis functionality without any changes

### Requirement 4

**User Story:** As a user of the existing Jarvis system, I want all current features to remain unchanged so that my existing workflows are not disrupted.

#### Acceptance Criteria

1. WHEN the new code analysis feature is added THEN all existing Jarvis commands SHALL continue to work exactly as before
2. WHEN the system is running THEN no existing functionality in the "added" folder SHALL be modified or removed
3. WHEN new code is added THEN it SHALL integrate with existing voice recognition and response systems
4. WHEN the feature is inactive THEN the system SHALL behave identically to the current implementation

### Requirement 5

**User Story:** As a developer, I want the code analysis to work with my existing OpenAI API key so that I don't need additional setup or configuration.

#### Acceptance Criteria

1. WHEN the system needs to analyze code THEN it SHALL use the existing OpenAI API key from the current Jarvis configuration
2. WHEN sending requests to OpenAI THEN the system SHALL use GPT-4 or the configured model for accurate code analysis
3. WHEN API calls are made THEN the system SHALL handle errors gracefully and inform the user if analysis fails
4. WHEN the feature is used THEN it SHALL respect existing API rate limits and error handling patterns