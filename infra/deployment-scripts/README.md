# Deployment Scripts

## Purpose
Automated deployment scripts for Nexus monorepo services.

## Scripts

### deploy-all.sh
Deploy all services to specified environment
```bash
./deploy-all.sh [dev|staging|prod]
```

### deploy-service.sh
Deploy specific service variant
```bash
./deploy-service.sh title internal one prod
```

### rollback.sh
Rollback to previous version
```bash
./rollback.sh title internal one
```

### validate.sh
Validate configurations before deployment
```bash
./validate.sh
```

## CI/CD Pipeline

### GitHub Actions Workflow
```yaml
name: Deploy Nexus Services
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm test
      - name: Deploy to staging
        run: ./deploy-all.sh staging
      - name: Run integration tests
        run: npm run test:integration
      - name: Deploy to production
        run: ./deploy-all.sh prod
```

## Environment Variables
```bash
# AWS Configuration
export AWS_REGION=ap-northeast-2
export AWS_ACCOUNT_ID=xxxxxxxxxxxx

# Deployment Configuration
export DEPLOY_BUCKET=nexus-deployments
export LAMBDA_ROLE=arn:aws:iam::xxxx:role/nexus-lambda-role

# Service Configuration
export API_GATEWAY_ID=xxxxxxxxxx
export VPC_ID=vpc-xxxxxxxxxx
export SUBNET_IDS=subnet-xxxxx,subnet-yyyyy
```

## Deployment Strategies

### Blue-Green Deployment
1. Deploy new version to green environment
2. Run smoke tests
3. Switch traffic to green
4. Keep blue as rollback option

### Canary Deployment
1. Deploy new version
2. Route 10% traffic to new version
3. Monitor metrics
4. Gradually increase traffic
5. Complete deployment or rollback

## Monitoring Deployment
```bash
# Check deployment status
aws cloudformation describe-stacks --stack-name nexus-$SERVICE-$ENV

# View Lambda logs
aws logs tail /aws/lambda/nexus-$SERVICE --follow

# Check API Gateway metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=nexus-api
```

## Rollback Procedure
1. Identify the issue
2. Check CloudWatch logs
3. Run rollback script
4. Verify rollback success
5. Investigate root cause

## Best Practices
1. Always deploy to staging first
2. Run integration tests before production
3. Monitor deployments actively
4. Keep deployment logs
5. Document deployment issues
6. Use infrastructure as code
7. Implement proper tagging strategy