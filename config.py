"""
Configuration File for Claims Processing Agent
Customize extraction patterns, business rules, and thresholds here

Author: Vamshi Vardhan
Date: February 6, 2026
"""

import json

# ============================================================================
# CONFIGURABLE PARAMETERS
# ============================================================================

# Damage threshold for fast-track eligibility (in dollars)
FASTTRACK_DAMAGE_THRESHOLD = 25000

# Discrepancy percentage that triggers inconsistency flag
DAMAGE_DISCREPANCY_THRESHOLD = 0.5  # 50%

# Mandatory fields that must be extracted
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

# Red flag keywords for fraud detection
RED_FLAG_KEYWORDS = [
    'fraud',
    'staged',
    'inconsistent',
    'suspicious',
    'questionable',
    'fabricated',
    'false claim',
    'staged incident',
    'insurance fraud',
    'claim fabrication'
]

# Claim types requiring specialist handling
SPECIALIST_CLAIM_TYPES = [
    'injury',
    'bodily injury',
    'personal injury',
    'workers compensation',
    'workers\' compensation',
    'workers comp',
    'liability',
    'workers injury'
]

# ============================================================================
# REGEX PATTERNS FOR FIELD EXTRACTION
# ============================================================================

EXTRACTION_PATTERNS = {
    'policy_number': [
        r'(?:policy\s*(?:number|#|no\.?|num)?[\s:]*)([\d\-A-Z]+)',
        r'(?:policyno|pol\s*no)[\s:]*([A-Z0-9\-]+)',
        r'(?:policy|pol)[\s:]*([PNPO][OL0-9]{8,})'
    ],
    
    'policyholder_name': [
        r'(?:policyholder|insured|named insured|policy holder)[\s:]*([A-Za-z\s,\.]+?)(?:\n|$|policy|effective)',
        r'(?:name of insured)[\s:]*([A-Za-z\s,\.]+?)(?:\n|policy)',
        r'(?:insured|policyholder)[\s:]*([A-Za-z\s,\.]+?)(?:address|\n|$)'
    ],
    
    'effective_dates': [
        r'(?:effective|coverage|policy period)[\s:]*([0-9/\-\s]+?(?:to|through|–|-)[0-9/\-\s]+)',
        r'(?:dates?|period|from)[\s:]*([0-9/\-]+)\s*(?:to|through)\s*([0-9/\-]+)',
        r'(\d{1,2}/\d{1,2}/\d{4})\s*[-–]\s*(\d{1,2}/\d{1,2}/\d{4})'
    ],
    
    'incident_date': [
        r'(?:incident|loss|accident)\s+(?:date|occurred on|on)[\s:]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
        r'(?:date of (?:incident|loss|accident))[\s:]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
        r'(?:when|when did|date)[\s:]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})'
    ],
    
    'incident_time': [
        r'(?:time|at|time of incident|time of loss)[\s:]*(\d{1,2}:\d{2}\s*(?:[AP]M)?)',
        r'(?:incident occurred at)[\s:]*(\d{1,2}:\d{2})',
        r'(\d{1,2}:\d{2}\s*(?:[AP]M)?)\s*(?:AM|PM|a\.m\.|p\.m\.)'
    ],
    
    'incident_location': [
        r'(?:location|place|where|at|occurred at)[\s:]*([^\n]+?)(?:\n|$)',
        r'(?:incident location|loss location)[\s:]*([^\n]+)',
        r'(?:address of incident)[\s:]*([^\n,]+(?:,\s*[^\n]+)?)'
    ],
    
    'incident_description': [
        r'(?:description|details|what happened|account|narrative)[\s:]*([^\n]+(?:\n[^\n]+)?(?:\n[^\n]+)?)',
        r'(?:incident description)[\s:]*([^\n]+(?:\n.{0,100})?)',
        r'(?:describe)[\s:]*([^\n]+)'
    ],
    
    'claimant': [
        r'(?:claimant|claim filed by|filed by)[\s:]*([A-Za-z\s,\.]+?)(?:\n|$|address)',
        r'(?:claimant name)[\s:]*([A-Za-z\s,\.]+?)(?:\n|$)',
        r'(?:person filing claim)[\s:]*([A-Za-z\s,\.]+)'
    ],
    
    'contact_details': [
        r'(?:phone|cell|telephone|contact number)[\s:]*([0-9\-\+\(\)\s]+)',
        r'(?:email)[\s:]*([A-Za-z0-9\.\_\-\+]+@[A-Za-z0-9\.]+)',
        r'(?:contact)[\s:]*([^\n]+)'
    ],
    
    'asset_type': [
        r'(?:asset|vehicle|property|equipment)\s+(?:type|class|category)[\s:]*([^\n]+)',
        r'(?:type of (?:asset|vehicle|property))[\s:]*([^\n]+)',
        r'(?:asset class)[\s:]*([^\n]+)'
    ],
    
    'asset_id': [
        r'(?:(?:vehicle|asset|claim|vin|serial)\s*(?:id|number|#|no\.?)|vin|claim\s*#)[\s:]*([^\n]+)',
        r'(?:identification|asset id)[\s:]*([A-Z0-9\-]+)',
        r'(?:serial number)[\s:]*([^\n]+)'
    ],
    
    'estimated_damage': [
        r'(?:estimated|damage|loss|amount|repair cost)[\s:]*\$?\s*([\d,]+(?:\.\d{2})?)',
        r'(?:amount of loss)[\s:]*\$?\s*([\d,]+(?:\.\d{2})?)',
        r'\$\s*([\d,]+(?:\.\d{2})?)'
    ],
    
    'claim_type': [
        r'(?:claim\s+type|type of claim|classification)[\s:]*([^\n]+)',
        r'(?:claim class)[\s:]*([^\n]+)',
        r'(?:claim category)[\s:]*([^\n]+)'
    ],
    
    'initial_estimate': [
        r'(?:initial\s*estimate|preliminary\s*estimate|first estimate)[\s:]*\$?\s*([\d,]+(?:\.\d{2})?)',
        r'(?:preliminary assessment)[\s:]*\$?\s*([\d,]+(?:\.\d{2})?)',
    ]
}

# ============================================================================
# ROUTING CONFIGURATION
# ============================================================================

ROUTING_CONFIG = {
    'fast_track': {
        'threshold': FASTTRACK_DAMAGE_THRESHOLD,
        'description': 'Claims with damage below threshold and complete data'
    },
    'standard_processing': {
        'description': 'Normal claims without special circumstances'
    },
    'specialist_queue': {
        'description': 'Claims requiring specialized handling (injury, liability, etc.)'
    },
    'investigation_queue': {
        'description': 'Claims with fraud indicators requiring investigation'
    },
    'manual_review': {
        'description': 'Claims with missing mandatory fields requiring manual input'
    }
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'claims_processing.log'
}

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

OUTPUT_CONFIG = {
    'format': 'json',  # json, csv, html
    'include_raw_text': False,  # Include original document text
    'include_confidence_scores': True,  # Include extraction confidence
    'pretty_print': True,  # Pretty format JSON
    'indent': 2
}

# ============================================================================
# PERFORMANCE TUNING
# ============================================================================

PERFORMANCE_CONFIG = {
    'parallel_processing': True,
    'num_workers': 4,
    'cache_patterns': True,
    'timeout_per_document': 30  # seconds
}

# ============================================================================
# VALIDATION RULES
# ============================================================================

VALIDATION_RULES = {
    'policy_number': {
        'required': True,
        'pattern': r'^[A-Z0-9\-]{5,}$',
        'min_length': 5
    },
    'estimated_damage': {
        'required': True,
        'min_value': 0,
        'max_value': 10000000  # 10M
    },
    'incident_date': {
        'required': True,
        'format': 'date'
    }
}

# ============================================================================
# FUNCTIONS FOR LOADING CONFIGURATION
# ============================================================================

def get_config():
    """Get current configuration as dictionary"""
    return {
        'fasttrack_threshold': FASTTRACK_DAMAGE_THRESHOLD,
        'mandatory_fields': MANDATORY_FIELDS,
        'red_flag_keywords': RED_FLAG_KEYWORDS,
        'specialist_claim_types': SPECIALIST_CLAIM_TYPES,
        'routing': ROUTING_CONFIG,
        'logging': LOGGING_CONFIG,
        'output': OUTPUT_CONFIG
    }


def save_config_to_json(filepath):
    """Save configuration to JSON file"""
    config = get_config()
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Configuration saved to {filepath}")


def load_config_from_json(filepath):
    """Load configuration from JSON file"""
    with open(filepath, 'r') as f:
        config = json.load(f)
    return config


def print_config():
    """Print current configuration"""
    config = get_config()
    print("\n" + "="*70)
    print("CURRENT CLAIMS PROCESSING CONFIGURATION")
    print("="*70)
    print(json.dumps(config, indent=2))
    print("="*70 + "\n")


if __name__ == "__main__":
    print_config()
