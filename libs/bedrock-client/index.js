'use strict';

const AWS = require('aws-sdk');

class BedrockClient {
  constructor(config = {}) {
    this.region = config.region || 'ap-northeast-2';
    this.model = config.model || 'anthropic.claude-3-sonnet-20240229';
    this.maxRetries = config.maxRetries || 3;
    
    this.bedrock = new AWS.BedrockRuntime({
      region: this.region
    });
  }

  async invoke(params) {
    const { system, messages, temperature = 0.7, maxTokens = 4096 } = params;
    
    const payload = {
      anthropic_version: 'bedrock-2023-05-31',
      system,
      messages,
      temperature,
      max_tokens: maxTokens
    };

    try {
      const response = await this.bedrock.invokeModel({
        modelId: this.model,
        contentType: 'application/json',
        accept: 'application/json',
        body: JSON.stringify(payload)
      }).promise();

      return JSON.parse(response.body.toString());
    } catch (error) {
      console.error('Bedrock invocation error:', error);
      throw error;
    }
  }

  async stream(params) {
    // TODO: Implement streaming
    throw new Error('Streaming not yet implemented');
  }

  countTokens(text) {
    // Rough estimate - actual implementation would use proper tokenizer
    return Math.ceil(text.length / 4);
  }

  estimateCost(tokens) {
    // Example pricing - adjust based on actual model
    const pricePerThousandTokens = 0.003;
    return (tokens / 1000) * pricePerThousandTokens;
  }

  async listModels() {
    // TODO: Implement model listing
    return [
      'anthropic.claude-3-sonnet-20240229',
      'anthropic.claude-3-haiku-20240307'
    ];
  }
}

module.exports = { BedrockClient };