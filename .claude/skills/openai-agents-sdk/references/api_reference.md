# OpenAI Agents SDK with Multiple LLM Providers

## Overview

The OpenAI Agents SDK provides a flexible framework for creating intelligent agents that can work with various Large Language Model (LLM) providers. While originally designed for OpenAI models, the SDK's OpenAI-compatible API design allows integration with other providers such as Google Gemini, Anthropic Claude (via third-party implementations), and other services that provide OpenAI-compatible endpoints.

## Supported Providers

### Native OpenAI Models
- GPT-4 series (gpt-4, gpt-4-turbo, gpt-4-vision-preview)
- GPT-3.5 Turbo (gpt-3.5-turbo)
- Specialized models (davinci, curie, babbage, ada)

### Google Gemini
- Gemini Pro (gemini-pro)
- Gemini Flash (gemini-2.5-flash, gemini-1.5-flash)
- Gemini Vision (gemini-1.5-pro)

## Configuration Patterns

### Basic Client Configuration

```python
from openai import OpenAI

# Standard OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"),)

# Google Gemini client (using OpenAI-compatible endpoint)
gemini_client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
```

### Provider-Agnostic Client Factory

```python
from openai import OpenAI
import os

def get_client(provider_name: str):
    """
    Factory function to return the appropriate client based on provider
    """
    if provider_name == "openai":
        return OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        ), "gpt-4-turbo"

    elif provider_name == "gemini":
        return OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        ), "gemini-2.5-flash"

    else:
        raise ValueError(f"Unsupported provider: {provider_name}")
```

## Advanced Configuration

### Async Support

```python
from openai import AsyncOpenAI

async def async_completion(provider_name: str, messages: list):
    """
    Perform async completion with specified provider
    """
    client, model = get_client(provider_name)

    if isinstance(client, AsyncOpenAI):
        response = await client.chat.completions.create(
            model=model,
            messages=messages
        )
    else:
        # Convert sync client to async client if needed
        async_client = AsyncOpenAI(
            api_key=client.api_key,
            base_url=getattr(client, 'base_url', None)
        )
        response = await async_client.chat.completions.create(
            model=model,
            messages=messages
        )

    return response
```

### Fallback Mechanisms

```python
from openai import OpenAI, APIError
import logging

def call_with_fallback(messages: list, primary_provider: str = "gemini",
                      secondary_provider: str = "openai", max_retries: int = 1):
    """
    Call LLM with fallback mechanism
    """
    providers = [primary_provider, secondary_provider]

    for i, provider in enumerate(providers):
        try:
            client, model = get_client(provider)

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_retries=max_retries
            )

            logging.info(f"Successfully used {provider} provider")
            return response

        except APIError as e:
            logging.warning(f"Failed to use {provider} provider: {str(e)}")

            # If this is the last provider, re-raise the exception
            if i == len(providers) - 1:
                raise e

    return None
```

## Practical Examples

### Example 1: Simple Agent with Provider Switching

```python
class MultiProviderAgent:
    def __init__(self, primary_provider="gemini", fallback_provider="openai"):
        self.primary_provider = primary_provider
        self.fallback_provider = fallback_provider

    def chat(self, messages):
        try:
            # Try primary provider first
            client, model = get_client(self.primary_provider)

            response = client.chat.completions.create(
                model=model,
                messages=messages
            )

            return {
                "provider_used": self.primary_provider,
                "model": model,
                "response": response.choices[0].message.content
            }

        except Exception as e:
            print(f"Primary provider failed: {e}")
            print("Switching to fallback provider...")

            # Fallback to secondary provider
            client, model = get_client(self.fallback_provider)

            response = client.chat.completions.create(
                model=model,
                messages=messages
            )

            return {
                "provider_used": self.fallback_provider,
                "model": model,
                "response": response.choices[0].message.content
            }

# Usage
agent = MultiProviderAgent(primary_provider="gemini", fallback_provider="openai")
messages = [{"role": "user", "content": "Explain quantum computing in simple terms"}]
result = agent.chat(messages)
print(f"Used {result['provider_used']}: {result['response']}")
```

### Example 2: Cost-Effective Provider Selection

```python
def select_cost_effective_provider(task_complexity: str = "standard"):
    """
    Select the most cost-effective provider based on task requirements
    """
    if task_complexity == "simple":
        # Use cheaper model like gemini-1.5-flash
        return get_client("gemini")
    elif task_complexity == "complex":
        # Use more capable model like gpt-4-turbo or gemini-pro
        return get_client("openai")  # or return get_client("gemini") depending on preference
    else:
        # Default to primary choice
        return get_client("gemini")
```

## Error Handling and Monitoring

### Comprehensive Error Handling

```python
from openai import OpenAI, APIError, RateLimitError
import time

def robust_llm_call(messages, provider="gemini", max_retries=3):
    """
    Robust LLM call with comprehensive error handling
    """
    for attempt in range(max_retries):
        try:
            client, model = get_client(provider)

            response = client.chat.completions.create(
                model=model,
                messages=messages
            )

            return response

        except RateLimitError as e:
            wait_time = min(2 ** attempt, 60)  # Exponential backoff
            print(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
            time.sleep(wait_time)

        except APIError as e:
            print(f"API Error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise e  # Re-raise on final attempt

        except Exception as e:
            print(f"Unexpected error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise e

    return None
```

## Performance Considerations

### Response Time Optimization

Different providers have different response characteristics:

- **Gemini Flash**: Optimized for speed, good for quick responses
- **Gemini Pro**: Better for complex reasoning tasks
- **GPT-4 Turbo**: Strong reasoning and instruction-following
- **GPT-3.5 Turbo**: Fast and cost-effective for simpler tasks

### Caching Strategies

For repeated queries, implement caching:

```python
import hashlib
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_completion(messages_tuple, model):
    """
    Cached completion to avoid repeated calls for identical requests
    """
    # Convert tuple back to list for API call
    messages = list(messages_tuple)

    client, _ = get_client("gemini")  # or appropriate provider

    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    return response.choices[0].message.content

def cache_friendly_call(messages, model):
    """
    Wrapper to convert messages to tuple for caching
    """
    messages_tuple = tuple(
        tuple(item.items()) for item in messages
    )

    return cached_completion(messages_tuple, model)
```

## Security Considerations

### API Key Management

Always store API keys securely:

```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access keys through environment variables only
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

### Input Sanitization

Validate and sanitize inputs before sending to LLMs:

```python
import re

def sanitize_input(user_input):
    """
    Basic sanitization of user input
    """
    # Remove potential harmful patterns
    sanitized = re.sub(r'[<>\{\}\\]', '', user_input)

    # Limit length
    if len(sanitized) > 10000:
        sanitized = sanitized[:10000]

    return sanitized.strip()
```

This reference provides comprehensive information about using the OpenAI Agents SDK with multiple providers, focusing on practical implementation patterns and best practices.
