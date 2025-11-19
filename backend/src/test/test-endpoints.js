#!/usr/bin/env node

const http = require('http');

const baseUrl = 'http://localhost:3060';
const endpoints = [
  '/',
  '/api',
  '/api/health',
  '/api/ready',
  '/api/live'
];

async function testEndpoint(path) {
  return new Promise((resolve) => {
    const options = {
      hostname: 'localhost',
      port: 3060,
      path: path,
      method: 'GET'
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve({
            path,
            status: res.statusCode,
            success: json.success || (res.statusCode === 200),
            message: json.message || 'OK'
          });
        } catch (e) {
          resolve({
            path,
            status: res.statusCode,
            success: false,
            message: 'Invalid JSON response'
          });
        }
      });
    });

    req.on('error', (err) => {
      resolve({
        path,
        status: 0,
        success: false,
        message: err.message
      });
    });

    req.setTimeout(5000, () => {
      req.destroy();
      resolve({
        path,
        status: 0,
        success: false,
        message: 'Timeout'
      });
    });

    req.end();
  });
}

async function runTests() {
  console.log('🧪 Testing Hana AI Backend Endpoints\n');
  
  for (const endpoint of endpoints) {
    const result = await testEndpoint(endpoint);
    const status = result.success ? '✅' : '❌';
    console.log(`${status} ${endpoint} - ${result.status} - ${result.message}`);
  }
  
  console.log('\n🎉 Test completed!');
}

runTests().catch(console.error);
