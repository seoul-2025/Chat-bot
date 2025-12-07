# Lambda Layer Configuration

## Purpose
Shared Lambda layers for common dependencies and utilities across all Nexus services.

## Layers

### nexus-core-layer
Core utilities and AWS SDK configurations
- AWS SDK
- Axios
- Lodash
- UUID
- Moment.js

### nexus-ai-layer
AI/ML related dependencies
- @anthropic-ai/sdk
- OpenAI SDK
- Langchain
- Token counting libraries

### nexus-utils-layer
Internal Nexus utilities
- @nexus/prompt-engine
- @nexus/bedrock-client
- @nexus/auth-utils
- @nexus/s3-utils
- @nexus/dynamo-utils

## Building Layers

```bash
# Build core layer
cd layers/nexus-core
npm install --production
zip -r nexus-core-layer.zip node_modules

# Build AI layer
cd layers/nexus-ai
npm install --production
zip -r nexus-ai-layer.zip node_modules

# Build utils layer
cd layers/nexus-utils
npm install --production
zip -r nexus-utils-layer.zip node_modules
```

## Deploying Layers

```bash
# Publish layer
aws lambda publish-layer-version \
  --layer-name nexus-core-layer \
  --description "Core utilities for Nexus services" \
  --zip-file fileb://nexus-core-layer.zip \
  --compatible-runtimes nodejs18.x

# Update function configuration
aws lambda update-function-configuration \
  --function-name nexus-title-internal-one \
  --layers arn:aws:lambda:region:account:layer:nexus-core-layer:1
```

## Layer Versioning
- Major version: Breaking changes
- Minor version: New features
- Patch version: Bug fixes

## Layer ARNs
```yaml
# Production layers
nexus-core-layer: arn:aws:lambda:ap-northeast-2:xxxx:layer:nexus-core-layer:latest
nexus-ai-layer: arn:aws:lambda:ap-northeast-2:xxxx:layer:nexus-ai-layer:latest
nexus-utils-layer: arn:aws:lambda:ap-northeast-2:xxxx:layer:nexus-utils-layer:latest
```

## Size Limits
- Maximum layer size: 50MB (zipped)
- Maximum total unzipped size: 250MB
- Maximum number of layers: 5

## Best Practices
1. Keep layers small and focused
2. Version layers properly
3. Test layer updates in staging first
4. Document breaking changes
5. Clean up old layer versions regularly