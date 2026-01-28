---
name: openai-agents-sdk
description: Enables the use of OpenAI Agents SDK with various LLM providers including OpenAI, Google Gemini, and other OpenAI-compatible APIs. Provides guidance on configuring clients for different providers and implementing agent workflows.
---

# Openai AgentsSdk

## Overview

The OpenAI Agents SDK provides a framework for creating intelligent agents that can interact with various language models. This skill covers how to use the OpenAI Agents SDK with different LLM providers, including OpenAI's native models and alternative providers like Google Gemini that offer OpenAI-compatible APIs.

## Using OpenAI Agents SDK with Different Providers

### Standard OpenAI Configuration

For using the OpenAI Agents SDK with native OpenAI models:

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

### Google Gemini Integration

Google's Gemini API provides an OpenAI-compatible endpoint that allows using the OpenAI Agents SDK with Gemini models:

```python
from openai import OpenAI
import os

# Configure OpenAI client to point to Gemini API
external_client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Use with Gemini models
response = external_client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "user", "content": "Hello, how can you help me?"}
    ]
)
```

### Async Client for Gemini

For asynchronous operations with Gemini:

```python
from openai import AsyncOpenAI
import os

async_external_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Use with Gemini models asynchronously
response = await async_external_client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "user", "content": "Hello, how can you help me?"}
    ]
)
```

## Agent Creation Patterns

### Basic Agent with Custom Provider

```python
from openai import OpenAI
import os

def create_agent_with_provider(provider="openai"):
    if provider == "gemini":
        client = OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        model = "gemini-2.5-flash"
    elif provider == "openai":
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = "gpt-4-turbo"
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    return client, model

# Example usage
client, model = create_agent_with_provider("gemini")
response = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Create a helpful agent response."}]
)
```

## Configuration Best Practices

### Environment Variables

Store API keys securely using environment variables:

```
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### Error Handling

When working with multiple providers, implement proper error handling:

```python
from openai import OpenAI, APIError
import os

def safe_call_with_fallback(messages, primary_provider="gemini", fallback_provider="openai"):
    providers = [primary_provider, fallback_provider]

    for provider in providers:
        try:
            if provider == "gemini":
                client = OpenAI(
                    api_key=os.getenv("GEMINI_API_KEY"),
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                )
                model = "gemini-2.5-flash"
            elif provider == "openai":
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                model = "gpt-4-turbo"

            response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response
        except APIError as e:
            print(f"Error with {provider}: {str(e)}")
            if provider == providers[-1]:  # Last provider in the list
                raise e  # Re-raise the error if all providers failed
            continue  # Try the next provider

    return None
```

## Resources

This skill includes example resource directories that demonstrate how to organize different types of bundled resources:

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Claude for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Claude's process and thinking.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Claude should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output Claude produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Any unneeded directories can be deleted.** Not every skill requires all three types of resources.
