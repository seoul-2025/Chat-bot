# proofreading Service - internal - one Card(s)

## Purpose
This service provides proofreading functionality for internal users with one card configuration.

## Card Configuration
- **Number of cards**: one
- **Target audience**: internal
- **Service type**: proofreading

## API Endpoint
`POST /proofreading/internal/one`

## Request Format
```json
{
  "text": "Input text for processing",
  "options": {}
}
```

## Response Format
```json
{
  "service": "proofreading",
  "audience": "internal", 
  "cards": "one",
  "result": "Processed result"
}
```

## Development
```bash
# Install dependencies
npm install

# Deploy to dev
serverless deploy --stage dev

# Deploy to production
serverless deploy --stage prod
```

## Prompts
- `prompts/system.txt`: System prompt for AI model
- `prompts/user.txt`: User prompt template
