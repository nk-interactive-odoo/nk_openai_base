# -*- coding: utf-8 -*-
# Copyright (C) 2025 NK Interactive
#
# This file is part of Odoo. See LICENSE file for full copyright and licensing details.
# License: LGPL-3 (GNU Lesser General Public License v3.0)
# See LICENSE file for full copyright and licensing details.

{
    'name': 'NK OpenAI Base',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Centralized OpenAI API configuration and service for NK modules (FREE)',
    'description': """
NK OpenAI Base - Centralized OpenAI Integration for Odoo (FREE)
================================================================

This FREE base module provides centralized OpenAI API configuration and service for all NK modules. It eliminates the need for each module to manage its own OpenAI settings, providing a single point of configuration and a unified service interface.

⚠️ CRITICAL REQUIREMENTS - READ BEFORE INSTALLATION
----------------------------------------------------
REQUIRES a valid OpenAI API key to function.
OpenAI usage costs are NOT included (this module is FREE, but API usage is paid).
You are responsible for all OpenAI API costs billed directly by OpenAI.
Without valid API credits, dependent modules will NOT function.
Get your API key from: https://platform.openai.com/api-keys

🔒 DATA PRIVACY & SECURITY
--------------------------
Data is sent externally to OpenAI's servers via HTTPS/TLS encryption.
Only metadata (field names, types) and queries are sent.
Actual database records are NEVER sent to OpenAI.
Review OpenAI's Privacy Policy: https://openai.com/policies/privacy-policy

✅ COMPATIBILITY
----------------
Compatible with Odoo Community v17.0 (fully tested and supported)
Enterprise edition NOT required
Also compatible with Odoo Enterprise v17.0

KEY FEATURES
------------
🔑 Centralized API Key Management
   - Single configuration point for all NK modules
   - Secure storage of API keys
   - Master enable/disable switch

⚙️ Comprehensive Configuration
   - Support for 60+ OpenAI models with rate limit information
   - Chat Completions API and Responses API support
   - Organization and Project ID support for multi-org setups
   - Custom model name support for new model versions
   - Configurable timeout and token limits

🔌 Flexible API Support
   - OpenAI official API (default)
   - OpenAI-compatible APIs (Ollama, LocalAI, etc.)
   - Custom base URL configuration

🛡️ Enterprise-Grade Reliability
   - Uses official OpenAI Python package
   - Comprehensive error handling with detailed messages
   - Rate limit handling with retry logic
   - Request ID tracking for debugging

📊 Model Selection
   - 60+ pre-configured models
   - Rate limit information for each model
   - Custom model name support
   - Model compatibility validation

CONFIGURATION
-------------
Navigate to: Settings > OpenAI Integration

Required Settings:
* Enable OpenAI Integration - Master switch
* OpenAI API Key - Your API key (stored securely)

Optional Settings:
* OpenAI Model - Select from 60+ models (default: gpt-4)
* Custom Model Name - For new model versions
* OpenAI Base URL - Default or custom endpoint
* API Type - Chat Completions or Responses API
* API Timeout - Request timeout in seconds (default: 60)
* Max Tokens - Maximum tokens in response (default: 2000)
* Organization ID - Optional, for multi-org setups
* Project ID - Optional, for project-based organization

TECHNICAL REQUIREMENTS
----------------------
* Python package: openai (install with: pip install openai)
* Valid OpenAI API key (required for functionality)
* Active OpenAI account with available credits

FOR DEVELOPERS
--------------
This module provides a service interface that other NK modules can use:

from odoo import api

# Get OpenAI service
openai_service = self.env['nk.openai.service']

# Get configuration
config = openai_service.get_openai_config()

# Call OpenAI API
response = openai_service.call_openai(
    prompt="Your prompt here",
    system_message="You are a helpful assistant"
)

SUPPORTED MODELS
----------------
* GPT-4 series (gpt-4, gpt-4-turbo, gpt-4o, etc.)
* GPT-3.5 series (gpt-3.5-turbo, etc.)
* GPT-5 series (gpt-5, gpt-5-mini, etc.)
* O1 series (o1, o1-pro, o3, o3-mini, etc.)
* And 50+ more models with rate limit information

SUPPORT & DOCUMENTATION
-----------------------
This is a FREE base module required by other NK modules.
Support: nk.interactive.odoo@gmail.com
    """,
    'external_dependencies': {
        'python': ['openai'],
    },
    'author': 'NK Interactive',
    'support': 'nk.interactive.odoo@gmail.com',
    'website': 'https://www.odoo.com',
    'license': 'LGPL-3',
    'price': 0.00,
    'currency': 'EUR',
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/openai_settings_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

