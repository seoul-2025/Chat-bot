# Prompt Engine

## Purpose
Centralized prompt management and templating engine for all Nexus AI services.

## Features
- Dynamic prompt template rendering
- Variable substitution
- Prompt versioning support
- Template caching
- Prompt validation

## Usage
```javascript
const { PromptEngine } = require('@nexus/prompt-engine');

const engine = new PromptEngine();
const prompt = await engine.render('title-generation', {
  context: 'news article',
  language: 'korean'
});
```

## API
- `render(templateName, variables)`: Render a prompt template
- `loadTemplate(path)`: Load a template from file
- `validate(prompt)`: Validate prompt structure
- `getCached(key)`: Get cached prompt
- `clearCache()`: Clear prompt cache