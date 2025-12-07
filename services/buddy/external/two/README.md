# buddy Service - external - two Card(s)

## Purpose
This service provides buddy functionality for external users with two card configuration.

## Card Configuration
- **Number of cards**: two
- **Target audience**: external
- **Service type**: buddy

## API Endpoint
`POST /buddy/external/two`

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
  "service": "buddy",
  "audience": "external", 
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
