#!/usr/bin/env python3
"""
Example helper script for openai-agents-sdk

This script demonstrates how to use the OpenAI Agents SDK with Google's Gemini API
through the OpenAI-compatible endpoint.

Example usage:
- Demonstrates configuring OpenAI client for Gemini API
- Shows how to create agents using different providers
"""

from openai import OpenAI, AsyncOpenAI
import os
import asyncio

def configure_gemini_client():
    """
    Configure OpenAI client to work with Google Gemini API
    """
    gemini_client = OpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    return gemini_client

def configure_openai_client():
    """
    Configure OpenAI client for native OpenAI models
    """
    openai_client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    return openai_client

def create_agent(provider="gemini"):
    """
    Create an agent using either Gemini or OpenAI provider
    """
    if provider == "gemini":
        client = configure_gemini_client()
        model = "gemini-2.5-flash"
    elif provider == "openai":
        client = configure_openai_client()
        model = "gpt-4-turbo"
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    return client, model

def run_simple_query(provider="gemini", message="Hello, how can you help me?"):
    """
    Run a simple query with the specified provider
    """
    client, model = create_agent(provider)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": message}
            ]
        )

        return {
            "provider": provider,
            "model": model,
            "response": response.choices[0].message.content
        }
    except Exception as e:
        return {
            "provider": provider,
            "error": str(e)
        }

async def run_async_query(provider="gemini", message="Hello, how can you help me?"):
    """
    Run an async query with the specified provider
    """
    if provider == "gemini":
        client = AsyncOpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        model = "gemini-2.5-flash"
    elif provider == "openai":
        client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        model = "gpt-4-turbo"
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": message}
            ]
        )

        return {
            "provider": provider,
            "model": model,
            "response": response.choices[0].message.content
        }
    except Exception as e:
        return {
            "provider": provider,
            "error": str(e)
        }

def main():
    print("OpenAI Agents SDK with Multiple Providers Example")
    print("="*50)

    # Check for required environment variables
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("Warning: Neither GEMINI_API_KEY nor OPENAI_API_KEY environment variables are set.")
        print("Please set at least one of these to run the examples.")
        return

    # Test with Gemini if API key is available
    if os.getenv("GEMINI_API_KEY"):
        print("\nTesting with Gemini:")
        result = run_simple_query("gemini", "Say hello and explain what you can do.")
        print(f"Provider: {result['provider']}")
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Response: {result['response'][:100]}...")

    # Test with OpenAI if API key is available
    if os.getenv("OPENAI_API_KEY"):
        print("\nTesting with OpenAI:")
        result = run_simple_query("openai", "Say hello and explain what you can do.")
        print(f"Provider: {result['provider']}")
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Response: {result['response'][:100]}...")

    print("\nExample completed!")

if __name__ == "__main__":
    main()
