#!/usr/bin/env python3
"""
Main Entry Point for Claims Processing Agent
Run: python main.py [options]

Author: Vamshi Vardhan
Date: February 6, 2026
"""

import sys
import argparse
import json
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from claims_processor import ClaimsProcessingAgent, FNOLProcessor
from pdf_processor import PDFClaimsProcessor
from config import print_config, get_config


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Autonomous Insurance Claims Processing Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --test                      # Run with sample data
  python main.py --folder /path/to/claims    # Process folder of documents
  python main.py --file claim.pdf            # Process single document
  python main.py --config                    # Show configuration
        """
    )
    
    parser.add_argument(
        '--test', action='store_true',
        help='Run with sample test data'
    )
    parser.add_argument(
        '--folder', type=str, metavar='PATH',
        help='Process all PDF/TXT files in folder'
    )
    parser.add_argument(
        '--file', type=str, metavar='PATH',
        help='Process single claim document'
    )
    parser.add_argument(
        '--output', '-o', type=str, metavar='FILE',
        help='Output JSON file (default: claims_processing_results.json)'
    )
    parser.add_argument(
        '--config', action='store_true',
        help='Display current configuration'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Show configuration if requested
    if args.config:
        print_config()
        return 0
    
    # Initialize agent
    agent = ClaimsProcessingAgent()
    
    # Determine operation mode
    if args.test:
        print("\n" + "="*70)
        print("RUNNING WITH SAMPLE TEST DATA")
        print("="*70)
        
        from claims_processor import sample_documents
        results = agent.process_claims(sample_documents)
        
    elif args.file:
        print(f"\nProcessing file: {args.file}")
        text = PDFClaimsProcessor.load_document(args.file)
        results = agent.process_claims([{
            'name': Path(args.file).name,
            'content': text
        }])
        
    elif args.folder:
        print(f"\nProcessing folder: {args.folder}")
        folder_path = Path(args.folder)
        documents = []
        
        for file_path in folder_path.glob('*'):
            if file_path.suffix.lower() in ['.pdf', '.txt']:
                try:
                    text = PDFClaimsProcessor.load_document(str(file_path))
                    documents.append({
                        'name': file_path.name,
                        'content': text
                    })
                except Exception as e:
                    print(f"  ❌ Error reading {file_path.name}: {e}")
        
        if documents:
            results = agent.process_claims(documents)
        else:
            print("No PDF or TXT files found in folder")
            return 1
            
    else:
        print("\nNo operation specified. Use --help for options")
        parser.print_help()
        return 1
    
    # Export results
    output_file = args.output or "claims_processing_results.json"
    output_path = Path(output_file)
    
    with open(output_path, 'w') as f:
        json.dump(agent.results, f, indent=2)
    
    print(f"\n[OK] Results saved to: {output_path}")
    print(f"[OK] Processed {len(agent.results)} claims")
    
    # Summary statistics
    if args.verbose:
        print("\n" + "="*70)
        print("SUMMARY STATISTICS")
        print("="*70)
        
        routes = {}
        total_missing = 0
        total_flags = 0
        
        for result in agent.results:
            claim = result['claimProcessing']
            route = claim['recommendedRoute']
            routes[route] = routes.get(route, 0) + 1
            total_missing += len(claim['missingFields'])
            total_flags += len(claim['investigationFlags'])
        
        print(f"\nRouting Summary:")
        for route, count in sorted(routes.items()):
            pct = (count / len(agent.results)) * 100
            print(f"  • {route}: {count} ({pct:.1f}%)")
        
        print(f"\nData Quality:")
        print(f"  • Total Missing Fields: {total_missing}")
        print(f"  • Total Red Flags: {total_flags}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
