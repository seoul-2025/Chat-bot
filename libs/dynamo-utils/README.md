# DynamoDB Utils

## Purpose
DynamoDB utilities for data persistence in Nexus services.

## Features
- CRUD operations
- Batch operations
- Query and scan helpers
- Transaction support
- Index management
- TTL support

## Usage
```javascript
const { DynamoUtils } = require('@nexus/dynamo-utils');

const db = new DynamoUtils({
  tableName: 'nexus-data',
  region: 'ap-northeast-2'
});

// Put item
await db.put({
  id: '123',
  service: 'title',
  data: { ... }
});

// Get item
const item = await db.get('123');

// Query by index
const results = await db.query({
  indexName: 'service-index',
  keyCondition: 'service = :service',
  values: { ':service': 'title' }
});
```

## API
- `put(item)`: Put item into table
- `get(key)`: Get item by key
- `delete(key)`: Delete item
- `update(key, updates)`: Update item attributes
- `query(params)`: Query table or index
- `scan(params)`: Scan table
- `batchWrite(items)`: Batch write operations
- `transactWrite(transactions)`: Transactional writes