#!/usr/bin/env ts-node

import dotenv from 'dotenv';
import database from '../config/database';
import { Service } from '../models/Service';

// Load environment variables
dotenv.config();

async function testDatabaseConnection() {
  console.log('🧪 Testing MongoDB Connection and Data...\n');

  try {
    // Connect to database
    console.log('📡 Connecting to MongoDB...');
    await database.connect();
    console.log('✅ Connected to MongoDB Atlas successfully\n');

    // Test 1: Check connection status
    console.log('🔍 Test 1: Connection Status');
    const isConnected = database.getConnectionStatus();
    console.log(`   Status: ${isConnected ? '✅ Connected' : '❌ Disconnected'}\n`);

    // Test 2: List collections
    console.log('🔍 Test 2: Available Collections');
    const db = database.getConnection().db;
    if (db) {
      const collections = await db.listCollections().toArray();
      console.log(`   Found ${collections.length} collections:`);
      collections.forEach(col => {
        console.log(`   - ${col.name} (${col.type})`);
      });
      console.log();
    }

    // Test 3: Count services
    console.log('🔍 Test 3: Services Collection');
    const servicesCount = await Service.countDocuments();
    console.log(`   Total services: ${servicesCount}`);
    
    if (servicesCount > 0) {
      console.log('   ✅ Services collection has data');
    } else {
      console.log('   ❌ Services collection is empty');
    }
    console.log();

    // Test 4: Service categories (from services data)
    console.log('🔍 Test 4: Service Categories');
    const categories = await Service.distinct('category');
    console.log(`   Categories found: ${categories.length}`);
    categories.forEach(cat => {
      console.log(`   - ${cat}`);
    });
    console.log('   💡 Note: Categories available via /api/services endpoint');
    console.log();

    // Test 5: Sample service data
    console.log('🔍 Test 5: Sample Service Data');
    const sampleService = await Service.findOne();
    if (sampleService) {
      console.log('   ✅ Sample service found:');
      console.log(`   - Name: ${sampleService.name}`);
      console.log(`   - Category: ${sampleService.category}`);
      console.log(`   - Duration: ${sampleService.duration_minutes} minutes`);
      console.log(`   - Price: $${sampleService.price}`);
      console.log(`   - Skill Level: ${sampleService.required_skill_level}`);
      console.log(`   - Popularity: ${sampleService.popularity_score}/10`);
    } else {
      console.log('   ❌ No services found');
    }
    console.log();

    // Test 6: Data validation
    console.log('🔍 Test 6: Data Validation');
    const services = await Service.find().limit(5);
    let validationPassed = true;

    services.forEach((service, index) => {
      const issues = [];
      
      if (!service.name || service.name.length === 0) issues.push('Missing name');
      if (!service.category || service.category.length === 0) issues.push('Missing category');
      if (!service.duration_minutes || service.duration_minutes <= 0) issues.push('Invalid duration');
      if (!service.price || service.price <= 0) issues.push('Invalid price');
      
      if (issues.length > 0) {
        console.log(`   ❌ Service ${index + 1} (${service.name}): ${issues.join(', ')}`);
        validationPassed = false;
      }
    });

    if (validationPassed) {
      console.log('   ✅ All sampled services have valid data structure');
    }
    console.log();

    console.log('🎉 Database tests completed successfully!');
    console.log(`📊 Summary: ${servicesCount} services across ${categories.length} categories`);

  } catch (error) {
    console.error('❌ Database test failed:', error);
    process.exit(1);
  } finally {
    // Disconnect
    await database.disconnect();
    console.log('\n📡 Disconnected from MongoDB');
    process.exit(0);
  }
}

// Run the test
testDatabaseConnection();
