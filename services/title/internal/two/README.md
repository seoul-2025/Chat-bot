# title Service - internal - two Card(s)

## Purpose
This service provides title functionality for internal users with two card configuration.

## Card Configuration
- **Number of cards**: two
- **Target audience**: internal
- **Service type**: title

## API Endpoint
`POST /title/internal/two`

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
  "service": "title",
  "audience": "internal", 
  "cards": "two",
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
