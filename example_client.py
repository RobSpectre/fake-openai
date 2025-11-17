#!/usr/bin/env python3
"""
Example client for testing the Fake OpenAI Responses Server.

This script demonstrates how to interact with the server using both
raw HTTP requests and the OpenAI Python SDK.
"""

import argparse
import json
import requests


def test_with_requests(base_url: str, stream: bool = True):
    """Test the server using raw HTTP requests."""
    print(f"\n{'='*60}")
    print(f"Testing with requests library (stream={stream})")
    print(f"{'='*60}\n")

    url = f"{base_url}/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": stream
    }

    response = requests.post(url, headers=headers, json=data, stream=stream)

    if stream:
        print("Streaming response:")
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # Remove 'data: ' prefix
                    if data_str == '[DONE]':
                        print("\n[Stream completed]")
                        break
                    try:
                        chunk = json.loads(data_str)
                        # Extract content from delta
                        delta = chunk['choices'][0]['delta']
                        if 'content' in delta:
                            print(delta['content'], end='', flush=True)
                        elif 'reasoning_content' in delta:
                            print(f"[THINKING: {delta['reasoning_content']}]", end='', flush=True)
                    except json.JSONDecodeError:
                        pass
        print()
    else:
        print("Non-streaming response:")
        result = response.json()
        message = result['choices'][0]['message']
        if 'content' in message and message['content']:
            print(f"Content: {message['content']}")
        elif 'reasoning_content' in message and message['reasoning_content']:
            print(f"Reasoning: {message['reasoning_content']}")
        print(f"\nUsage: {result['usage']}")


def test_with_openai_sdk(base_url: str):
    """Test the server using the OpenAI Python SDK."""
    try:
        from openai import OpenAI
    except ImportError:
        print("\n⚠️  OpenAI SDK not installed. Install with: pip install openai")
        return

    print(f"\n{'='*60}")
    print("Testing with OpenAI SDK (streaming)")
    print(f"{'='*60}\n")

    client = OpenAI(
        base_url=f"{base_url}/v1",
        api_key="fake-key"  # Any string works
    )

    print("Streaming response:")
    stream = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end='', flush=True)

    print("\n")


def check_health(base_url: str):
    """Check the server health."""
    print(f"\n{'='*60}")
    print("Server Health Check")
    print(f"{'='*60}\n")

    response = requests.get(f"{base_url}/health")
    health = response.json()

    print(f"Status: {health['status']}")
    print(f"Configuration:")
    for key, value in health['config'].items():
        print(f"  {key}: {value}")


def main():
    parser = argparse.ArgumentParser(
        description="Example client for Fake OpenAI Responses Server"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:8000",
        help="Base URL of the server (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--test",
        choices=["all", "requests", "openai", "health"],
        default="all",
        help="Which test to run (default: all)"
    )

    args = parser.parse_args()

    print(f"Testing server at: {args.base_url}")

    try:
        if args.test in ["all", "health"]:
            check_health(args.base_url)

        if args.test in ["all", "requests"]:
            test_with_requests(args.base_url, stream=True)
            test_with_requests(args.base_url, stream=False)

        if args.test in ["all", "openai"]:
            test_with_openai_sdk(args.base_url)

    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Could not connect to server at {args.base_url}")
        print("Make sure the server is running with: python server.py 'Your text here'")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
