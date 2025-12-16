# -*- coding: utf-8 -*-
# Copyright (C) 2025 NK Interactive
#
# This file is copyright Odoo SA, Odoo S.A. (formerly OpenERP) and others.
# License: OPL-1 (Odoo Proprietary License v1.0)
# See LICENSE file for full copyright and licensing details.

"""
OpenAI Service
==============

Base service for OpenAI API integration.
Can be used by any module that needs AI functionality.
"""

import json
import logging
import datetime
from urllib.parse import urlparse
from odoo import models, api
from odoo.exceptions import UserError

try:
    from openai import OpenAI
    from openai import APIError, RateLimitError, APIConnectionError, APITimeoutError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

_logger = logging.getLogger(__name__)

if not OPENAI_AVAILABLE:
    _logger.warning("OpenAI Python package not installed. Install it with: pip install openai")


class OpenAIService(models.AbstractModel):
    """
    Abstract service for OpenAI API integration
    Provides base functionality for AI-powered features
    """
    _name = 'nk.openai.service'
    _description = 'OpenAI Service'

    @api.model
    def get_openai_config(self):
        """
        Get OpenAI configuration from system parameters
        Returns: dict with OpenAI settings
        """
        config = self.env['ir.config_parameter'].sudo()
        # Use custom model if provided, otherwise use selected model
        custom_model = config.get_param('nk_openai.model_custom', '').strip()
        selected_model = config.get_param('nk_openai.model', 'gpt-4')
        model = custom_model if custom_model else selected_model
        
        return {
            'enabled': config.get_param('nk_openai.enabled', 'False') == 'True',
            'api_key': config.get_param('nk_openai.api_key', ''),
            'model': model,
            'base_url': config.get_param('nk_openai.base_url', 'https://api.openai.com/v1'),
            'timeout': int(config.get_param('nk_openai.timeout', '60')),
            'max_tokens': int(config.get_param('nk_openai.max_tokens', '2000')),
            'organization_id': config.get_param('nk_openai.organization_id', '').strip() or None,
            'project_id': config.get_param('nk_openai.project_id', '').strip() or None,
            'api_type': config.get_param('nk_openai.api_type', 'chat'),
        }

    def _get_openai_client(self, config):
        """
        Create and configure OpenAI client
        
        Args:
            config: Configuration dict from get_openai_config()
            
        Returns:
            OpenAI: Configured OpenAI client instance
        """
        if not OPENAI_AVAILABLE:
            raise UserError(
                'OpenAI Python package is not installed. '
                'Please install it with: pip install openai'
            )
        
        # Prepare client configuration
        client_kwargs = {
            'api_key': config['api_key'],
            'timeout': config['timeout'],
        }
        
        # Handle custom base URL (for Ollama, LocalAI, etc.)
        base_url = config['base_url'].strip().rstrip('/')
        if base_url and base_url != 'https://api.openai.com/v1':
            client_kwargs['base_url'] = base_url
        
        # Add organization and project if configured
        if config.get('organization_id'):
            client_kwargs['organization'] = config['organization_id']
        if config.get('project_id'):
            client_kwargs['project'] = config['project_id']
        
        return OpenAI(**client_kwargs)
    
    @api.model
    def call_openai(self, prompt, system_message=None):
        """
        Call OpenAI API with a prompt using the official OpenAI Python package
        
        Args:
            prompt: The user prompt to send
            system_message: Optional system message (default: generic assistant)
        
        Returns:
            str: OpenAI response text
        """
        config = self.get_openai_config()
        if not config['enabled']:
            raise UserError('OpenAI is not enabled. Please configure OpenAI API key in Settings.')
        
        if not config['api_key']:
            raise UserError('OpenAI API key is not configured. Please set it in Settings.')
        
        if not OPENAI_AVAILABLE:
            raise UserError(
                'OpenAI Python package is not installed. '
                'Please install it with: pip install openai'
            )
        
        try:
            client = self._get_openai_client(config)
            api_type = config.get('api_type', 'chat')
            
            if api_type == 'responses':
                # Use Responses API
                params = {
                    'model': config['model'],
                    'input': str(prompt),
                    'instructions': system_message or 'You are a helpful AI assistant.',
                    'max_output_tokens': config['max_tokens'],
                }
                
                try:
                    response = client.responses.create(**params)
                except APIError as e:
                    # Handle API errors with better messages
                    error_msg = str(e)
                    error_code = None
                    
                    # Try to extract error details
                    if hasattr(e, 'response') and e.response:
                        try:
                            error_body = e.response.json() if hasattr(e.response, 'json') else {}
                            if isinstance(error_body, dict) and 'error' in error_body:
                                error_obj = error_body['error']
                                if isinstance(error_obj, dict):
                                    error_code = error_obj.get('code')
                                    error_msg = error_obj.get('message', error_msg)
                        except:
                            pass
                        
                        if hasattr(e.response, 'status_code'):
                            if e.response.status_code == 400:
                                if error_code == 'context_length_exceeded':
                                    raise UserError(
                                        f'Input exceeds the context window of {config["model"]}.\n\n'
                                        'The model information (fields, relationships) is too large for this model.\n\n'
                                        'Suggestions:\n'
                                        '- Use a model with a larger context window (e.g., gpt-4.1, gpt-5, o1, o3, o4)\n'
                                        '- Try switching to "Chat Completions API" in Settings\n'
                                        '- Select a simpler model with fewer fields\n'
                                        '- Reduce the depth of field discovery in your report request'
                                    )
                                else:
                                    raise UserError(
                                        f'OpenAI Responses API error: {error_msg}\n\n'
                                        f'Model: {config["model"]}\n\n'
                                        'The selected model may not support the Responses API or the requested parameters.\n'
                                        'Try switching to "Chat Completions API" in Settings, '
                                        'or use a compatible model (gpt-4.1, gpt-5, o1, o3, o4).'
                                    )
                    raise UserError(f'OpenAI API error: {error_msg}')
                
                # Use output_text property - aggregates all text outputs from the model
                # This is the recommended way per OpenAI documentation
                if hasattr(response, 'output_text') and response.output_text:
                    result = str(response.output_text).strip()
                    return result
                
                # Fallback: manually extract from output.items if output_text not available
                if hasattr(response, 'output') and response.output:
                    output = response.output
                    message_content = ''
                    
                    if hasattr(output, 'items'):
                        for item in output.items:
                            if hasattr(item, 'type'):
                                if item.type == 'message' and hasattr(item, 'content'):
                                    for content_item in item.content:
                                        if hasattr(content_item, 'type') and content_item.type == 'output_text':
                                            if hasattr(content_item, 'text'):
                                                message_content += content_item.text
                                elif item.type == 'output_text' and hasattr(item, 'text'):
                                    message_content += item.text
                    
                    if message_content:
                        return message_content
                
                # Last resort: convert to string
                result = str(response)
                return result
                    
            else:
                # Use Chat Completions API
                messages = []
                if system_message:
                    messages.append({
                        'role': 'system',
                        'content': system_message
                    })
                else:
                    messages.append({
                        'role': 'system',
                        'content': 'You are a helpful AI assistant.'
                    })
                
                messages.append({
                    'role': 'user',
                    'content': prompt
                })
                
                response = client.chat.completions.create(
                    model=config['model'],
                    messages=messages,
                    max_tokens=config['max_tokens'],
                )
                
                # Extract message content
                if hasattr(response, 'choices') and len(response.choices) > 0:
                    choice = response.choices[0]
                    if hasattr(choice, 'message'):
                        message = choice.message
                        if hasattr(message, 'content'):
                            return message.content
                
                # Fallback
                return str(response)
                
        except RateLimitError as e:
            # Handle rate limit errors - OpenAI package provides good error messages
            error_msg = str(e)
            
            # Try to extract rate limit info from error if available
            rate_limit_info = {}
            if hasattr(e, 'response') and e.response:
                if hasattr(e.response, 'headers'):
                    rate_limit_info = self._extract_rate_limit_info(e.response.headers)
            
            rate_limit_message = self._format_rate_limit_message(rate_limit_info) if rate_limit_info else ""
            
            full_error = f"OpenAI API rate limit exceeded.\n{error_msg}"
            if rate_limit_message:
                full_error += f"\n\nCurrent Rate Limits:\n{rate_limit_message}"
            full_error += (
                "\n\nPlease wait a few minutes before trying again, or consider:\n"
                "- Upgrading your OpenAI plan for higher limits\n"
                "- Reducing the frequency of requests\n"
                "- Using a model with higher rate limits"
            )
            
            raise UserError(full_error)
            
        except APITimeoutError:
            raise UserError('OpenAI API request timed out. Please try again or increase the timeout in Settings.')
            
        except APIConnectionError:
            raise UserError('Failed to connect to OpenAI API. Please check your internet connection.')
            
        except APIError as e:
            error_msg = str(e)
            error_code = None
            
            # Try to extract error details
            if hasattr(e, 'response') and e.response:
                try:
                    error_body = e.response.json() if hasattr(e.response, 'json') else {}
                    if isinstance(error_body, dict) and 'error' in error_body:
                        error_obj = error_body['error']
                        if isinstance(error_obj, dict):
                            error_code = error_obj.get('code')
                            error_msg = error_obj.get('message', error_msg)
                except:
                    pass
            
            _logger.error(f"OpenAI API error: {error_msg}", exc_info=True)
            
            # Provide helpful error messages based on error type
            if error_code == 'context_length_exceeded':
                model_name = config.get('model', 'the selected model')
                raise UserError(
                    f'Input exceeds the context window of {model_name}.\n\n'
                    'The model information (fields, relationships) is too large for this model.\n\n'
                    'Suggestions:\n'
                    '- Use a model with a larger context window (e.g., gpt-4.1, gpt-5, o1, o3, o4)\n'
                    '- Try switching to "Chat Completions API" in Settings\n'
                    '- Select a simpler model with fewer fields\n'
                    '- Reduce the depth of field discovery in your report request'
                )
            elif hasattr(e, 'response') and e.response:
                if hasattr(e.response, 'status_code'):
                    if e.response.status_code == 401:
                        raise UserError('OpenAI API authentication failed. Please check your API key in Settings.')
                    elif e.response.status_code == 402:
                        raise UserError('OpenAI API payment required. Please check your OpenAI account billing.')
                    elif e.response.status_code == 500:
                        raise UserError('OpenAI API server error. Please try again later.')
            
            raise UserError(f'OpenAI API error: {error_msg}')
            
        except Exception as e:
            _logger.error(f"Unexpected error calling OpenAI API: {e}", exc_info=True)
            raise UserError(f'Unexpected error: {str(e)}')
    
    @api.model
    def call_responses_api(self, input_data, instructions=None, model=None, 
                          max_output_tokens=None, tools=None, tool_choice=None, 
                          text=None, stream=False, **kwargs):
        """
        Call OpenAI Responses API with advanced features using the official OpenAI Python package
        
        Args:
            input_data: Text, image, or file inputs (string or array)
            instructions: System/developer message (string)
            model: Model ID (defaults to configured model)
            max_output_tokens: Max tokens for output (defaults to configured max_tokens)
            tools: Array of tools the model can call
            tool_choice: How model should select tools
            text: Text configuration object (for structured outputs)
            stream: Whether to stream the response
            **kwargs: Additional parameters (conversation, previous_response_id, etc.)
        
        Returns:
            Response object from Responses API (or stream object if streaming)
        """
        config = self.get_openai_config()
        if not config['enabled']:
            raise UserError('OpenAI is not enabled. Please configure OpenAI API key in Settings.')
        
        if not config['api_key']:
            raise UserError('OpenAI API key is not configured. Please set it in Settings.')
        
        # Normalize and construct URL properly
        base_url = config['base_url'].strip()
        if not base_url:
            raise UserError('OpenAI Base URL is not configured. Please set it in Settings.')
        
        base_url = base_url.rstrip('/')
        
        # Validate URL format
        try:
            parsed = urlparse(base_url)
            if not parsed.scheme or not parsed.netloc:
                raise UserError(f'Invalid Base URL format: {base_url}. Must be a valid URL (e.g., https://api.openai.com/v1)')
        except Exception as e:
            raise UserError(f'Invalid Base URL: {base_url}. Error: {str(e)}')
        
        if not OPENAI_AVAILABLE:
            raise UserError(
                'OpenAI Python package is not installed. '
                'Please install it with: pip install openai'
            )
        
        try:
            client = self._get_openai_client(config)
            
            # Build parameters for Responses API
            params = {
                'model': model or config['model'],
                'input': input_data,
                'max_output_tokens': max_output_tokens or config['max_tokens'],
                'stream': stream,
            }
            
            if instructions:
                params['instructions'] = instructions
            
            if tools:
                params['tools'] = tools
            
            if tool_choice:
                params['tool_choice'] = tool_choice
            
            if text:
                params['text'] = text
            
            # Add any additional parameters
            params.update(kwargs)
            
            # Call Responses API using OpenAI package
            response = client.responses.create(**params)
            
            if stream:
                # Return stream object
                return response
            else:
                # Return response object (can be converted to dict if needed)
                return response
                
        except RateLimitError as e:
            error_msg = str(e)
            raise UserError(
                f'OpenAI API rate limit exceeded: {error_msg}\n\n'
                'Please wait a few minutes before trying again, or consider:\n'
                '- Upgrading your OpenAI plan for higher limits\n'
                '- Reducing the frequency of requests'
            )
        except APITimeoutError:
            raise UserError('OpenAI API request timed out. Please try again or increase the timeout in Settings.')
        except APIConnectionError:
            raise UserError('Failed to connect to OpenAI API. Please check your internet connection.')
        except APIError as e:
            error_msg = str(e)
            _logger.error(f"OpenAI Responses API error: {error_msg}", exc_info=True)
            raise UserError(f'OpenAI Responses API error: {error_msg}')
        except Exception as e:
            _logger.error(f"Unexpected error calling OpenAI Responses API: {e}", exc_info=True)
            raise UserError(f'Unexpected error: {str(e)}')
    
    def _parse_error_response(self, response):
        """
        Parse error response from OpenAI API
        
        Args:
            response: requests.Response object
            
        Returns:
            str: Error message
        """
        if not response:
            return "Unknown error - no response received"
        
        # Try to parse JSON error response
        try:
            error_data = response.json()
            if isinstance(error_data, dict):
                error_obj = error_data.get('error', {})
                if isinstance(error_obj, dict):
                    # Get the main error message
                    message = error_obj.get('message', '')
                    error_type = error_obj.get('type', '')
                    code = error_obj.get('code', '')
                    
                    error_parts = []
                    if error_type:
                        error_parts.append(f"Type: {error_type}")
                    if code:
                        error_parts.append(f"Code: {code}")
                    if message:
                        error_parts.append(f"Message: {message}")
                    
                    if error_parts:
                        return " | ".join(error_parts)
                    else:
                        return str(error_obj)
                elif isinstance(error_obj, str):
                    return error_obj
                else:
                    return str(error_data)
            else:
                return str(error_data)
        except json.JSONDecodeError:
            # Not JSON, try to get text
            try:
                if hasattr(response, 'text') and response.text:
                    # Try to extract meaningful error from text
                    text = response.text.strip()
                    if text:
                        # Limit length to avoid huge error messages
                        return text[:500] if len(text) > 500 else text
            except:
                pass
            
            # Fallback to status code
            return f"HTTP {response.status_code} - Unable to parse error response"
        except Exception as e:
            # Last resort
            try:
                return response.text[:500] if hasattr(response, 'text') and response.text else f"HTTP {response.status_code} - Error parsing response: {str(e)}"
            except:
                return f"HTTP {response.status_code} - Unknown error"
    
    def _extract_rate_limit_info(self, headers):
        """
        Extract rate limit information from response headers
        
        Args:
            headers: Response headers dict
            
        Returns:
            dict: Rate limit information
        """
        info = {}
        rate_limit_fields = [
            'x-ratelimit-limit-requests',
            'x-ratelimit-limit-tokens',
            'x-ratelimit-remaining-requests',
            'x-ratelimit-remaining-tokens',
            'x-ratelimit-reset-requests',
            'x-ratelimit-reset-tokens',
        ]
        
        for field in rate_limit_fields:
            value = headers.get(field)
            if value:
                info[field] = value
        
        return info if info else None
    
    def _format_rate_limit_message(self, rate_limit_info):
        """
        Format rate limit information into a user-friendly message
        
        Args:
            rate_limit_info: dict with rate limit headers
            
        Returns:
            str: Formatted rate limit message
        """
        if not rate_limit_info:
            return ""
        
        lines = []
        
        # Format TPM (Tokens Per Minute) information
        limit_tokens = rate_limit_info.get('x-ratelimit-limit-tokens')
        remaining_tokens = rate_limit_info.get('x-ratelimit-remaining-tokens')
        reset_tokens = rate_limit_info.get('x-ratelimit-reset-tokens')
        
        if limit_tokens or remaining_tokens:
            token_line = "  TPM (Tokens Per Minute): "
            if limit_tokens:
                token_line += f"Limit: {self._format_number(limit_tokens)}"
            if remaining_tokens:
                if limit_tokens:
                    token_line += ", "
                token_line += f"Remaining: {self._format_number(remaining_tokens)}"
                if limit_tokens:
                    used = int(limit_tokens) - int(remaining_tokens)
                    percentage = (used / int(limit_tokens)) * 100
                    token_line += f" ({percentage:.1f}% used)"
            if reset_tokens:
                try:
                    reset_time = datetime.datetime.fromtimestamp(int(reset_tokens))
                    now = datetime.datetime.now()
                    seconds_until_reset = max(0, int((reset_time - now).total_seconds()))
                    if seconds_until_reset > 0:
                        minutes = seconds_until_reset // 60
                        seconds = seconds_until_reset % 60
                        if minutes > 0:
                            token_line += f", Resets in: {minutes}m {seconds}s"
                        else:
                            token_line += f", Resets in: {seconds_until_reset}s"
                except:
                    pass
            lines.append(token_line)
        
        # Format RPM (Requests Per Minute) information
        limit_requests = rate_limit_info.get('x-ratelimit-limit-requests')
        remaining_requests = rate_limit_info.get('x-ratelimit-remaining-requests')
        reset_requests = rate_limit_info.get('x-ratelimit-reset-requests')
        
        if limit_requests or remaining_requests:
            request_line = "  RPM (Requests Per Minute): "
            if limit_requests:
                request_line += f"Limit: {self._format_number(limit_requests)}"
            if remaining_requests:
                if limit_requests:
                    request_line += ", "
                request_line += f"Remaining: {self._format_number(remaining_requests)}"
                if limit_requests:
                    used = int(limit_requests) - int(remaining_requests)
                    percentage = (used / int(limit_requests)) * 100
                    request_line += f" ({percentage:.1f}% used)"
            if reset_requests:
                try:
                    reset_time = datetime.datetime.fromtimestamp(int(reset_requests))
                    now = datetime.datetime.now()
                    seconds_until_reset = max(0, int((reset_time - now).total_seconds()))
                    if seconds_until_reset > 0:
                        minutes = seconds_until_reset // 60
                        seconds = seconds_until_reset % 60
                        if minutes > 0:
                            request_line += f", Resets in: {minutes}m {seconds}s"
                        else:
                            request_line += f", Resets in: {seconds_until_reset}s"
                except:
                    pass
            lines.append(request_line)
        
        return "\n".join(lines) if lines else ""
    
    def _format_number(self, value):
        """
        Format number with thousand separators for readability
        
        Args:
            value: Number as string or int
            
        Returns:
            str: Formatted number
        """
        try:
            num = int(value)
            return f"{num:,}"
        except:
            return str(value)

    @api.model
    def parse_json_response(self, response_text):
        """
        Parse JSON from OpenAI response (handles markdown code blocks)
        
        Args:
            response_text: Raw response from OpenAI
        
        Returns:
            dict: Parsed JSON object
        """
        try:
            # Try to extract JSON from response
            # OpenAI might wrap JSON in markdown code blocks
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                json_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                # Try to find JSON object
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                else:
                    json_text = response_text
            
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            _logger.error(f"Failed to parse OpenAI response as JSON: {e}", exc_info=True)
            raise UserError("OpenAI returned invalid JSON. Please try rephrasing your request.")

