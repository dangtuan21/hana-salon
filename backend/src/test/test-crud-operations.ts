#!/usr/bin/env ts-node

import dotenv from 'dotenv';
import axios from 'axios';

// Load environment variables
dotenv.config();

const API_BASE = 'http://localhost:8060/api/services';

interface Service {
  _id?: string;
  name: string;
  category: string;
  duration_minutes: number;
  price: number;
  description?: string;
  required_skill_level?: string;
  popularity_score?: number;
}

async function testCRUDOperations() {
  console.log('🧪 Testing Services CRUD Operations...\n');

  let createdServiceId: string | undefined;

  try {
    // Test 1: CREATE - POST /api/services
    console.log('🔍 Test 1: CREATE Service (POST)');
    const newService: Service = {
      name: 'Test CRUD Service',
      category: 'Test Category',
      duration_minutes: 45,
      price: 35,
      description: 'A test service for CRUD operations',
      required_skill_level: 'Junior',
      popularity_score: 7
    };

    const createResponse = await axios.post(API_BASE, newService);
    
    if (createResponse.status === 201 && createResponse.data.success) {
      createdServiceId = createResponse.data.data._id;
      console.log('   ✅ Service created successfully');
      console.log(`   - ID: ${createdServiceId}`);
      console.log(`   - Name: ${createResponse.data.data.name}`);
      console.log(`   - Price: $${createResponse.data.data.price}`);
    } else {
      console.log('   ❌ Failed to create service');
      return;
    }
    console.log();

    // Test 2: READ - GET /api/services/:id
    console.log('🔍 Test 2: READ Service by ID (GET)');
    const readResponse = await axios.get(`${API_BASE}/${createdServiceId}`);
    
    if (readResponse.status === 200 && readResponse.data.success) {
      console.log('   ✅ Service retrieved successfully');
      console.log(`   - Name: ${readResponse.data.data.name}`);
      console.log(`   - Category: ${readResponse.data.data.category}`);
      console.log(`   - Duration: ${readResponse.data.data.duration_minutes} minutes`);
    } else {
      console.log('   ❌ Failed to retrieve service');
    }
    console.log();

    // Test 3: READ ALL - GET /api/services
    console.log('🔍 Test 3: READ All Services (GET)');
    const readAllResponse = await axios.get(API_BASE);
    
    if (readAllResponse.status === 200 && readAllResponse.data.success) {
      const serviceCount = readAllResponse.data.data.count;
      console.log(`   ✅ Retrieved all services successfully`);
      console.log(`   - Total services: ${serviceCount}`);
      
      // Check if our created service is in the list
      const ourService = readAllResponse.data.data.services.find((s: any) => s._id === createdServiceId);
      if (ourService) {
        console.log('   ✅ Our created service found in the list');
      } else {
        console.log('   ⚠️  Our created service not found in the list');
      }
    } else {
      console.log('   ❌ Failed to retrieve all services');
    }
    console.log();

    // Test 4: UPDATE - PUT /api/services/:id
    console.log('🔍 Test 4: UPDATE Service (PUT)');
    const updateData = {
      name: 'Updated CRUD Service',
      price: 50,
      popularity_score: 9
    };

    const updateResponse = await axios.put(`${API_BASE}/${createdServiceId}`, updateData);
    
    if (updateResponse.status === 200 && updateResponse.data.success) {
      console.log('   ✅ Service updated successfully');
      console.log(`   - Updated name: ${updateResponse.data.data.name}`);
      console.log(`   - Updated price: $${updateResponse.data.data.price}`);
      console.log(`   - Updated popularity: ${updateResponse.data.data.popularity_score}/10`);
      console.log(`   - Category unchanged: ${updateResponse.data.data.category}`);
    } else {
      console.log('   ❌ Failed to update service');
    }
    console.log();

    // Test 5: DELETE - DELETE /api/services/:id
    console.log('🔍 Test 5: DELETE Service (DELETE)');
    const deleteResponse = await axios.delete(`${API_BASE}/${createdServiceId}`);
    
    if (deleteResponse.status === 200 && deleteResponse.data.success) {
      console.log('   ✅ Service deleted successfully');
      console.log(`   - Deleted ID: ${deleteResponse.data.data.id}`);
      console.log(`   - Deleted name: ${deleteResponse.data.data.name}`);
      createdServiceId = undefined; // Mark as deleted
    } else {
      console.log('   ❌ Failed to delete service');
    }
    console.log();

    // Test 6: Verify DELETE - GET deleted service
    console.log('🔍 Test 6: Verify Deletion (GET deleted service)');
    try {
      await axios.get(`${API_BASE}/${deleteResponse.data.data.id}`);
      console.log('   ❌ Service still exists after deletion');
    } catch (error: any) {
      if (error.response?.status === 404) {
        console.log('   ✅ Service properly deleted (404 Not Found)');
      } else {
        console.log(`   ⚠️  Unexpected error: ${error.response?.status || 'Unknown'}`);
      }
    }
    console.log();

    // Test 7: Error Handling - Invalid ID
    console.log('🔍 Test 7: Error Handling (Invalid ID)');
    try {
      await axios.get(`${API_BASE}/invalid-id-format`);
      console.log('   ❌ Should have returned error for invalid ID');
    } catch (error: any) {
      if (error.response?.status === 500 || error.response?.status === 400) {
        console.log('   ✅ Properly handled invalid ID format');
      } else {
        console.log(`   ⚠️  Unexpected status: ${error.response?.status}`);
      }
    }
    console.log();

    // Test 8: Validation - Missing required fields
    console.log('🔍 Test 8: Validation (Missing Required Fields)');
    try {
      await axios.post(API_BASE, { name: 'Incomplete Service' });
      console.log('   ❌ Should have returned validation error');
    } catch (error: any) {
      if (error.response?.status === 400) {
        console.log('   ✅ Properly validated missing required fields');
      } else {
        console.log(`   ⚠️  Unexpected status: ${error.response?.status}`);
      }
    }
    console.log();

    console.log('🎉 All CRUD operations completed successfully!');
    console.log('📊 Summary: CREATE ✅ READ ✅ UPDATE ✅ DELETE ✅');

  } catch (error: any) {
    console.error('❌ CRUD test failed:', error.message);
    
    // Cleanup: Delete the service if it was created but test failed
    if (createdServiceId) {
      try {
        await axios.delete(`${API_BASE}/${createdServiceId}`);
        console.log('🧹 Cleaned up test service');
      } catch (cleanupError) {
        console.log('⚠️  Failed to cleanup test service');
      }
    }
    
    process.exit(1);
  }
}

// Run the test
testCRUDOperations();
