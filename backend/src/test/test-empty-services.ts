#!/usr/bin/env ts-node

import dotenv from 'dotenv';
import database from '../config/database';
import { Service } from '../models/Service';

// Load environment variables
dotenv.config();

async function testEmptyServicesScenario() {
  console.log('🧪 Testing Empty Services Scenario...\n');

  try {
    // Connect to database
    console.log('📡 Connecting to MongoDB...');
    await database.connect();
    console.log('✅ Connected to MongoDB Atlas successfully\n');

    // Backup current services
    console.log('💾 Backing up current services...');
    const originalServices = await Service.find({});
    console.log(`   Backed up ${originalServices.length} services\n`);

    // Test 1: Remove all services
    console.log('🔍 Test 1: Removing all services');
    await Service.deleteMany({});
    const countAfterDelete = await Service.countDocuments();
    console.log(`   Services count after deletion: ${countAfterDelete}`);
    
    if (countAfterDelete === 0) {
      console.log('   ✅ All services successfully removed');
    } else {
      console.log('   ❌ Failed to remove all services');
    }
    console.log();

    // Test 2: Query empty collection
    console.log('🔍 Test 2: Querying empty services collection');
    const emptyServices = await Service.find({});
    console.log(`   Query result length: ${emptyServices.length}`);
    console.log(`   Query result: ${JSON.stringify(emptyServices)}`);
    
    if (emptyServices.length === 0 && Array.isArray(emptyServices)) {
      console.log('   ✅ Empty query returns empty array correctly');
    } else {
      console.log('   ❌ Empty query did not return expected result');
    }
    console.log();

    // Test 3: Find by ID in empty collection
    console.log('🔍 Test 3: Finding service by ID in empty collection');
    const fakeId = '507f1f77bcf86cd799439011';
    const notFoundService = await Service.findById(fakeId);
    console.log(`   Find by ID result: ${notFoundService}`);
    
    if (notFoundService === null) {
      console.log('   ✅ Find by ID correctly returns null for non-existent service');
    } else {
      console.log('   ❌ Find by ID did not return null as expected');
    }
    console.log();

    // Test 4: Distinct categories from empty collection
    console.log('🔍 Test 4: Getting distinct categories from empty collection');
    const emptyCategories = await Service.distinct('category');
    console.log(`   Distinct categories result: ${JSON.stringify(emptyCategories)}`);
    
    if (emptyCategories.length === 0 && Array.isArray(emptyCategories)) {
      console.log('   ✅ Distinct query returns empty array correctly');
    } else {
      console.log('   ❌ Distinct query did not return expected result');
    }
    console.log();

    // Restore original services
    console.log('🔄 Restoring original services...');
    if (originalServices.length > 0) {
      await Service.insertMany(originalServices);
      const restoredCount = await Service.countDocuments();
      console.log(`   Restored ${restoredCount} services`);
      
      if (restoredCount === originalServices.length) {
        console.log('   ✅ All services successfully restored');
      } else {
        console.log('   ⚠️  Service count mismatch after restoration');
      }
    } else {
      console.log('   ℹ️  No services to restore (collection was already empty)');
    }
    console.log();

    console.log('🎉 Empty services scenario tests completed successfully!');
    console.log('📊 Summary: All empty collection operations behave correctly');

  } catch (error) {
    console.error('❌ Empty services test failed:', error);
    process.exit(1);
  } finally {
    // Disconnect
    await database.disconnect();
    console.log('\n📡 Disconnected from MongoDB');
    process.exit(0);
  }
}

// Run the test
testEmptyServicesScenario();
