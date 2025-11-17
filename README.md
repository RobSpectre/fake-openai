# Fake OpenAI Responses Server

A development and testing server that mimics OpenAI's API but returns predefined tokens with configurable streaming rates and token types.

## Features

- **OpenAI-compatible API**: Implements the `/v1/chat/completions` endpoint
- **Configurable token streaming**: Control the rate of token delivery
- **Random pauses**: Add realistic variable delays between tokens
- **Token type support**: Simulate both "thinking" and "output" tokens
- **Streaming and non-streaming**: Supports both streaming and non-streaming responses
- **No actual inference**: Returns predefined text instead of doing AI inference

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python server.py "Hello, this is a test response!"
```

### With Rate Limiting

Stream tokens at 5 tokens per second:

```bash
python server.py "Hello, this is a test response!" --rate 5
```

### Thinking Tokens

Serve thinking tokens instead of output tokens:

```bash
python server.py "Let me think about this..." --type thinking
```

### With Random Pauses

Add random pauses between 0 and 0.5 seconds for more realistic streaming:

```bash
python server.py "Hello, this is a test response!" --random-pause 0.5
```

### Combining Rate and Random Pauses

Use both constant rate and random pauses for variable-rate streaming:

```bash
python server.py "This simulates realistic AI response timing" \
  --rate 10 \
  --random-pause 0.3
```

This will deliver tokens at approximately 10 tokens/sec with an additional random delay of 0-0.3s per token.

### Custom Host and Port

```bash
python server.py "Response text" --host localhost --port 8080
```

### All Options

```bash
python server.py "Your response text here" \
  --rate 10 \
  --type output \
  --random-pause 0.2 \
  --host 0.0.0.0 \
  --port 8000
```

## Command Line Arguments

- `tokens` (required): The text/tokens to serve in responses
- `--rate` (optional): Token delivery rate in tokens per second (default: no delay)
- `--type` (optional): Type of tokens - "thinking" or "output" (default: "output")
- `--random-pause` (optional): Maximum random pause between tokens in seconds (default: no random pause)
- `--host` (optional): Host to bind to (default: "0.0.0.0")
- `--port` (optional): Port to bind to (default: 8000)

## API Endpoints

### POST /v1/chat/completions

OpenAI-compatible chat completions endpoint.

**Streaming Example:**

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": true
  }'
```

**Non-streaming Example:**

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": false
  }'
```

### GET /health

Health check endpoint that returns server status and configuration.

```bash
curl http://localhost:8000/health
```

### GET /

Root endpoint with server information.

```bash
curl http://localhost:8000/
```

## Using with OpenAI SDK

You can use this server as a drop-in replacement for OpenAI's API:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="fake-key"  # Any string works
)

# Streaming
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Use Cases

- **Testing**: Test OpenAI API integrations without making real API calls
- **Development**: Develop applications with predictable responses
- **Rate limiting simulation**: Test how your application handles different token delivery rates
- **Variable timing simulation**: Simulate realistic AI response patterns with random pauses
- **Token type testing**: Test handling of thinking vs output tokens
- **Cost-free development**: Develop without incurring OpenAI API costs

## Example Sessions

### Slow streaming (simulating thinking)

```bash
python server.py "First, I need to analyze the problem. Then, I'll formulate a solution." \
  --rate 2 \
  --type thinking
```

### Fast output

```bash
python server.py "Here is the quick answer to your question." \
  --rate 50 \
  --type output
```

### Realistic variable-rate streaming

```bash
python server.py "This simulates natural AI response patterns with variable timing." \
  --rate 8 \
  --random-pause 0.4 \
  --type output
```

This creates a more realistic streaming experience where tokens arrive at roughly 8 tokens/sec with random variations.

## License

MIT
