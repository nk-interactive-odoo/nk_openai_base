## Module <nk_openai_base>

#### 16.12.2025
#### Version 17.0.1.0.0
##### ADD
- Initial release of NK OpenAI Base module
- Centralized OpenAI API configuration and service
- Support for multiple OpenAI models (60+ models with rate limit information)
- OpenAI API key management in system parameters
- Support for OpenAI-compatible APIs (Ollama, LocalAI, etc.)
- Official OpenAI Python package integration
- Support for Chat Completions API (/v1/chat/completions)
- Support for Responses API (/v1/responses) with advanced features
- Organization and Project ID support for multi-org setups
- Custom model name support for new model versions
- Configurable timeout and token limits
- Comprehensive error handling with detailed messages
- Rate limit error messages with TPM/RPM details and actionable advice
- Context length exceeded error handling
- Request ID tracking for debugging

##### FIX
- Fixed URL normalization and validation
- Fixed base URL joining with endpoints
- Improved error messages for better debugging
- Fixed Responses API input parameter formatting
- Fixed model compatibility validation

##### IMPROVE
- Enhanced rate limit error messages with TPM/RPM details
- Better context length exceeded error handling
- Improved API response parsing
- Optimized error logging (removed debug logs, kept essential errors)
- Code cleanup for production readiness

##### REMOVE
- Removed manual requests library usage (now using official OpenAI package)
- Removed temperature parameter (not needed for most use cases)
- Removed debug logging and pprint statements

