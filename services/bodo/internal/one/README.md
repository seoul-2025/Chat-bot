# bodo Service - internal - one Card(s)

## Purpose
This service provides bodo functionality for internal users with one card configuration.

## Card Configuration
- **Number of cards**: one
- **Target audience**: internal
- **Service type**: bodo

## API Endpoint
`POST /bodo/internal/one`

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
  "service": "bodo",
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
