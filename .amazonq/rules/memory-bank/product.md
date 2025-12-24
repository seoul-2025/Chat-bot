# Nexus - AI-Powered Newsroom Platform

## Project Purpose
Nexus is a comprehensive AI-powered content creation platform built for Seoul Economic Daily, providing 6 specialized services that streamline newsroom operations through advanced AI capabilities. The platform leverages Anthropic Claude Opus 4.5 with real-time WebSocket streaming, native web search, and prompt caching optimization to deliver professional-grade content assistance.

## Value Proposition
- **Cost Efficiency**: 67-92% cost reduction through intelligent prompt caching
- **Real-time Processing**: WebSocket streaming for immediate AI responses
- **Professional Quality**: Specialized prompts and workflows for journalism
- **Scalable Architecture**: Serverless AWS infrastructure supporting high concurrency
- **Dual AI Engine**: Primary Anthropic API with AWS Bedrock fallback for reliability

## Key Features

### Core AI Services
1. **Proofreading Service (p1.sedaily.ai)**: Article proofreading, title generation, grammar correction
2. **Column Writing Assistant (r1.sedaily.ai)**: Column article writing with style guidance
3. **General Chat Service (f1.sedaily.ai)**: AI chat with web search integration
4. **Press Release Assistant (b1.sedaily.ai)**: Corporate/Government press release writing
5. **Press Release Service (w1.sedaily.ai)**: Systematic 12-step press release creation
6. **Title AI Conversation (t1.sedaily.ai)**: AI conversation with RAG support

### Advanced Capabilities
- **Web Search Integration**: Native search functionality with up to 5 searches per session
- **Prompt Caching**: Ephemeral caching reducing costs by 67-92%
- **Real-time Streaming**: WebSocket-based streaming responses
- **Multi-language Support**: Korean and English content processing
- **RAG Support**: Vector database integration for enhanced context (t1 service)

### Technical Excellence
- **High Performance**: Sub-2 second response times for 95th percentile
- **Scalability**: Auto-scaling Lambda functions supporting 1000+ concurrent users
- **Security**: API key authentication, encryption at rest and in transit
- **Monitoring**: Comprehensive CloudWatch logging and X-Ray tracing
- **Cost Optimization**: Intelligent resource management and usage tracking

## Target Users

### Primary Users
- **Journalists**: Article writing, proofreading, and title generation
- **Editors**: Content review, style checking, and quality assurance
- **PR Teams**: Press release creation and corporate communications
- **Content Creators**: Column writing and general content assistance

### Use Cases
- **Daily News Production**: Streamline article creation and editing workflows
- **Press Release Management**: Automated corporate and government announcement processing
- **Content Quality Assurance**: Grammar checking and style consistency
- **Research Assistance**: AI-powered information gathering with web search
- **Title Optimization**: Generate compelling headlines for articles
- **Multi-language Content**: Korean-English translation and localization

## Business Impact
- **Productivity Gains**: 3-5x faster content creation and editing
- **Cost Savings**: Significant reduction in AI processing costs through caching
- **Quality Improvement**: Consistent professional standards across all content
- **Scalability**: Handle peak newsroom demands without performance degradation
- **Innovation**: Cutting-edge AI technology providing competitive advantage

## Platform Architecture
Built on modern serverless architecture with React frontends, Python backends, and comprehensive AWS infrastructure including API Gateway, Lambda, DynamoDB, S3, and CloudFront for global content delivery.