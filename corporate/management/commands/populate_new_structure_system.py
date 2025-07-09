from django.core.management.base import BaseCommand
from django.db import transaction
from corporate.models import Entity, Structure, StructureNode, NodeOwnership
from parties.models import Party


class Command(BaseCommand):
    help = 'Populate the new structure system with example data based on user feedback'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Populating new structure system...')
        )

        with transaction.atomic():
            # Create Entity Templates (Reusable)
            self.create_entity_templates()
            
            # Create Parties
            self.create_parties()
            
            # Create Structure with Multi-level Nodes
            self.create_multi_level_structure()
            
            # Create "Holding Família Caetano" example
            self.create_caetano_family_holding()

        self.stdout.write(
            self.style.SUCCESS('✅ New structure system populated successfully!')
        )

    def create_entity_templates(self):
        """Create reusable entity templates"""
        self.stdout.write('📋 Creating entity templates...')
        
        # Wyoming DAO LLC Template
        wyoming_llc, created = Entity.objects.get_or_create(
            name="Wyoming DAO LLC",
            defaults={
                'entity_type': 'LLC_DISREGARDED',
                'tax_classification': 'LLC_DISREGARDED_ENTITY',
                'jurisdiction': 'US',
                'us_state': 'WY',
                'implementation_templates': 'Operating Agreement, Memorandum',
                'implementation_time': 15,
                'complexity': 2,
                'tax_impact_usa': 'LLC Disregarded Entity - Pass-through taxation',
                'tax_impact_brazil': 'Transparent entity for Brazilian tax purposes',
                'tax_impact_others': 'Wyoming state tax advantages',
                'total_shares': 1000,
                'active': True,
            }
        )
        if created:
            self.stdout.write(f'  ✅ Created: {wyoming_llc.name}')
        
        # Bahamas Fund Template
        bahamas_fund, created = Entity.objects.get_or_create(
            name="Bahamas Fund",
            defaults={
                'entity_type': 'FUND',
                'tax_classification': 'FUND',
                'jurisdiction': 'BS',
                'implementation_templates': 'Operating Agreement, Memorandum',
                'implementation_time': 30,
                'complexity': 4,
                'tax_impact_usa': 'Foreign fund - CFC rules may apply',
                'tax_impact_brazil': 'Foreign investment fund regulations',
                'tax_impact_others': 'Bahamas tax-exempt status',
                'total_shares': 5000,
                'active': True,
            }
        )
        if created:
            self.stdout.write(f'  ✅ Created: {bahamas_fund.name}')
        
        # Delaware Corporation Template
        delaware_corp, created = Entity.objects.get_or_create(
            name="Delaware Corporation",
            defaults={
                'entity_type': 'CORP',
                'tax_classification': 'US_CORP',
                'jurisdiction': 'US',
                'us_state': 'DE',
                'implementation_templates': 'Articles of Incorporation, Bylaws',
                'implementation_time': 10,
                'complexity': 3,
                'tax_impact_usa': 'C-Corporation - Double taxation',
                'tax_impact_brazil': 'Foreign corporation - withholding tax',
                'tax_impact_others': 'Delaware corporate advantages',
                'total_shares': 10000,
                'active': True,
            }
        )
        if created:
            self.stdout.write(f'  ✅ Created: {delaware_corp.name}')

    def create_parties(self):
        """Create example parties"""
        self.stdout.write('👥 Creating parties...')
        
        parties_data = [
            {'name': 'João da Silva', 'tax_identification_number': '123.456.789-01'},
            {'name': 'Maria Caetano', 'tax_identification_number': '234.567.890-12'},
            {'name': 'José Caetano', 'tax_identification_number': '345.678.901-23'},
            {'name': 'Ana Caetano', 'tax_identification_number': '456.789.012-34'},
        ]
        
        for party_data in parties_data:
            party, created = Party.objects.get_or_create(
                name=party_data['name'],
                defaults=party_data
            )
            if created:
                self.stdout.write(f'  ✅ Created party: {party.name}')

    def create_multi_level_structure(self):
        """Create multi-level structure example"""
        self.stdout.write('🏗️ Creating multi-level structure...')
        
        # Create Structure
        structure, created = Structure.objects.get_or_create(
            name="Exemplo Multi-Nível Structure",
            defaults={
                'description': 'Estrutura de 4 níveis demonstrando entities reutilizáveis',
                'status': 'DRAFTING'
            }
        )
        if created:
            self.stdout.write(f'  ✅ Created structure: {structure.name}')
        
        # Get templates and parties
        wyoming_template = Entity.objects.get(name="Wyoming DAO LLC")
        bahamas_template = Entity.objects.get(name="Bahamas Fund")
        joao = Party.objects.get(name="João da Silva")
        
        # Level 1 Nodes
        primary_wyoming = StructureNode.objects.create(
            entity_template=wyoming_template,
            structure=structure,
            custom_name="João's Primary Wyoming LLC",
            total_shares=1000,
            corporate_name="Primary Wyoming DAO LLC",
            hash_number="WY001",
            level=1
        )
        
        investment_fund_l1 = StructureNode.objects.create(
            entity_template=bahamas_template,
            structure=structure,
            custom_name="Investment Fund Level 1",
            total_shares=5000,
            corporate_name="Bahamas Investment Fund I",
            hash_number="BS001",
            level=1
        )
        
        # Level 2 Nodes
        secondary_wyoming = StructureNode.objects.create(
            entity_template=wyoming_template,
            structure=structure,
            custom_name="Secondary Wyoming LLC",
            total_shares=800,
            corporate_name="Secondary Wyoming DAO LLC",
            hash_number="WY002",
            level=2,
            parent_node=primary_wyoming
        )
        
        investment_fund_l2 = StructureNode.objects.create(
            entity_template=bahamas_template,
            structure=structure,
            custom_name="Investment Fund Level 2",
            total_shares=3000,
            corporate_name="Bahamas Investment Fund II",
            hash_number="BS002",
            level=2,
            parent_node=investment_fund_l1
        )
        
        # Level 3 Node
        tertiary_wyoming = StructureNode.objects.create(
            entity_template=wyoming_template,
            structure=structure,
            custom_name="Tertiary Wyoming LLC",
            total_shares=600,
            corporate_name="Tertiary Wyoming DAO LLC",
            hash_number="WY003",
            level=3,
            parent_node=secondary_wyoming
        )
        
        # Level 4 Node
        final_fund = StructureNode.objects.create(
            entity_template=bahamas_template,
            structure=structure,
            custom_name="Final Investment Fund",
            total_shares=2000,
            corporate_name="Final Bahamas Investment Fund",
            hash_number="BS003",
            level=4,
            parent_node=tertiary_wyoming
        )
        
        # Create Ownership Relationships
        self.stdout.write('🔗 Creating ownership relationships...')
        
        # Level 1 Ownerships (Party → Node)
        NodeOwnership.objects.create(
            owner_party=joao,
            owned_node=primary_wyoming,
            ownership_percentage=70.00,
            owned_shares=700,
            share_value_usd=100.00
        )
        
        NodeOwnership.objects.create(
            owner_party=joao,
            owned_node=investment_fund_l1,
            ownership_percentage=100.00,
            owned_shares=5000,
            share_value_usd=50.00
        )
        
        # Level 2 Ownerships (Node → Node)
        NodeOwnership.objects.create(
            owner_node=primary_wyoming,
            owned_node=secondary_wyoming,
            ownership_percentage=85.00,
            owned_shares=680,
            share_value_usd=150.00
        )
        
        NodeOwnership.objects.create(
            owner_node=investment_fund_l1,
            owned_node=investment_fund_l2,
            ownership_percentage=90.00,
            owned_shares=2700,
            share_value_usd=75.00
        )
        
        # Level 3 Ownership
        NodeOwnership.objects.create(
            owner_node=secondary_wyoming,
            owned_node=tertiary_wyoming,
            ownership_percentage=95.00,
            owned_shares=570,
            share_value_usd=200.00
        )
        
        # Level 4 Ownership
        NodeOwnership.objects.create(
            owner_node=tertiary_wyoming,
            owned_node=final_fund,
            ownership_percentage=100.00,
            owned_shares=2000,
            share_value_usd=125.00
        )
        
        self.stdout.write(f'  ✅ Created 6 ownership relationships')

    def create_caetano_family_holding(self):
        """Create Holding Família Caetano example"""
        self.stdout.write('👨‍👩‍👧‍👦 Creating Holding Família Caetano...')
        
        # Create Structure
        caetano_structure, created = Structure.objects.get_or_create(
            name="Holding Família Caetano",
            defaults={
                'description': 'Estrutura de 2 níveis: Bahamas 123 → Wyoming 1 + Wyoming 2',
                'status': 'DRAFTING'
            }
        )
        if created:
            self.stdout.write(f'  ✅ Created structure: {caetano_structure.name}')
        
        # Get templates and parties
        wyoming_template = Entity.objects.get(name="Wyoming DAO LLC")
        bahamas_template = Entity.objects.get(name="Bahamas Fund")
        maria = Party.objects.get(name="Maria Caetano")
        jose = Party.objects.get(name="José Caetano")
        ana = Party.objects.get(name="Ana Caetano")
        
        # Level 1: Bahamas 123
        bahamas_123 = StructureNode.objects.create(
            entity_template=bahamas_template,
            structure=caetano_structure,
            custom_name="Bahamas 123",
            total_shares=1000,
            corporate_name="Caetano Family Fund 123",
            hash_number="CF123",
            level=1
        )
        
        # Level 2: Wyoming 1 and Wyoming 2
        wyoming_1 = StructureNode.objects.create(
            entity_template=wyoming_template,
            structure=caetano_structure,
            custom_name="Wyoming 1",
            total_shares=500,
            corporate_name="Caetano Wyoming LLC 1",
            hash_number="CW001",
            level=2,
            parent_node=bahamas_123
        )
        
        wyoming_2 = StructureNode.objects.create(
            entity_template=wyoming_template,
            structure=caetano_structure,
            custom_name="Wyoming 2",
            total_shares=800,
            corporate_name="Caetano Wyoming LLC 2",
            hash_number="CW002",
            level=2,
            parent_node=bahamas_123
        )
        
        # Ownership Relationships
        # Level 1: 50% Maria + 50% José → Bahamas 123
        NodeOwnership.objects.create(
            owner_party=maria,
            owned_node=bahamas_123,
            ownership_percentage=50.00,
            owned_shares=500,
            share_value_usd=1000.00
        )
        
        NodeOwnership.objects.create(
            owner_party=jose,
            owned_node=bahamas_123,
            ownership_percentage=50.00,
            owned_shares=500,
            share_value_usd=1000.00
        )
        
        # Level 2.1: 50% Bahamas 123 + 50% Ana → Wyoming 1
        NodeOwnership.objects.create(
            owner_node=bahamas_123,
            owned_node=wyoming_1,
            ownership_percentage=50.00,
            owned_shares=250,
            share_value_usd=2000.00
        )
        
        NodeOwnership.objects.create(
            owner_party=ana,
            owned_node=wyoming_1,
            ownership_percentage=50.00,
            owned_shares=250,
            share_value_usd=2000.00
        )
        
        # Level 2.2: 100% Bahamas 123 → Wyoming 2
        NodeOwnership.objects.create(
            owner_node=bahamas_123,
            owned_node=wyoming_2,
            ownership_percentage=100.00,
            owned_shares=800,
            share_value_usd=1500.00
        )
        
        self.stdout.write(f'  ✅ Created Caetano family structure with 5 ownership relationships')

    def print_summary(self):
        """Print summary of created data"""
        self.stdout.write('\n📊 SUMMARY:')
        self.stdout.write(f'  Entities (Templates): {Entity.objects.count()}')
        self.stdout.write(f'  Structures: {Structure.objects.count()}')
        self.stdout.write(f'  Structure Nodes: {StructureNode.objects.count()}')
        self.stdout.write(f'  Node Ownerships: {NodeOwnership.objects.count()}')
        self.stdout.write(f'  Parties: {Party.objects.count()}')

