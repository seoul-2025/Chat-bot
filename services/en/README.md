# English Language Services

## Overview
This directory contains English language versions of Nexus AI services, optimized for English-speaking users and international markets.

## Services Available

### 1. Title Service
- **Path**: `/en/title/external/two/`
- **Status**: ✅ Implemented
- **Description**: English-optimized title generation for articles and content
- **Files**: 52,580

### 2. Regression Service
- **Path**: `/en/regression/external/two/`
- **Status**: ✅ Implemented  
- **Description**: English content revision and quality checking service
- **Files**: 52,592

## Language-First Architecture
The monorepo now follows a language-first structure:
```
services/
├── en/          # English services
│   ├── title/
│   └── regression/
├── ko/          # Korean services (to be migrated)
│   ├── title/
│   ├── proofreading/
│   └── ...
└── ...          # Other languages
```

## Key Features
- Optimized for English grammar and style
- Cultural localization for international audiences
- Enhanced NLP models for English text processing
- Compatible with existing Nexus infrastructure

## Deployment
Each service maintains its own deployment configuration in the respective directories.
Refer to individual service README files for specific deployment instructions.