# Bedrock Client

## Purpose
AWS Bedrock client wrapper for interacting with Claude and other foundation models.

## Features
- Unified interface for multiple models
- Automatic retry with exponential backoff
- Request/response logging
- Error handling and recovery
- Streaming support
- Token counting and cost tracking

## Usage
```javascript
const { BedrockClient } = require('@nexus/bedrock-client');

const client = new BedrockClient({
  region: 'ap-northeast-2',
  model: 'anthropic.claude-3-sonnet'
});

const response = await client.invoke({
  system: 'You are a helpful assistant',
  messages: [{ role: 'user', content: 'Hello' }]
});
```

## API
- `invoke(params)`: Invoke model with messages
- `stream(params)`: Stream model responses
- `countTokens(text)`: Count tokens in text
- `estimateCost(tokens)`: Estimate API cost
- `listModels()`: List available models