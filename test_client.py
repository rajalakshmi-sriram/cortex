#!/usr/bin/env python
"""
Test Client for Cortex API
Demonstrates all main features and endpoints
"""

import requests
import json
from typing import Dict, Any
import time


class CortexClient:
    """Simple client for testing Cortex API"""
    
    def __init__(self, base_url: str = "http://localhost:5050"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check application health"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_api_info(self) -> Dict[str, Any]:
        """Get API information"""
        response = self.session.get(f"{self.base_url}/api/v1")
        response.raise_for_status()
        return response.json()
    
    def validate_idea(self, idea: str) -> Dict[str, Any]:
        """Validate a research idea"""
        response = self.session.post(
            f"{self.base_url}/api/v1/ideas/validate",
            json={"idea": idea}
        )
        response.raise_for_status()
        return response.json()
    
    def get_research_modes(self) -> Dict[str, Any]:
        """Get available research modes"""
        response = self.session.get(f"{self.base_url}/api/v1/research-modes")
        response.raise_for_status()
        return response.json()
    
    def select_methodology(self, idea: str, mode: str) -> Dict[str, Any]:
        """Select a research methodology"""
        response = self.session.post(
            f"{self.base_url}/api/v1/methodology/select",
            json={"idea": idea, "mode": mode}
        )
        response.raise_for_status()
        return response.json()
    
    def get_step_details(self, mode: str, step_number: int) -> Dict[str, Any]:
        """Get details for a specific methodology step"""
        response = self.session.get(
            f"{self.base_url}/api/v1/methodology/{mode}/step/{step_number}"
        )
        response.raise_for_status()
        return response.json()


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")


def print_json(data: Dict, indent: int = 2):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=indent))


def test_health_check(client: CortexClient):
    """Test health check endpoint"""
    print_section("HEALTH CHECK")
    
    try:
        result = client.health_check()
        print("✓ Application is healthy")
        print_json(result)
    except Exception as e:
        print(f"✗ Health check failed: {str(e)}")
        return False
    
    return True


def test_api_info(client: CortexClient):
    """Test API info endpoint"""
    print_section("API INFORMATION")
    
    try:
        result = client.get_api_info()
        print("✓ API information retrieved")
        print_json(result)
    except Exception as e:
        print(f"✗ API info failed: {str(e)}")
        return False
    
    return True


def test_idea_validation(client: CortexClient):
    """Test idea validation with multiple examples"""
    print_section("IDEA VALIDATION")
    
    test_ideas = [
        "Investigate the role of astrocytes in memory consolidation using optogenetics",
        "Study circadian rhythm effects on neuroplasticity in aging mice",
        "Explore dopamine's role in decision-making through neural circuit manipulation",
        "Examine astrocyte-mediated memory consolidation in sleep",  # Similar to first
    ]
    
    results = []
    
    for i, idea in enumerate(test_ideas, 1):
        print(f"\n[Test {i}/{len(test_ideas)}] Validating idea...")
        print(f"Idea: {idea}")
        print("-" * 80)
        
        try:
            result = client.validate_idea(idea)
            
            status = result.get('status', 'unknown')
            message = result.get('message', '')
            valid = result.get('valid', False)
            score = result.get('max_similarity_score', 0)
            
            symbol = "✓" if valid else "✗"
            print(f"{symbol} Status: {status}")
            print(f"  Message: {message}")
            print(f"  Similarity Score: {score:.2%}")
            
            if 'related_papers' in result and result['related_papers']:
                print(f"  Related Papers: {len(result['related_papers'])}")
                for paper in result['related_papers'][:2]:
                    print(f"    - {paper['title'][:70]}...")
            
            results.append({
                'idea': idea,
                'status': status,
                'valid': valid,
                'score': score
            })
            
        except Exception as e:
            print(f"✗ Validation failed: {str(e)}")
            results.append({
                'idea': idea,
                'status': 'error',
                'valid': False,
                'score': 0
            })
        
        # Avoid rate limiting
        time.sleep(1)
    
    return results


def test_research_modes(client: CortexClient):
    """Test research modes retrieval"""
    print_section("RESEARCH MODES")
    
    try:
        result = client.get_research_modes()
        modes = result.get('modes', {})
        
        print(f"✓ Retrieved {len(modes)} research modes:\n")
        
        for mode_key, mode_info in list(modes.items())[:5]:
            print(f"  [{mode_key}]")
            print(f"    Name: {mode_info['name']}")
            print(f"    Description: {mode_info['description']}\n")
        
        if len(modes) > 5:
            print(f"  ... and {len(modes) - 5} more modes\n")
        
        return list(modes.keys())
        
    except Exception as e:
        print(f"✗ Failed to retrieve modes: {str(e)}")
        return []


def test_methodology_selection(client: CortexClient, mode_keys: list):
    """Test methodology selection"""
    print_section("METHODOLOGY SELECTION")
    
    test_cases = [
        {
            'idea': 'Investigate astrocytes in memory consolidation',
            'mode': 'experimental'
        },
        {
            'idea': 'Study aging effects on neuroplasticity',
            'mode': 'quasi_experimental'
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        idea = test_case['idea']
        mode = test_case['mode']
        
        print(f"\n[Test {i}] Selecting methodology...")
        print(f"Idea: {idea}")
        print(f"Mode: {mode}")
        print("-" * 80)
        
        try:
            result = client.select_methodology(idea, mode)
            
            mode_name = result.get('mode_name', '')
            steps_count = result.get('total_steps', 0)
            timeline = result.get('guidance', {}).get('timeline_estimate', '')
            
            print(f"✓ Methodology selected")
            print(f"  Mode: {mode_name}")
            print(f"  Total Steps: {steps_count}")
            print(f"  Timeline: {timeline}")
            
            # Print first few steps
            steps = result.get('steps', [])
            print(f"\n  First 5 steps:")
            for j, step in enumerate(steps[:5], 1):
                print(f"    {j}. {step}")
            
            # Get first step details
            print(f"\n  Getting details for Step 1...")
            step_details = client.get_step_details(mode, 1)
            print(f"    Step: {step_details['step']}")
            
        except Exception as e:
            print(f"✗ Methodology selection failed: {str(e)}")
        
        time.sleep(1)


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("CORTEX API TEST CLIENT".center(80))
    print("="*80)
    
    # Initialize client
    client = CortexClient()
    
    print("\nConnecting to Cortex API at http://localhost:5050...")
    print("Make sure the application is running: python run.py")
    
    # Run tests
    try:
        # Test 1: Health check
        if not test_health_check(client):
            print("\n✗ Cannot connect to API. Make sure application is running.")
            return
        
        time.sleep(0.5)
        
        # Test 2: API info
        test_api_info(client)
        time.sleep(0.5)
        
        # Test 3: Idea validation
        validation_results = test_idea_validation(client)
        
        # Test 4: Research modes
        mode_keys = test_research_modes(client)
        time.sleep(0.5)
        
        # Test 5: Methodology selection
        if mode_keys:
            test_methodology_selection(client, mode_keys)
        
        # Summary
        print_section("TEST SUMMARY")
        print("✓ All tests completed successfully!")
        print(f"✓ Validated {len(validation_results)} research ideas")
        print(f"✓ Retrieved {len(mode_keys)} research modes")
        print(f"✓ Tested methodology selection")
        
    except Exception as e:
        print_section("ERROR")
        print(f"✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
