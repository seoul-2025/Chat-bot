'use strict';

const AWS = require('aws-sdk');

class DynamoUtils {
  constructor(config = {}) {
    this.tableName = config.tableName || process.env.DYNAMO_TABLE;
    this.region = config.region || 'ap-northeast-2';
    
    this.dynamodb = new AWS.DynamoDB.DocumentClient({
      region: this.region
    });
  }

  async put(item) {
    const params = {
      TableName: this.tableName,
      Item: {
        ...item,
        createdAt: item.createdAt || new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    };

    try {
      await this.dynamodb.put(params).promise();
      return item;
    } catch (error) {
      console.error('DynamoDB put error:', error);
      throw error;
    }
  }

  async get(key) {
    const params = {
      TableName: this.tableName,
      Key: typeof key === 'object' ? key : { id: key }
    };

    try {
      const result = await this.dynamodb.get(params).promise();
      return result.Item;
    } catch (error) {
      console.error('DynamoDB get error:', error);
      throw error;
    }
  }

  async delete(key) {
    const params = {
      TableName: this.tableName,
      Key: typeof key === 'object' ? key : { id: key }
    };

    try {
      await this.dynamodb.delete(params).promise();
      return true;
    } catch (error) {
      console.error('DynamoDB delete error:', error);
      throw error;
    }
  }

  async update(key, updates) {
    const updateExpression = [];
    const expressionAttributeNames = {};
    const expressionAttributeValues = {};

    Object.keys(updates).forEach((field, index) => {
      const placeholder = `#field${index}`;
      const valuePlaceholder = `:value${index}`;
      
      updateExpression.push(`${placeholder} = ${valuePlaceholder}`);
      expressionAttributeNames[placeholder] = field;
      expressionAttributeValues[valuePlaceholder] = updates[field];
    });

    const params = {
      TableName: this.tableName,
      Key: typeof key === 'object' ? key : { id: key },
      UpdateExpression: `SET ${updateExpression.join(', ')}, updatedAt = :updatedAt`,
      ExpressionAttributeNames: expressionAttributeNames,
      ExpressionAttributeValues: {
        ...expressionAttributeValues,
        ':updatedAt': new Date().toISOString()
      },
      ReturnValues: 'ALL_NEW'
    };

    try {
      const result = await this.dynamodb.update(params).promise();
      return result.Attributes;
    } catch (error) {
      console.error('DynamoDB update error:', error);
      throw error;
    }
  }

  async query(params) {
    const queryParams = {
      TableName: this.tableName,
      ...params
    };

    try {
      const result = await this.dynamodb.query(queryParams).promise();
      return result.Items;
    } catch (error) {
      console.error('DynamoDB query error:', error);
      throw error;
    }
  }

  async scan(params = {}) {
    const scanParams = {
      TableName: this.tableName,
      ...params
    };

    try {
      const result = await this.dynamodb.scan(scanParams).promise();
      return result.Items;
    } catch (error) {
      console.error('DynamoDB scan error:', error);
      throw error;
    }
  }

  async batchWrite(items) {
    const chunks = [];
    for (let i = 0; i < items.length; i += 25) {
      chunks.push(items.slice(i, i + 25));
    }

    const results = [];
    for (const chunk of chunks) {
      const params = {
        RequestItems: {
          [this.tableName]: chunk
        }
      };

      try {
        const result = await this.dynamodb.batchWrite(params).promise();
        results.push(result);
      } catch (error) {
        console.error('DynamoDB batch write error:', error);
        throw error;
      }
    }

    return results;
  }

  async transactWrite(transactions) {
    const params = {
      TransactItems: transactions
    };

    try {
      await this.dynamodb.transactWrite(params).promise();
      return true;
    } catch (error) {
      console.error('DynamoDB transaction error:', error);
      throw error;
    }
  }
}

module.exports = { DynamoUtils };