# Nexus Service Guidelines

## Service Categories

### 1. Title Service
**Purpose**: Generate engaging and SEO-optimized titles for articles

#### Variants
- **Internal/One**: Single title suggestion for internal review
- **Internal/Two**: Two title options with rationale
- **Internal/Three**: Three diverse title approaches
- **External/One**: Polished single title for publication
- **External/Two**: Two publication-ready options
- **External/Three**: Three titles with A/B testing metadata

#### Prompt Guidelines
- Consider SEO keywords
- Match publication tone
- Include emotional hooks
- Optimize for click-through rate
- Respect character limits (60-70 chars)

### 2. Proofreading Service
**Purpose**: Grammar checking, style consistency, and readability improvements

#### Variants
- **Internal/One**: Basic grammar and spelling check
- **External/One**: Comprehensive editing with suggestions
- **External/Two**: Two versions - minimal and extensive edits

#### Proofreading Checklist
- Grammar and spelling
- Punctuation consistency
- Style guide compliance
- Fact verification flags
- Readability score
- Tone consistency

### 3. Bodo Service
**Purpose**: Process and format press releases (보도자료)

#### Variants
- **Internal/One**: Raw press release processing
- **External/One**: Formatted for publication
- **External/Two**: Two formats - brief and detailed

#### Processing Steps
1. Extract key information
2. Identify spokespersons
3. Highlight statistics
4. Format quotations
5. Add context
6. Generate summary

### 4. Foreign Service
**Purpose**: Translate and localize foreign news content

#### Variants
- **Internal/One**: Direct translation
- **External/One**: Localized for Korean audience
- **External/Two**: Two versions - literal and adaptive
- **External/Three**: Three regional variations

#### Translation Guidelines
- Preserve original meaning
- Adapt cultural references
- Convert measurements/currency
- Add local context
- Maintain journalistic tone
- Flag sensitive content

### 5. Regression Service
**Purpose**: Test content changes and version comparisons

#### Variants
- **Internal/One**: Basic regression testing
- **External/One**: Comprehensive change analysis

#### Testing Scope
- Content integrity
- Format preservation
- Link validation
- SEO impact
- Readability changes
- Legal compliance

### 6. Buddy Service
**Purpose**: AI writing assistant for journalists

#### Variants
- **Internal/One**: Basic assistance
- **External/One**: Full writing support
- **External/Two**: Collaborative dual-mode

#### Features
- Content ideation
- Research assistance
- Fact-checking support
- Style suggestions
- Quote integration
- Source management

## Card Configuration Guidelines

### One Card Layout
```
┌─────────────────────────┐
│                         │
│     Primary Content     │
│                         │
│      [Action Button]    │
└─────────────────────────┘
```

**Use Cases**:
- Single recommendation
- Binary decision
- Simple output
- Quick review

### Two Card Layout
```
┌────────────┬────────────┐
│  Option A  │  Option B  │
│            │            │
│  [Select]  │  [Select]  │
└────────────┴────────────┘
```

**Use Cases**:
- A/B comparison
- Alternative suggestions
- Different approaches
- User choice required

### Three Card Layout
```
┌──────┬──────┬──────┐
│  A   │  B   │  C   │
│      │      │      │
└──────┴──────┴──────┘
```

**Use Cases**:
- Multiple options
- Varied perspectives
- Comprehensive coverage
- Testing variations

## Audience Differentiation

### Internal Audience
**Characteristics**:
- Newsroom staff
- Editors and journalists
- Technical understanding
- Need detailed information

**Features**:
- Technical metadata
- Detailed explanations
- Debug information
- Performance metrics
- Cost tracking

### External Audience
**Characteristics**:
- End users
- Readers
- Third-party clients
- Public API users

**Features**:
- Polished output
- Clean formatting
- No technical jargon
- Optimized response time
- Rate limiting

## Service Quality Standards

### Performance Metrics
| Metric | Target | Maximum |
|--------|--------|---------|
| Response Time | < 2s | 10s |
| Success Rate | > 99% | - |
| Error Rate | < 1% | 5% |
| Availability | 99.9% | - |

### Content Quality
- Accuracy: > 95%
- Relevance: > 90%
- Readability: Grade 8-10
- Originality: > 80%

## Prompt Engineering Best Practices

### System Prompts
```
You are a professional {role} working for a Korean news organization.
Your task is to {specific task}.
Follow these guidelines:
1. {Guideline 1}
2. {Guideline 2}
3. {Guideline 3}
```

### User Prompts
```
Input: {user_input}
Context: {additional_context}
Requirements: {specific_requirements}
Output format: {format_specification}
```

### Temperature Settings
- **Creative tasks** (titles, ideation): 0.7-0.9
- **Analytical tasks** (proofreading): 0.3-0.5
- **Translation**: 0.2-0.4
- **Factual content**: 0.1-0.3

## Error Handling

### Common Errors
1. **Input Too Long**
   - Split into chunks
   - Process sequentially
   - Combine results

2. **Timeout**
   - Implement retry logic
   - Use async processing
   - Cache partial results

3. **Rate Limiting**
   - Queue requests
   - Implement backoff
   - Use connection pooling

### Error Messages
```javascript
const ERROR_MESSAGES = {
  INVALID_INPUT: '입력 텍스트가 유효하지 않습니다',
  TEXT_TOO_LONG: '텍스트가 너무 깁니다 (최대 10,000자)',
  SERVICE_UNAVAILABLE: '서비스를 일시적으로 사용할 수 없습니다',
  RATE_LIMITED: '요청 한도를 초과했습니다'
};
```

## Integration Patterns

### Synchronous Processing
```javascript
// For quick operations (< 2s)
const result = await processSync(input);
return { success: true, data: result };
```

### Asynchronous Processing
```javascript
// For long operations (> 2s)
const jobId = await startAsyncJob(input);
return { 
  success: true, 
  jobId, 
  statusUrl: `/status/${jobId}` 
};
```

### Webhook Pattern
```javascript
// For external integrations
await processAndNotify(input, {
  webhookUrl: client.callbackUrl,
  retryCount: 3
});
```

## Monitoring & Analytics

### Key Metrics to Track
1. **Usage Metrics**
   - Requests per service
   - Unique users
   - Peak usage times
   - Geographic distribution

2. **Performance Metrics**
   - Average response time
   - P95 latency
   - Cold start frequency
   - Memory usage

3. **Business Metrics**
   - Articles processed
   - Time saved
   - Quality improvements
   - User satisfaction

### Dashboard Components
- Real-time request monitor
- Service health status
- Error rate trends
- Cost analysis
- User activity heatmap

## Service Lifecycle

### Development Phase
1. Define requirements
2. Design prompts
3. Implement logic
4. Write tests
5. Document API

### Testing Phase
1. Unit testing
2. Integration testing
3. Load testing
4. User acceptance testing
5. Security testing

### Deployment Phase
1. Stage deployment
2. Smoke tests
3. Canary release
4. Full deployment
5. Monitor metrics

### Maintenance Phase
1. Monitor performance
2. Collect feedback
3. Optimize prompts
4. Update documentation
5. Plan improvements

## Future Enhancements

### Planned Features
- Multi-language support
- Real-time collaboration
- Advanced analytics
- Custom model fine-tuning
- Batch processing
- WebSocket support

### Research Areas
- Prompt optimization
- Context preservation
- Cost reduction
- Latency improvement
- Accuracy enhancement