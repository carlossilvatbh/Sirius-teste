#!/usr/bin/env python3
"""
Test script for Organogram Builder implementation
Tests the new hierarchical structure builder functionality
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sirius_project.settings')
django.setup()

from corporate.models import Entity, Structure, EntityOwnership
from parties.models import Party


class OrganogramBuilderTest:
    """Test the Organogram Builder functionality"""
    
    def __init__(self):
        self.client = Client()
        self.setup_test_data()
    
    def setup_test_data(self):
        """Create test data for organogram building"""
        print("🔧 Setting up test data...")
        
        # Create superuser for testing
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        
        # Create test entities
        self.entities = []
        
        # Delaware Corporation
        delaware_corp = Entity.objects.create(
            name="Delaware Holdings Corp",
            entity_type="CORP",
            jurisdiction="US",
            us_state="DE",
            total_shares=1000,
            tax_classification="C-Corp",
            implementation_time=15,
            complexity=3,
            confidentiality_level=2,
            asset_protection=3,
            banking_facility=4
        )
        self.entities.append(delaware_corp)
        
        # Bahamas IBC
        bahamas_ibc = Entity.objects.create(
            name="Bahamas International Ltd",
            entity_type="IBC",
            jurisdiction="BS",
            total_shares=50000,
            tax_classification="Foreign Corporation",
            implementation_time=21,
            complexity=4,
            confidentiality_level=5,
            asset_protection=5,
            banking_facility=3
        )
        self.entities.append(bahamas_ibc)
        
        # Wyoming LLC
        wyoming_llc = Entity.objects.create(
            name="Wyoming Privacy LLC",
            entity_type="LLC_DISREGARDED",
            jurisdiction="US",
            us_state="WY",
            tax_classification="Disregarded Entity",
            implementation_time=10,
            complexity=2,
            confidentiality_level=4,
            asset_protection=4,
            banking_facility=3
        )
        self.entities.append(wyoming_llc)
        
        # Nevada Trust
        nevada_trust = Entity.objects.create(
            name="Nevada Asset Protection Trust",
            entity_type="TRUST",
            jurisdiction="US",
            us_state="NV",
            tax_classification="Grantor Trust",
            implementation_time=30,
            complexity=5,
            confidentiality_level=5,
            asset_protection=5,
            banking_facility=2
        )
        self.entities.append(nevada_trust)
        
        # Create test parties
        self.parties = []
        
        john_smith = Party.objects.create(
            name="John Smith",
            nationality="US",
            tin="123-45-6789",
            email="john.smith@email.com",
            phone="+1-555-0123",
            address="123 Main St, New York, NY 10001"
        )
        self.parties.append(john_smith)
        
        maria_silva = Party.objects.create(
            name="Maria Silva",
            nationality="BR",
            tin="123.456.789-00",
            email="maria.silva@email.com",
            phone="+55-11-99999-9999",
            address="Rua das Flores, 123, São Paulo, SP"
        )
        self.parties.append(maria_silva)
        
        # Create test structure
        self.structure = Structure.objects.create(
            name="International Holding Structure",
            status="DRAFTING",
            description="Multi-jurisdictional holding structure for international operations"
        )
        
        print(f"✅ Created {len(self.entities)} entities")
        print(f"✅ Created {len(self.parties)} parties")
        print(f"✅ Created structure: {self.structure.name}")
    
    def test_admin_access(self):
        """Test admin access to organogram builder"""
        print("\n🔐 Testing admin access...")
        
        # Login as admin
        login_success = self.client.login(username='admin', password='admin123')
        if not login_success:
            print("❌ Failed to login as admin")
            return False
        
        # Test structure changelist access
        response = self.client.get('/admin/corporate/structure/')
        if response.status_code == 200:
            print("✅ Structure changelist accessible")
        else:
            print(f"❌ Structure changelist failed: {response.status_code}")
            return False
        
        # Test organogram builder access
        response = self.client.get(f'/admin/corporate/structure/{self.structure.id}/organogram/')
        if response.status_code == 200:
            print("✅ Organogram builder accessible")
        else:
            print(f"❌ Organogram builder failed: {response.status_code}")
            return False
        
        # Test entity library access
        response = self.client.get('/admin/corporate/entity-library/')
        if response.status_code == 200:
            print("✅ Entity library accessible")
        else:
            print(f"❌ Entity library failed: {response.status_code}")
            return False
        
        return True
    
    def test_entity_library_api(self):
        """Test entity library API endpoints"""
        print("\n📚 Testing entity library API...")
        
        # Login first
        self.client.login(username='admin', password='admin123')
        
        # Test entity creation API
        entity_data = {
            'name': 'Test API Entity',
            'entity_type': 'LLC_DISREGARDED',
            'jurisdiction': 'US',
            'total_shares': 100
        }
        
        response = self.client.post(
            '/admin/corporate/api/create-entity/',
            data=entity_data,
            content_type='application/json'
        )
        
        if response.status_code == 200:
            print("✅ Entity creation API working")
        else:
            print(f"❌ Entity creation API failed: {response.status_code}")
            return False
        
        # Test entity stats API
        entity_id = self.entities[0].id
        response = self.client.get(f'/admin/corporate/api/entity-stats/{entity_id}/')
        
        if response.status_code == 200:
            print("✅ Entity stats API working")
        else:
            print(f"❌ Entity stats API failed: {response.status_code}")
            return False
        
        # Test party stats API
        party_id = self.parties[0].id
        response = self.client.get(f'/admin/corporate/api/party-stats/{party_id}/')
        
        if response.status_code == 200:
            print("✅ Party stats API working")
        else:
            print(f"❌ Party stats API failed: {response.status_code}")
            return False
        
        # Test templates API
        response = self.client.get('/admin/corporate/api/templates/')
        
        if response.status_code == 200:
            print("✅ Templates API working")
        else:
            print(f"❌ Templates API failed: {response.status_code}")
            return False
        
        return True
    
    def test_organogram_data_structure(self):
        """Test organogram data structure and serialization"""
        print("\n🌳 Testing organogram data structure...")
        
        # Create some ownerships for testing
        ownership1 = EntityOwnership.objects.create(
            structure=self.structure,
            owner_ubo=self.parties[0],  # John Smith
            owned_entity=self.entities[0],  # Delaware Corp
            ownership_percentage=60.0,
            owned_shares=600,
            corporate_name="John Smith Holdings"
        )
        
        ownership2 = EntityOwnership.objects.create(
            structure=self.structure,
            owner_ubo=self.parties[1],  # Maria Silva
            owned_entity=self.entities[0],  # Delaware Corp
            ownership_percentage=40.0,
            owned_shares=400,
            corporate_name="Maria Silva Holdings"
        )
        
        ownership3 = EntityOwnership.objects.create(
            structure=self.structure,
            owner_entity=self.entities[0],  # Delaware Corp
            owned_entity=self.entities[1],  # Bahamas IBC
            ownership_percentage=100.0,
            owned_shares=50000,
            corporate_name="Delaware Holdings Corp"
        )
        
        print(f"✅ Created {EntityOwnership.objects.filter(structure=self.structure).count()} ownerships")
        
        # Test data serialization for organogram
        from corporate.admin_organogram import StructureOrganogramAdmin
        
        admin_instance = StructureOrganogramAdmin(Structure, None)
        organogram_data = admin_instance.get_organogram_data(self.structure)
        
        if 'nodes' in organogram_data and 'edges' in organogram_data:
            print(f"✅ Organogram data structure valid")
            print(f"   - Nodes: {len(organogram_data['nodes'])}")
            print(f"   - Edges: {len(organogram_data['edges'])}")
        else:
            print("❌ Invalid organogram data structure")
            return False
        
        return True
    
    def test_validation_system(self):
        """Test structure validation system"""
        print("\n✅ Testing validation system...")
        
        # Login first
        self.client.login(username='admin', password='admin123')
        
        # Test validation API
        response = self.client.get(f'/admin/corporate/structure/api/validate-structure/{self.structure.id}/')
        
        if response.status_code == 200:
            print("✅ Validation API working")
            
            # Check response content
            import json
            data = json.loads(response.content)
            
            if 'success' in data and 'validation_results' in data:
                print("✅ Validation response structure valid")
                
                results = data['validation_results']
                if 'overall_status' in results:
                    print(f"   - Overall status: {results['overall_status']}")
                
                if 'ownership_totals' in results:
                    print(f"   - Ownership totals calculated: {len(results['ownership_totals'])} entities")
                
            else:
                print("❌ Invalid validation response structure")
                return False
        else:
            print(f"❌ Validation API failed: {response.status_code}")
            return False
        
        return True
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Organogram Builder Tests")
        print("=" * 50)
        
        tests = [
            self.test_admin_access,
            self.test_entity_library_api,
            self.test_organogram_data_structure,
            self.test_validation_system
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    print(f"❌ Test failed: {test.__name__}")
            except Exception as e:
                print(f"❌ Test error in {test.__name__}: {str(e)}")
        
        print("\n" + "=" * 50)
        print(f"🏆 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Organogram Builder is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the implementation.")
        
        return passed == total


def main():
    """Main test function"""
    print("🌳 SIRIUS Organogram Builder Test Suite")
    print("Testing Phase 1: Structure Builder Hierárquico")
    print()
    
    tester = OrganogramBuilderTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Phase 1 implementation is ready!")
        print("🎯 Next: Implement Phase 2 - Entity Library & Quick Add")
    else:
        print("\n❌ Phase 1 needs fixes before proceeding")
    
    return success


if __name__ == '__main__':
    main()

