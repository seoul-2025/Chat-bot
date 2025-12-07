# Nexus Development Conventions

## Code Style

### JavaScript/Node.js
- **Style Guide**: Airbnb JavaScript Style Guide
- **Linting**: ESLint with Airbnb config
- **Formatting**: Prettier with 2-space indentation
- **Naming**: camelCase for variables, PascalCase for classes

```javascript
// Good
const processArticle = async (text) => {
  const result = await analyzeContent(text);
  return formatResponse(result);
};

// Bad
const process_article = async (text) => {
  var result = await analyze_content(text)
  return format_response(result)
}
```

### File Naming
- **Services**: `kebab-case` (e.g., `title-service.js`)
- **Utilities**: `camelCase` (e.g., `promptEngine.js`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_TOKENS.js`)
- **Tests**: `*.test.js` or `*.spec.js`

## Project Structure

### Service Structure
```
/services/{service-name}/{audience}/{card-count}/
├── serverless.yml       # Serverless configuration
├── handler.js          # Lambda handler
├── index.js           # Main logic
├── prompts/           # Prompt templates
│   ├── system.txt
│   └── user.txt
├── tests/             # Unit tests
│   └── index.test.js
├── package.json       # Dependencies
└── README.md          # Documentation
```

### Shared Libraries
```
/libs/{library-name}/
├── index.js          # Main export
├── src/              # Source files
│   └── *.js
├── tests/            # Unit tests
│   └── *.test.js
├── package.json      # Dependencies
└── README.md         # Documentation
```

## Git Conventions

### Branch Naming
- `feature/service-name-description`
- `fix/issue-number-description`
- `chore/task-description`
- `docs/section-update`

### Commit Messages
Follow Conventional Commits specification:
```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Build/tooling changes

Examples:
```bash
feat(title): add three-card layout support
fix(proofreading): resolve timeout issue with long texts
docs(api): update endpoint documentation
```

## API Conventions

### Endpoint Naming
- Pattern: `/{service}/{audience}/{cards}`
- Method: POST for all AI operations
- Version: `/api/v1/` prefix

### Request Format
```json
{
  "text": "Required input text",
  "options": {
    "temperature": 0.7,
    "maxTokens": 4096,
    "language": "ko"
  },
  "metadata": {
    "userId": "user123",
    "sessionId": "session456"
  }
}
```

### Response Format
```json
{
  "success": true,
  "data": {
    "result": "Processed content",
    "cards": [
      { "id": 1, "content": "..." }
    ]
  },
  "metadata": {
    "service": "title",
    "audience": "internal",
    "cards": "two",
    "processTime": 1234,
    "tokens": 500
  },
  "error": null
}
```

### Error Response
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Input text is required",
    "details": {}
  }
}
```

## Testing Conventions

### Test Structure
```javascript
describe('ServiceName', () => {
  describe('functionName', () => {
    it('should handle valid input', async () => {
      // Arrange
      const input = { text: 'test' };
      
      // Act
      const result = await processRequest(input);
      
      // Assert
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
    });

    it('should handle invalid input', async () => {
      // Test error cases
    });
  });
});
```

### Test Coverage
- Minimum 80% code coverage
- 100% coverage for critical paths
- Integration tests for each service

## Documentation Standards

### README Structure
1. Service name and purpose
2. Quick start guide
3. API documentation
4. Configuration options
5. Examples
6. Troubleshooting
7. Contributing guidelines

### Code Comments
```javascript
/**
 * Process article text and generate title suggestions
 * @param {string} text - The article text to process
 * @param {Object} options - Processing options
 * @param {number} options.count - Number of titles to generate
 * @returns {Promise<Array>} Array of title suggestions
 */
async function generateTitles(text, options = {}) {
  // Implementation
}
```

## Environment Variables

### Naming Convention
- Prefix with service name: `NEXUS_`
- Use UPPER_SNAKE_CASE
- Group by service

### Required Variables
```bash
# AWS Configuration
NEXUS_AWS_REGION=ap-northeast-2
NEXUS_AWS_ACCOUNT_ID=xxxxxxxxxxxx

# Service Configuration
NEXUS_API_KEY=xxx
NEXUS_BEDROCK_MODEL=anthropic.claude-3-sonnet

# Database
NEXUS_DYNAMO_TABLE=nexus-data
NEXUS_S3_BUCKET=nexus-storage

# Monitoring
NEXUS_LOG_LEVEL=info
NEXUS_ENABLE_XRAY=true
```

## Security Conventions

### Secrets Management
- Use AWS Secrets Manager
- Never commit secrets to repository
- Rotate keys every 90 days

### Input Validation
```javascript
const validateInput = (input) => {
  if (!input.text || typeof input.text !== 'string') {
    throw new ValidationError('Text is required and must be a string');
  }
  
  if (input.text.length > MAX_TEXT_LENGTH) {
    throw new ValidationError(`Text exceeds maximum length of ${MAX_TEXT_LENGTH}`);
  }
  
  return true;
};
```

### Error Handling
```javascript
try {
  const result = await riskyOperation();
  return { success: true, data: result };
} catch (error) {
  logger.error('Operation failed', { error, context });
  
  // Don't expose internal errors
  return {
    success: false,
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An error occurred processing your request'
    }
  };
}
```

## Performance Guidelines

### Lambda Optimization
- Keep functions small and focused
- Minimize cold starts with provisioned concurrency
- Use connection pooling for databases
- Cache frequently used data

### API Response Times
- Target: < 2 seconds for 95th percentile
- Maximum: 10 seconds before timeout
- Use async processing for long operations

## Monitoring & Logging

### Log Format
```javascript
logger.info('Processing request', {
  service: 'title',
  audience: 'internal',
  cards: 'two',
  userId: 'user123',
  timestamp: new Date().toISOString()
});
```

### Metrics to Track
- Request count
- Response time
- Error rate
- Token usage
- Cost per request

## Deployment Checklist

Before deploying:
- [ ] All tests passing
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] Security scan passed
- [ ] Performance tested
- [ ] Rollback plan ready