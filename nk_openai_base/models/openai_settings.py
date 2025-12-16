# -*- coding: utf-8 -*-
# Copyright (C) 2025 NK Interactive
#
# This file is copyright Odoo SA, Odoo S.A. (formerly OpenERP) and others.
# License: OPL-1 (Odoo Proprietary License v1.0)
# See LICENSE file for full copyright and licensing details.

"""
OpenAI Settings Model
=====================

Configuration settings for OpenAI integration.
"""

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    """Configuration settings for OpenAI integration"""
    _inherit = 'res.config.settings'

    # OpenAI Configuration
    openai_enabled = fields.Boolean(
        string='Enable OpenAI Integration',
        config_parameter='nk_openai.enabled',
        default=False,
        help='Enable AI-powered features using OpenAI API'
    )
    
    openai_api_key = fields.Char(
        string='OpenAI API Key',
        config_parameter='nk_openai.api_key',
        help='Your OpenAI API key. Get it from https://platform.openai.com/api-keys',
        groups='base.group_system',
        copy=False,
    )
    
    openai_model = fields.Selection([
        # GPT-4 Series
        ('gpt-4', 'GPT-4 (10K TPM, 500 RPM)'),
        ('gpt-4-0613', 'GPT-4 0613 (10K TPM, 500 RPM)'),
        ('gpt-4-turbo', 'GPT-4 Turbo (30K TPM, 500 RPM)'),
        ('gpt-4-turbo-2024-04-09', 'GPT-4 Turbo 2024-04-09 (30K TPM, 500 RPM)'),
        ('gpt-4-turbo-preview', 'GPT-4 Turbo Preview (30K TPM, 500 RPM)'),
        ('gpt-4-0125-preview', 'GPT-4 0125 Preview (30K TPM, 500 RPM)'),
        ('gpt-4-1106-preview', 'GPT-4 1106 Preview (30K TPM, 500 RPM)'),
        
        # GPT-4.1 Series
        ('gpt-4.1-2025-04-14', 'GPT-4.1 (30K TPM, 500 RPM)'),
        ('gpt-4.1-mini-2025-04-14', 'GPT-4.1 Mini (200K TPM, 500 RPM)'),
        ('gpt-4.1-nano-2025-04-14', 'GPT-4.1 Nano (200K TPM, 500 RPM)'),
        
        # GPT-4o Series
        ('gpt-4o', 'GPT-4o (30K TPM, 500 RPM)'),
        ('gpt-4o-2024-05-13', 'GPT-4o 2024-05-13 (30K TPM, 500 RPM)'),
        ('gpt-4o-2024-08-06', 'GPT-4o 2024-08-06 (30K TPM, 500 RPM)'),
        ('gpt-4o-2024-11-20', 'GPT-4o 2024-11-20 (30K TPM, 500 RPM)'),
        ('gpt-4o-mini', 'GPT-4o Mini (200K TPM, 500 RPM)'),
        ('gpt-4o-mini-2024-07-18', 'GPT-4o Mini 2024-07-18 (200K TPM, 500 RPM)'),
        
        # GPT-5 Series
        ('gpt-5-2025-08-07', 'GPT-5 (500K TPM, 500 RPM)'),
        ('gpt-5-chat-latest', 'GPT-5 Chat Latest (30K TPM, 500 RPM)'),
        ('gpt-5-codex', 'GPT-5 Codex (500K TPM, 500 RPM)'),
        ('gpt-5-mini', 'GPT-5 Mini (500K TPM, 500 RPM)'),
        ('gpt-5-mini-2025-08-07', 'GPT-5 Mini 2025-08-07 (500K TPM, 500 RPM)'),
        ('gpt-5-nano', 'GPT-5 Nano (200K TPM, 500 RPM)'),
        ('gpt-5-nano-2025-08-07', 'GPT-5 Nano 2025-08-07 (200K TPM, 500 RPM)'),
        ('gpt-5-pro', 'GPT-5 Pro (30K TPM, 500 RPM)'),
        ('gpt-5-pro-2025-10-06', 'GPT-5 Pro 2025-10-06 (30K TPM, 500 RPM)'),
        
        # GPT-5.1 Series
        ('gpt-5.1-2025-11-13', 'GPT-5.1 (500K TPM, 500 RPM)'),
        ('gpt-5.1-chat-latest', 'GPT-5.1 Chat Latest (30K TPM, 500 RPM)'),
        ('gpt-5.1-codex', 'GPT-5.1 Codex (500K TPM, 500 RPM)'),
        ('gpt-5.1-codex-max', 'GPT-5.1 Codex Max (500K TPM, 500 RPM)'),
        ('gpt-5.1-codex-mini', 'GPT-5.1 Codex Mini (200K TPM, 500 RPM)'),
        
        # GPT-5.2 Series
        ('gpt-5.2', 'GPT-5.2 (500K TPM, 500 RPM)'),
        ('gpt-5.2-2025-12-11', 'GPT-5.2 2025-12-11 (500K TPM, 500 RPM)'),
        ('gpt-5.2-chat-latest', 'GPT-5.2 Chat Latest (500K TPM, 500 RPM)'),
        ('gpt-5.2-pro', 'GPT-5.2 Pro (500K TPM, 500 RPM)'),
        ('gpt-5.2-pro-2025-12-11', 'GPT-5.2 Pro 2025-12-11 (500K TPM, 500 RPM)'),
        
        # GPT-3.5 Series
        ('gpt-3.5-turbo', 'GPT-3.5 Turbo (200K TPM, 500 RPM)'),
        ('gpt-3.5-turbo-0125', 'GPT-3.5 Turbo 0125 (200K TPM, 500 RPM)'),
        ('gpt-3.5-turbo-1106', 'GPT-3.5 Turbo 1106 (200K TPM, 500 RPM)'),
        ('gpt-3.5-turbo-16k', 'GPT-3.5 Turbo 16K (200K TPM, 500 RPM)'),
        ('gpt-3.5-turbo-instruct', 'GPT-3.5 Turbo Instruct (90K TPM, 3500 RPM)'),
        ('gpt-3.5-turbo-instruct-0914', 'GPT-3.5 Turbo Instruct 0914 (90K TPM, 3500 RPM)'),
        
        # O Series (Reasoning Models)
        ('o1', 'O1 (30K TPM, 500 RPM)'),
        ('o1-2024-12-17', 'O1 2024-12-17 (30K TPM, 500 RPM)'),
        ('o1-pro', 'O1 Pro (30K TPM, 500 RPM)'),
        ('o1-pro-2025-03-19', 'O1 Pro 2025-03-19 (30K TPM, 500 RPM)'),
        ('o3', 'O3 (30K TPM, 500 RPM)'),
        ('o3-2025-04-16', 'O3 2025-04-16 (30K TPM, 500 RPM)'),
        ('o3-mini', 'O3 Mini (200K TPM, 500 RPM)'),
        ('o3-mini-2025-01-31', 'O3 Mini 2025-01-31 (200K TPM, 500 RPM)'),
        ('o4-mini', 'O4 Mini (200K TPM, 500 RPM)'),
        ('o4-mini-2025-04-16', 'O4 Mini 2025-04-16 (200K TPM, 500 RPM)'),
        
        # Text Models
        ('babbage-002', 'Babbage-002 (250K TPM, 3000 RPM)'),
        ('davinci-002', 'Davinci-002 (250K TPM, 3000 RPM)'),
        ('text-embedding-3-large', 'Text Embedding 3 Large (10M TPM, 3000 RPM)'),
        ('text-embedding-3-small', 'Text Embedding 3 Small (10M TPM, 3000 RPM)'),
        ('text-embedding-ada-002', 'Text Embedding Ada 002 (10M TPM, 3000 RPM)'),
        
        # Other Models
        ('chatgpt-4o-latest', 'ChatGPT-4o Latest (500K TPM, 200 RPM)'),
        ('codex-mini-latest', 'Codex Mini Latest (200K TPM, 500 RPM)'),
    ], string='OpenAI Model',
        config_parameter='nk_openai.model',
        default='gpt-4',
        help='Select the OpenAI model to use. Rate limits shown as (TPM, RPM). TPM = Tokens Per Minute, RPM = Requests Per Minute. Higher TPM/RPM = faster processing but may cost more.'
    )
    
    openai_model_custom = fields.Char(
        string='Custom Model Name',
        config_parameter='nk_openai.model_custom',
        help='Enter a custom model name if not listed above. Leave empty to use the selected model from the dropdown. This is useful for custom deployments or new model versions.'
    )
    
    openai_base_url = fields.Char(
        string='OpenAI Base URL',
        config_parameter='nk_openai.base_url',
        default='https://api.openai.com/v1',
        help='Base URL for OpenAI API. Use default for OpenAI, or custom URL for compatible APIs (e.g., Ollama, LocalAI)'
    )
    
    openai_timeout = fields.Integer(
        string='API Timeout (seconds)',
        config_parameter='nk_openai.timeout',
        default=60,
        help='Timeout in seconds for OpenAI API requests'
    )
    
    openai_max_tokens = fields.Integer(
        string='Max Tokens',
        config_parameter='nk_openai.max_tokens',
        default=2000,
        help='Maximum number of tokens in the API response'
    )
    
    openai_organization_id = fields.Char(
        string='OpenAI Organization ID',
        config_parameter='nk_openai.organization_id',
        help='Optional: Organization ID for API requests. Found in your organization settings page. Leave empty if not using multiple organizations.'
    )
    
    openai_project_id = fields.Char(
        string='OpenAI Project ID',
        config_parameter='nk_openai.project_id',
        help='Optional: Project ID for API requests. Found in your project general settings. Leave empty if not using projects.'
    )
    
    openai_api_type = fields.Selection([
        ('chat', 'Chat Completions API (/v1/chat/completions)'),
        ('responses', 'Responses API (/v1/responses)'),
    ], string='API Type',
        config_parameter='nk_openai.api_type',
        default='responses',
        help='Choose which OpenAI API to use. Responses API supports advanced features like tools, file search, and structured outputs. Chat Completions API is the traditional API.'
    )
    
    def set_values(self):
        """Save configuration values with validation"""
        super(ResConfigSettings, self).set_values()
        
        # Validate API key if enabled
        if self.openai_enabled and not self.openai_api_key:
            raise UserError('OpenAI API key is required when OpenAI integration is enabled.')
        
        # Validate base URL format
        if self.openai_base_url:
            base_url = self.openai_base_url.strip()
            if base_url:
                # Remove trailing slash for consistency
                base_url = base_url.rstrip('/')
                # Basic URL validation
                if not base_url.startswith(('http://', 'https://')):
                    raise UserError('Base URL must start with http:// or https://')
                if '://' not in base_url or not base_url.split('://')[1]:
                    raise UserError('Invalid Base URL format. Must be a valid URL (e.g., https://api.openai.com/v1)')
        
        # Validate timeout and max_tokens
        if self.openai_timeout and self.openai_timeout < 10:
            raise UserError('API timeout must be at least 10 seconds.')
        if self.openai_max_tokens and self.openai_max_tokens < 100:
            raise UserError('Max tokens must be at least 100.')
        
        # Settings updated successfully

