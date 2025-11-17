#!/usr/bin/env python3
"""
Fake OpenAI Responses Server

A development server that mimics OpenAI's API but returns predefined tokens
with configurable streaming rates and token types.
"""

import argparse
import asyncio
import json
import time
import uuid
from typing import Optional, AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import uvicorn


app = FastAPI(title="Fake OpenAI Responses Server")

# Global configuration
config = {
    "tokens": "Hello, this is a fake OpenAI response!",
    "rate": None,  # tokens per second, None = no delay
    "type": "output",  # "thinking" or "output"
}


async def generate_tokens(tokens: str, rate: Optional[float], token_type: str) -> AsyncGenerator[str, None]:
    """
    Generate tokens with optional rate limiting.

    Args:
        tokens: The text to stream
        rate: Tokens per second (None for no delay)
        token_type: "thinking" or "output"
    """
    # Split into individual tokens (simple word-based splitting)
    words = tokens.split()

    for i, word in enumerate(words):
        # Add space before word except for first token
        token_text = word if i == 0 else f" {word}"

        # Create the appropriate response chunk based on token type
        if token_type == "thinking":
            chunk = {
                "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "gpt-4",
                "choices": [{
                    "index": 0,
                    "delta": {
                        "reasoning_content": token_text
                    },
                    "finish_reason": None
                }]
            }
        else:  # output
            chunk = {
                "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "gpt-4",
                "choices": [{
                    "index": 0,
                    "delta": {
                        "content": token_text
                    },
                    "finish_reason": None
                }]
            }

        # Yield the chunk in SSE format
        yield f"data: {json.dumps(chunk)}\n\n"

        # Apply rate limiting if specified
        if rate is not None and rate > 0:
            await asyncio.sleep(1.0 / rate)

    # Send final chunk
    final_chunk = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": "gpt-4",
        "choices": [{
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }]
    }
    yield f"data: {json.dumps(final_chunk)}\n\n"
    yield "data: [DONE]\n\n"


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """
    OpenAI-compatible chat completions endpoint.
    """
    body = await request.json()
    stream = body.get("stream", False)

    if stream:
        # Return streaming response
        return StreamingResponse(
            generate_tokens(config["tokens"], config["rate"], config["type"]),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    else:
        # Return non-streaming response
        response = {
            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-4",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": config["tokens"] if config["type"] == "output" else None,
                    "reasoning_content": config["tokens"] if config["type"] == "thinking" else None,
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": len(config["tokens"].split()),
                "total_tokens": 10 + len(config["tokens"].split())
            }
        }
        return response


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "config": {
            "tokens_length": len(config["tokens"]),
            "rate": config["rate"],
            "type": config["type"]
        }
    }


@app.get("/")
async def root():
    """Root endpoint with server info."""
    return {
        "name": "Fake OpenAI Responses Server",
        "version": "1.0.0",
        "endpoints": [
            "/v1/chat/completions",
            "/health"
        ],
        "config": {
            "tokens_preview": config["tokens"][:100] + "..." if len(config["tokens"]) > 100 else config["tokens"],
            "rate": config["rate"],
            "type": config["type"]
        }
    }


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Fake OpenAI Responses Server - Serve predefined tokens with configurable streaming"
    )
    parser.add_argument(
        "tokens",
        type=str,
        help="The tokens/text to serve in responses"
    )
    parser.add_argument(
        "--rate",
        type=float,
        default=None,
        help="Token delivery rate in tokens per second (default: no delay)"
    )
    parser.add_argument(
        "--type",
        choices=["thinking", "output"],
        default="output",
        help="Type of tokens to serve: 'thinking' or 'output' (default: output)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )

    args = parser.parse_args()

    # Update global config
    config["tokens"] = args.tokens
    config["rate"] = args.rate
    config["type"] = args.type

    print(f"🚀 Starting Fake OpenAI Responses Server")
    print(f"   Tokens: {args.tokens[:100]}{'...' if len(args.tokens) > 100 else ''}")
    print(f"   Rate: {args.rate if args.rate else 'unlimited'} tokens/sec")
    print(f"   Type: {args.type}")
    print(f"   Listening on http://{args.host}:{args.port}")
    print(f"\n   OpenAI-compatible endpoint: http://{args.host}:{args.port}/v1/chat/completions")
    print(f"   Health check: http://{args.host}:{args.port}/health\n")

    # Run the server
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
