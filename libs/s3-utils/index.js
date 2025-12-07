'use strict';

const AWS = require('aws-sdk');

class S3Utils {
  constructor(config = {}) {
    this.bucket = config.bucket || process.env.S3_BUCKET;
    this.region = config.region || 'ap-northeast-2';
    
    this.s3 = new AWS.S3({
      region: this.region
    });
  }

  async upload(key, data, options = {}) {
    const params = {
      Bucket: this.bucket,
      Key: key,
      Body: data,
      ...options
    };

    try {
      const result = await this.s3.upload(params).promise();
      return result;
    } catch (error) {
      console.error('S3 upload error:', error);
      throw error;
    }
  }

  async download(key) {
    const params = {
      Bucket: this.bucket,
      Key: key
    };

    try {
      const result = await this.s3.getObject(params).promise();
      return result.Body;
    } catch (error) {
      console.error('S3 download error:', error);
      throw error;
    }
  }

  async delete(key) {
    const params = {
      Bucket: this.bucket,
      Key: key
    };

    try {
      await this.s3.deleteObject(params).promise();
      return true;
    } catch (error) {
      console.error('S3 delete error:', error);
      throw error;
    }
  }

  async list(prefix = '', maxKeys = 1000) {
    const params = {
      Bucket: this.bucket,
      Prefix: prefix,
      MaxKeys: maxKeys
    };

    try {
      const result = await this.s3.listObjectsV2(params).promise();
      return result.Contents || [];
    } catch (error) {
      console.error('S3 list error:', error);
      throw error;
    }
  }

  async getPresignedUrl(key, expires = 3600) {
    const params = {
      Bucket: this.bucket,
      Key: key,
      Expires: expires
    };

    try {
      return await this.s3.getSignedUrlPromise('getObject', params);
    } catch (error) {
      console.error('S3 presigned URL error:', error);
      throw error;
    }
  }

  async copyObject(sourceKey, destKey) {
    const params = {
      Bucket: this.bucket,
      CopySource: `${this.bucket}/${sourceKey}`,
      Key: destKey
    };

    try {
      await this.s3.copyObject(params).promise();
      return true;
    } catch (error) {
      console.error('S3 copy error:', error);
      throw error;
    }
  }
}

module.exports = { S3Utils };