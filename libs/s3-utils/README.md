# S3 Utils

## Purpose
Amazon S3 utilities for file storage and retrieval in Nexus services.

## Features
- File upload/download
- Presigned URL generation
- Bucket operations
- Multipart upload support
- Object metadata management
- Versioning support

## Usage
```javascript
const { S3Utils } = require('@nexus/s3-utils');

const s3 = new S3Utils({
  bucket: 'nexus-storage',
  region: 'ap-northeast-2'
});

// Upload file
await s3.upload('path/to/file.pdf', buffer);

// Generate presigned URL
const url = await s3.getPresignedUrl('path/to/file.pdf');

// Download file
const data = await s3.download('path/to/file.pdf');
```

## API
- `upload(key, data, options)`: Upload file to S3
- `download(key)`: Download file from S3
- `delete(key)`: Delete file from S3
- `list(prefix)`: List objects with prefix
- `getPresignedUrl(key, expires)`: Generate presigned URL
- `copyObject(source, dest)`: Copy object within S3