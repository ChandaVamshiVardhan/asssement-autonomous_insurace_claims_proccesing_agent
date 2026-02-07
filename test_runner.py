#!/usr/bin/env python3
"""
Quick Test Runner for Claims Processing Agent
Run this to quickly test the system with sample data

Author: Vamshi Vardhan
Date: February 6, 2026
"""

import json
import sys
import io
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from claims_processor import ClaimsProcessingAgent

# Sample FNOL documents for testing
sample_documents = [
    {
        "name": "Claim_001_Auto_Damage.txt",
        "content": """
        FIRST NOTICE OF LOSS (FNOL)
        
        Policy Number: POL-2024-001234
        Policyholder Name: John Smith
        Effective Dates: 01/01/2024 - 12/31/2024
        
        INCIDENT INFORMATION
        Incident Date: 01/15/2024
        Time: 14:30 PM
        Location: Intersection of Main St and Oak Ave, Springfield, IL 60601
        
        Description: Vehicle collision with another automobile. Minor injuries to driver. 
        Vehicle sustained significant front-end damage including broken headlight, 
        damaged bumper, and hood dent.
        
        INVOLVED PARTIES
        Claimant: John Smith
        Third Party: Jane Doe
        Contact Details: 217-555-0123, john.smith@email.com
        
        ASSET DETAILS
        Asset Type: Automobile
        Asset ID: VIN-2020XYZ789ABC
        Estimated Damage: $8,500.00
        
        CLAIM INFORMATION
        Claim Type: Property Damage
        Initial Estimate: $8,200.00
        Attachments: Police_Report.pdf, Photos.jpg
        """
    },
    {
        "name": "Claim_002_Injury.txt",
        "content": """
        FIRST NOTICE OF LOSS
        
        Policy Number: POL-2024-005678
        Effective Dates: 06/01/2024 - 05/31/2025
        
        INCIDENT INFORMATION
        Incident Date: 01/20/2024
        Location: Office Building, 100 Commerce Dr, Chicago, IL
        Description: Employee sustained injury while performing job duties. 
        Incident occurred in warehouse during loading operations.
        
        Asset Type: Worker Compensation Claim
        Claim Type: Bodily Injury - Workers Compensation
        Estimated Damage: $45,000.00
        
        [MISSING: Policyholder Name, Incident Time, Claimant Details, Contact Information]
        """
    },
    {
        "name": "Claim_003_Suspicious.txt",
        "content": """
        FNOL REPORT
        
        Policy Number: POL-2024-009999
        Policyholder Name: Robert Johnson
        Incident Date: 01/22/2024
        Location: Warehouse, Industrial Park
        
        Description: Equipment loss reported. Circumstances appear suspicious and staged. 
        Multiple inconsistencies in timeline. Fraud indicators present. 
        Equipment was worth $120,000 but claim shows inconsistent valuations.
        
        Asset Type: Industrial Equipment
        Estimated Damage: $120,000.00
        Initial Estimate: $45,000.00
        Claim Type: Equipment Loss
        
        [MISSING: Policyholder contact details, detailed incident description]
        """
    }
]


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def print_result_summary(result):
    """Print summary of processing result"""
    claim = result['claimProcessing']
    
    print(f"DOCUMENT: {result['documentName']}")
    print(f"{'─'*70}")
    print(f"Route:      {claim['recommendedRoute']}")
    print(f"Extracted:  {len(claim['extractedFields'])} fields")
    print(f"Missing:    {len(claim['missingFields'])} fields")
    print(f"Flags:      {len(claim['investigationFlags'])} red flags")
    print()
    
    if claim['extractedFields']:
        print("Key Extracted Data:")
        for key in ['policy_number', 'policyholder_name', 'incident_date', 
                    'incident_location', 'claim_type', 'estimated_damage']:
            value = claim['extractedFields'].get(key)
            if value:
                print(f"  • {key}: {value}")
    
    if claim['missingFields']:
        print(f"\nMissing Fields: {', '.join(claim['missingFields'])}")
    
    if claim['investigationFlags']:
        print("\nInvestigation Flags:")
        for flag in claim['investigationFlags']:
            print(f"  [WARNING] {flag}")
    
    print(f"\nReasoning: {'; '.join(claim['reasoning'])}")
    print(f"\n{'─'*70}\n")


def main():
    """Main test execution"""
    print_header("AUTONOMOUS INSURANCE CLAIMS PROCESSING AGENT - TEST RUN")
    
    try:
        # Initialize agent
        print("Initializing Claims Processing Agent...")
        agent = ClaimsProcessingAgent()
        print("[OK] Agent initialized successfully\n")
        
        # Process sample documents
        print(f"Processing {len(sample_documents)} sample FNOL documents...\n")
        results = agent.process_claims(sample_documents)
        
        # Print detailed results
        print_header("DETAILED RESULTS")
        for result in results:
            print_result_summary(result)
        
        # Summary statistics
        print_header("SUMMARY STATISTICS")
        
        routes = {}
        total_missing = 0
        total_flags = 0
        
        for result in agent.results:
            claim = result['claimProcessing']
            route = claim['recommendedRoute']
            routes[route] = routes.get(route, 0) + 1
            total_missing += len(claim['missingFields'])
            total_flags += len(claim['investigationFlags'])
        
        print(f"Total Claims Processed: {len(results)}")
        print(f"\nRouting Breakdown:")
        for route, count in sorted(routes.items()):
            pct = (count / len(results)) * 100
            print(f"  • {route}: {count} ({pct:.1f}%)")
        
        print(f"\nData Quality Metrics:")
        print(f"  • Total Missing Fields: {total_missing}")
        print(f"  • Total Red Flags: {total_flags}")
        print(f"  • Average Fields per Claim: {sum(len(r['claimProcessing']['extractedFields']) for r in agent.results) / len(results):.1f}")
        
        # Export results
        print_header("EXPORTING RESULTS")
        output_file = agent.export_results()
        print(f"[OK] Results saved to: {output_file}")
        
        # Display JSON sample
        print("\n[INFO] Sample JSON Output (First Claim):")
        print(json.dumps(agent.results[0], indent=2)[:500] + "...\n")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
