"""
Usage Examples for the Autonomous Insurance Claims Processing Agent

This module demonstrates various ways to use the claims processing system.

Author: Vamshi Vardhan
Date: February 6, 2026
"""

import json
from claims_processor import FNOLProcessor, ClaimsProcessingAgent
from pdf_processor import PDFClaimsProcessor


# =============================================================================
# EXAMPLE 1: Simple Single Document Processing
# =============================================================================

def example_1_simple_text_processing():
    """Process a simple text claim"""
    claim_text = """
    FIRST NOTICE OF LOSS
    
    Policy Number: POL-2024-001234
    Policyholder Name: John Smith
    Effective Dates: 01/01/2024 - 12/31/2024
    
    Incident Date: 01/15/2024
    Time: 14:30 PM
    Location: 123 Main Street, Springfield, IL
    
    Description: Vehicle collision. Minor injuries to driver.
    
    Claimant: John Smith
    Contact: 217-555-0123
    
    Asset Type: Automobile
    Asset ID: VIN-2020XYZ789ABC
    Estimated Damage: $8,500.00
    
    Claim Type: Property Damage
    Initial Estimate: $8,200.00
    """
    
    print("Example 1: Simple Text Processing")
    print("="*70)
    
    processor = FNOLProcessor()
    result = processor.process_document(claim_text)
    
    print(f"Route: {result['recommendedRoute']}")
    print(f"Policy: {result['extractedFields'].get('policy_number')}")
    print(f"Damage: {result['extractedFields'].get('estimated_damage')}")
    print()


# =============================================================================
# EXAMPLE 2: Process Multiple Documents
# =============================================================================

def example_2_batch_processing():
    """Process multiple claims at once"""
    print("Example 2: Batch Processing")
    print("="*70)
    
    documents = [
        {
            'name': 'Claim_Auto_001.txt',
            'content': """
            Policy Number: POL-2024-001
            Policyholder Name: Alice Johnson
            Incident Date: 01/10/2024
            Incident Location: Downtown Parking Lot
            Incident Description: Vehicle scratch in parking lot
            Asset Type: Automobile
            Estimated Damage: $3,500
            Claim Type: Property Damage
            """
        },
        {
            'name': 'Claim_Injury_002.txt',
            'content': """
            Policy Number: POL-2024-002
            Policyholder Name: Bob Wilson
            Incident Date: 01/12/2024
            Incident Location: Factory Floor
            Incident Description: Work-related injury
            Asset Type: Worker
            Estimated Damage: $75,000
            Claim Type: Bodily Injury - Workers Compensation
            """
        }
    ]
    
    agent = ClaimsProcessingAgent()
    results = agent.process_claims(documents)
    
    # Display summary
    for result in results:
        print(f"  {result['documentName']}: {result['claimProcessing']['recommendedRoute']}")
    print()


# =============================================================================
# EXAMPLE 3: Fraud Detection
# =============================================================================

def example_3_fraud_detection():
    """Detect fraudulent claims"""
    print("Example 3: Fraud Detection")
    print("="*70)
    
    suspicious_claim = """
    Policy Number: POL-2024-999
    Policyholder Name: Charles Brown
    Incident Date: 01/20/2024
    Incident Location: Remote Storage Unit
    
    Description: Equipment disappearance. Circumstances appear staged and suspicious.
    Multiple inconsistencies in timeline. Fraud indicators detected.
    
    Asset Type: Industrial Equipment
    Estimated Damage: $150,000
    Initial Estimate: $45,000
    Claim Type: Equipment Loss
    """
    
    processor = FNOLProcessor()
    result = processor.process_document(suspicious_claim)
    
    print(f"Route: {result['recommendedRoute']}")
    print(f"Red Flags Detected: {len(result['investigationFlags'])}")
    for flag in result['investigationFlags']:
        print(f"  ⚠️  {flag}")
    print()


# =============================================================================
# EXAMPLE 4: Missing Data Handling
# =============================================================================

def example_4_missing_data_detection():
    """Handle claims with missing mandatory fields"""
    print("Example 4: Missing Data Detection")
    print("="*70)
    
    incomplete_claim = """
    Policy Number: POL-2024-INCOMPLETE
    
    Incident Date: 01/22/2024
    Description: Some incident occurred
    
    Estimated Damage: $12,000
    """
    
    processor = FNOLProcessor()
    result = processor.process_document(incomplete_claim)
    
    print(f"Route: {result['recommendedRoute']}")
    print(f"Missing Fields ({len(result['missingFields'])}):")
    for field in result['missingFields']:
        print(f"  ❌ {field}")
    print()


# =============================================================================
# EXAMPLE 5: Custom Field Extraction
# =============================================================================

def example_5_custom_extraction():
    """Extract custom patterns from documents"""
    print("Example 5: Custom Field Extraction")
    print("="*70)
    
    claim = """
    CLAIM REFERENCE: CL-2024-12345
    Insured Party: Jane Doe
    Coverage Period: 01/01/2024 - 12/31/2024
    Loss Occurred: January 25, 2024 at 3:45 PM
    Loss Address: 456 Oak Street, Chicago, IL 60601
    What Happened: Residential property damage due to water intrusion
    Reporting Party: Jane Doe
    Phone: (312) 555-0123; Email: jane@email.com
    Property Type: Single Family Residence
    Property ID: PIN-4567
    Repair Cost: $22,500
    Loss Category: Home Damage
    Supporting Documents: inspection_report.pdf, photos_1.jpg, photos_2.jpg
    Adjuster Estimate: $21,000
    """
    
    processor = FNOLProcessor()
    result = processor.process_document(claim)
    
    print(f"Extracted {len(result['extractedFields'])} fields:")
    for key, value in result['extractedFields'].items():
        if value:
            print(f"  • {key}: {value}")
    print()


# =============================================================================
# EXAMPLE 6: Routing Logic
# =============================================================================

def example_6_routing_decisions():
    """Demonstrate routing logic for different scenarios"""
    print("Example 6: Routing Decision Logic")
    print("="*70)
    
    scenarios = [
        ("Fast Track", """
            Policy Number: POL-FT-001
            Policyholder Name: Test User
            Incident Date: 01/01/2024
            Incident Location: Test Location
            Incident Description: Minor claim
            Asset Type: Vehicle
            Estimated Damage: $15,000
            Claim Type: Property Damage
        """),
        
        ("Standard Processing", """
            Policy Number: POL-ST-001
            Policyholder Name: Test User
            Incident Date: 01/01/2024
            Incident Location: Test Location
            Incident Description: Moderate claim
            Asset Type: Property
            Estimated Damage: $35,000
            Claim Type: Fire Damage
        """),
        
        ("Specialist Queue", """
            Policy Number: POL-SP-001
            Policyholder Name: Test User
            Incident Date: 01/01/2024
            Incident Location: Factory
            Incident Description: Work injury
            Asset Type: Employee
            Estimated Damage: $50,000
            Claim Type: Workers Compensation
        """)
    ]
    
    for scenario_name, claim_text in scenarios:
        processor = FNOLProcessor()
        result = processor.process_document(claim_text)
        print(f"{scenario_name}: {result['recommendedRoute']}")
        print(f"  Reason: {result['reasoning'][0]}")
        print()


# =============================================================================
# EXAMPLE 7: JSON Output Format
# =============================================================================

def example_7_json_output_format():
    """Show complete JSON output format"""
    print("Example 7: Complete JSON Output Format")
    print("="*70)
    
    claim = """
    Policy Number: POL-2024-JSON-DEMO
    Policyholder Name: Demo User
    Effective Dates: 01/01/2024 - 12/31/2024
    Incident Date: 01/15/2024
    Time: 10:30 AM
    Location: 789 Test Ave, Sample City, ST 12345
    Description: Vehicle damage incident
    Claimant: Demo User
    Contact: 555-0123
    Asset Type: Vehicle
    Asset ID: VIN-TEST123
    Estimated Damage: $9,500
    Claim Type: Auto Damage
    Initial Estimate: $9,200
    """
    
    processor = FNOLProcessor()
    result = processor.process_document(claim)
    
    print(json.dumps(result, indent=2))
    print()


# =============================================================================
# EXAMPLE 8: Confidence and Metrics
# =============================================================================

def example_8_extraction_metrics():
    """Show extraction quality metrics"""
    print("Example 8: Extraction Quality Metrics")
    print("="*70)
    
    claim = """
    Policy Number: POL-METRICS-001
    Policyholder Name: Metric Test User
    Effective Dates: 01/01/2024 - 12/31/2024
    Incident Date: 01/20/2024
    Time: 14:00
    Location: Metrics Test Location
    Description: Test incident description
    Claimant: Metric Test
    Contact: (555) 123-4567
    Asset Type: Test Asset
    Asset ID: ASSET-001
    Estimated Damage: $18,500
    Claim Type: Test Claim Type
    Initial Estimate: $18,000
    Attachments: document1.pdf, photo.jpg
    """
    
    processor = FNOLProcessor()
    result = processor.process_document(claim)
    
    total_fields = len([f for f in processor.MANDATORY_FIELDS if f])
    extracted = len(result['extractedFields'])
    extraction_rate = (extracted / total_fields) * 100 if total_fields > 0 else 0
    
    print(f"Mandatory Fields: {total_fields}")
    print(f"Extracted Fields: {extracted}")
    print(f"Extraction Rate: {extraction_rate:.1f}%")
    print(f"Missing Fields: {len(result['missingFields'])}")
    print(f"Red Flags: {len(result.get('investigationFlags', []))}")
    print(f"Route: {result['recommendedRoute']}")
    print()


# =============================================================================
# EXAMPLE 9: Integration with External Systems
# =============================================================================

def example_9_api_integration():
    """Example of integrating with external systems"""
    print("Example 9: API Integration Example")
    print("="*70)
    
    claim = """
    Policy Number: POL-API-001
    Policyholder Name: API Test
    Incident Date: 01/25/2024
    Incident Location: API Test Location
    Incident Description: API integration test
    Asset Type: Digital
    Estimated Damage: $5,000
    Claim Type: System Error
    """
    
    processor = FNOLProcessor()
    result = processor.process_document(claim)
    
    # Simulate API response
    api_response = {
        "status": "success",
        "claimData": result,
        "nextAction": f"Route to {result['recommendedRoute']}",
        "timestamp": result.get('processedAt')
    }
    
    print(json.dumps(api_response, indent=2))
    print()


# =============================================================================
# EXAMPLE 10: Full Agent Pipeline
# =============================================================================

def example_10_full_pipeline():
    """Complete end-to-end pipeline"""
    print("Example 10: Full Agent Pipeline")
    print("="*70)
    
    claims = [
        {
            'name': 'fast_track.txt',
            'content': """
            Policy Number: POL-FT-123
            Policyholder Name: Speed Claimant
            Incident Date: 02/01/2024
            Incident Location: Parking Lot
            Incident Description: Minor scratch
            Asset Type: Car
            Estimated Damage: $5,000
            Claim Type: Property Damage
            """
        },
        {
            'name': 'needs_review.txt',
            'content': """
            Policy Number: POL-NR-456
            Incident Date: 02/02/2024
            Description: Incomplete information provided
            Asset Type: Unknown
            Estimated Damage: $8,000
            """
        }
    ]
    
    agent = ClaimsProcessingAgent()
    results = agent.process_claims(claims)
    agent.export_results('/tmp/pipeline_results.json')
    
    print(f"Pipeline completed successfully!")
    print(f"Processed: {len(results)} claims")
    print(f"Results saved to: /tmp/pipeline_results.json")
    print()


# =============================================================================
# RUN ALL EXAMPLES
# =============================================================================

def run_all_examples():
    """Run all examples in sequence"""
    print("\n" + "="*70)
    print("CLAIMS PROCESSING AGENT - USAGE EXAMPLES")
    print("="*70 + "\n")
    
    examples = [
        example_1_simple_text_processing,
        example_2_batch_processing,
        example_3_fraud_detection,
        example_4_missing_data_detection,
        example_5_custom_extraction,
        example_6_routing_decisions,
        example_7_json_output_format,
        example_8_extraction_metrics,
        example_9_api_integration,
        example_10_full_pipeline
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"Error in {example_func.__name__}: {e}\n")


if __name__ == "__main__":
    run_all_examples()
