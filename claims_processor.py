"""
Autonomous Insurance Claims Processing Agent
Processes FNOL (First Notice of Loss) documents and routes them appropriately

Author: Vamshi Vardhan
Date: February 6, 2026
"""

import json
import re
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime


@dataclass
class ExtractedFields:
    """Data class for extracted claim fields"""
    policy_number: Optional[str] = None
    policyholder_name: Optional[str] = None
    effective_dates: Optional[str] = None
    incident_date: Optional[str] = None
    incident_time: Optional[str] = None
    incident_location: Optional[str] = None
    incident_description: Optional[str] = None
    claimant: Optional[str] = None
    third_parties: List[str] = field(default_factory=list)
    contact_details: Optional[str] = None
    asset_type: Optional[str] = None
    asset_id: Optional[str] = None
    estimated_damage: Optional[float] = None
    claim_type: Optional[str] = None
    attachments: List[str] = field(default_factory=list)
    initial_estimate: Optional[float] = None



class FNOLProcessor:
    """Main processor for FNOL documents"""
    
    # Required fields for claim processing
    MANDATORY_FIELDS = [
        'policy_number',
        'policyholder_name',
        'incident_date',
        'incident_location',
        'incident_description',
        'claim_type',
        'asset_type',
        'estimated_damage'
    ]
    
    # Red flag keywords indicating fraud or staging
    RED_FLAG_KEYWORDS = [
        'fraud', 'staged', 'inconsistent', 'suspicious', 
        'questionable', 'fabricated', 'false claim'
    ]
    
    # Claim types that require specialist handling
    SPECIALIST_CLAIM_TYPES = [
        'injury', 'bodily injury', 'personal injury', 
        'workers compensation', 'liability'
    ]
    
    def __init__(self):
        self.extracted_fields = ExtractedFields()
        self.missing_fields = []
        self.recommended_route = None
        self.reasoning = []
        self.investigation_flags = []
    
    def extract_fields_from_text(self, text: str) -> ExtractedFields:
        """Extract fields from raw text/PDF content"""
        self.extracted_fields = ExtractedFields()
        
        # Policy Number extraction
        self.extracted_fields.policy_number = self._extract_pattern(
            text, r'(?:policy\s*(?:number|#|no\.?|num)?[\s:]*|policyno[\s:]*)([\d\-A-Z]+)', 'Policy Number'
        )
        
        # Policyholder Name
        self.extracted_fields.policyholder_name = self._extract_pattern(
            text, r'(?:policyholder|insured|named insured|policy holder)[\s:]*([A-Za-z\s,]+?)(?:\n|$|(?:policy|effective))', 'Policyholder Name'
        )
        
        # Effective Dates
        self.extracted_fields.effective_dates = self._extract_pattern(
            text, r'(?:effective|coverage|policy period)[\s:]*([0-9/\-\s]+(?:to|through|–|-)[0-9/\-\s]+)', 'Effective Dates'
        )
        
        # Incident Date
        self.extracted_fields.incident_date = self._extract_pattern(
            text, r'(?:incident|loss|accident)\s+(?:date|on)[\s:]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})', 'Incident Date'
        )
        
        # Incident Time
        self.extracted_fields.incident_time = self._extract_pattern(
            text, r'(?:time|at|time of incident)[\s:]*(\d{1,2}:\d{2}(?:\s?[AP]M)?)', 'Incident Time'
        )
        
        # Incident Location
        self.extracted_fields.incident_location = self._extract_pattern(
            text, r'(?:location|place|where)[\s:]*([^\n]+?)(?:\n|$)', 'Incident Location'
        )
        
        # Incident Description
        self.extracted_fields.incident_description = self._extract_pattern(
            text, r'(?:description|details|what happened)[\s:]*([^\n]+(?:\n[^\n]+)?)', 'Incident Description'
        )
        
        # Claimant
        self.extracted_fields.claimant = self._extract_pattern(
            text, r'(?:claimant|claim filed by)[\s:]*([A-Za-z\s,]+?)(?:\n|$)', 'Claimant'
        )
        
        # Contact Details
        self.extracted_fields.contact_details = self._extract_pattern(
            text, r'(?:phone|email|contact)[\s:]*([^\n]+)', 'Contact Details'
        )
        
        # Asset Type
        self.extracted_fields.asset_type = self._extract_pattern(
            text, r'(?:asset|vehicle|property)\s+(?:type|class)[\s:]*([^\n]+)', 'Asset Type'
        )
        
        # Asset ID
        self.extracted_fields.asset_id = self._extract_pattern(
            text, r'(?:(?:vehicle|asset|claim|vin|serial)\s*(?:id|number|#)|vin|claim #)[\s:]*([^\n]+)', 'Asset ID'
        )
        
        # Estimated Damage
        damage_str = self._extract_pattern(
            text, r'(?:estimated|damage|loss|amount)[\s:]*[\$]*([\d,]+(?:\.\d{2})?)', 'Estimated Damage'
        )
        if damage_str:
            try:
                self.extracted_fields.estimated_damage = float(damage_str.replace(',', ''))
            except ValueError:
                pass
        
        # Claim Type
        self.extracted_fields.claim_type = self._extract_pattern(
            text, r'(?:claim\s+type|type of claim)[\s:]*([^\n]+)', 'Claim Type'
        )
        
        # Attachments
        attachments = re.findall(
            r'(?:attachment|attached|document|file)[\s:]*([^\n]+\.(?:pdf|jpg|png|doc|docx))', text, re.IGNORECASE
        )
        self.extracted_fields.attachments = attachments if attachments else []
        
        # Initial Estimate
        estimate_str = self._extract_pattern(
            text, r'(?:initial estimate|preliminary estimate)[\s:]*[\$]*([\d,]+(?:\.\d{2})?)', 'Initial Estimate'
        )
        if estimate_str:
            try:
                self.extracted_fields.initial_estimate = float(estimate_str.replace(',', ''))
            except ValueError:
                pass
        
        return self.extracted_fields
    
    def _extract_pattern(self, text: str, pattern: str, field_name: str) -> Optional[str]:
        """Generic pattern extraction helper"""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
        
    
    def identify_missing_fields(self) -> List[str]:
        """Identify mandatory fields that are missing"""
        self.missing_fields = []
        
        for field in self.MANDATORY_FIELDS:
            value = getattr(self.extracted_fields, field)
            if not value:
                self.missing_fields.append(field)
        
        return self.missing_fields
    
    def check_red_flags(self) -> List[str]:
        """Check for fraud indicators or red flags"""
        self.investigation_flags = []
        
        description = (self.extracted_fields.incident_description or "").lower()
        
        for keyword in self.RED_FLAG_KEYWORDS:
            if keyword in description:
                self.investigation_flags.append(
                    f"Red flag detected: '{keyword}' found in incident description"
                )
        
        # Check for inconsistencies
        if self.extracted_fields.estimated_damage and self.extracted_fields.initial_estimate:
            if abs(self.extracted_fields.estimated_damage - self.extracted_fields.initial_estimate) > self.extracted_fields.estimated_damage * 0.5:
                self.investigation_flags.append(
                    "Inconsistency detected: Large discrepancy between estimated and initial damage"
                )
        
        return self.investigation_flags
    
    def route_claim(self) -> Tuple[str, List[str]]:
        """Determine routing based on claim characteristics"""
        reasoning = []
        
        # Check for missing mandatory fields
        if self.missing_fields:
            return "MANUAL_REVIEW", [f"Missing mandatory fields: {', '.join(self.missing_fields)}"]
        
        # Check for red flags/investigation indicators
        if self.investigation_flags:
            return "INVESTIGATION_QUEUE", self.investigation_flags
        
        # Check if specialist claim type
        claim_type = (self.extracted_fields.claim_type or "").lower()
        if any(spec in claim_type for spec in self.SPECIALIST_CLAIM_TYPES):
            reasoning.append(f"Claim type '{self.extracted_fields.claim_type}' requires specialist handling")
            return "SPECIALIST_QUEUE", reasoning
        
        # Check damage amount for fast-track eligibility
        if self.extracted_fields.estimated_damage:
            if self.extracted_fields.estimated_damage < 25000:
                reasoning.append(f"Damage amount ${self.extracted_fields.estimated_damage:,.2f} is below $25,000 threshold")
                return "FAST_TRACK", reasoning
            else:
                reasoning.append(f"Damage amount ${self.extracted_fields.estimated_damage:,.2f} exceeds $25,000 threshold")
                return "STANDARD_PROCESSING", reasoning
        
        return "STANDARD_PROCESSING", ["No specific routing criteria met"]
    
    def process_document(self, document_text: str) -> Dict[str, Any]:
        """Main processing pipeline"""
        # Extract fields
        self.extract_fields_from_text(document_text)
        
        # Identify missing fields
        self.identify_missing_fields()
        
        # Check for red flags
        self.check_red_flags()
        
        # Route claim
        route, reasoning = self.route_claim()
        self.recommended_route = route
        self.reasoning = reasoning
        
        # Build output
        extracted_dict = {k: v for k, v in asdict(self.extracted_fields).items() if v}
        
        output = {
            "extractedFields": extracted_dict,
            "missingFields": self.missing_fields,
            "investigationFlags": self.investigation_flags,
            "recommendedRoute": self.recommended_route,
            "reasoning": self.reasoning,
            "processedAt": datetime.now().isoformat()
        }
        
        return output


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


class ClaimsProcessingAgent:
    """Main agent orchestrating the claims processing"""
    
    def __init__(self):
        self.processor = FNOLProcessor()
        self.results = []
    
    def process_claims(self, documents: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Process multiple claim documents"""
        results = []
        
        for i, doc in enumerate(documents, 1):
            print(f"\n{'='*60}")
            print(f"Processing Document {i}: {doc.get('name', 'Unknown')}")
            print('='*60)
            
            result = self.processor.process_document(doc['content'])
            results.append({
                "documentName": doc.get('name', f'Document_{i}'),
                "claimProcessing": result
            })
            
            # Print summary
            print(f"Status: {result['recommendedRoute']}")
            print(f"Extracted Policy: {result['extractedFields'].get('policy_number', 'N/A')}")
            print(f"Missing Fields: {len(result['missingFields'])}")
            if result['investigationFlags']:
                print(f"Red Flags: {len(result['investigationFlags'])}")
            print(f"Reasoning: {'; '.join(result['reasoning'])}")
        
        self.results = results
        return results
    
    def export_results(self, filename: str = "claims_processing_results.json"):
        """Export results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n[OK] Results exported to {filename}")
        return filename


# Example usage
if __name__ == "__main__":
    # Initialize agent and process claims
    agent = ClaimsProcessingAgent()
    results = agent.process_claims(sample_documents)
    
    # Export results
    agent.export_results("/home/arjun/Downloads/m1/claims_processing_results.json")
