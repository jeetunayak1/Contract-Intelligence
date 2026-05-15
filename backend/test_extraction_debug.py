"""
Debug script to see what the LLM is actually returning
"""
import asyncio
import sys
import json
sys.path.insert(0, '.')

from app.agents.contract_agent_feature import ContractIntelligenceAgent

# Small sample contract
contract_text = """
STATEMENT OF WORK
Contract ID: SOW-2024-001
Client: Acme Corporation
Provider: TechServices Inc

1. INCIDENT RESPONSE SLAs
Priority 1 (P1) - Critical:
- Acknowledgment: 15 minutes
- Resolution: 4 hours
- Availability: 24x7x365

Priority 2 (P2) - High:
- Acknowledgment: 30 minutes
- Resolution: 8 hours

2. SERVICE CREDITS
- P1 Resolution exceeds 4 hours: 2% service credit
- Monthly Cap: 10% of monthly fees

3. LIABILITY EXCLUSIONS
- Client infrastructure failures
- Force majeure events
"""

async def test():
    print("=" * 80)
    print("CREATING FRESH AGENT")
    print("=" * 80)
    agent = ContractIntelligenceAgent()
    
    print("\n" + "=" * 80)
    print("EXTRACTING CONTRACT")
    print("=" * 80)
    
    try:
        result = await agent.extract_contract(contract_text, 'test.txt', 'test-debug')
        
        print("\n" + "=" * 80)
        print("EXTRACTION SUCCESSFUL")
        print("=" * 80)
        
        result_dict = result.model_dump()
        
        print(f"\nCompliance SLAs: {len(result_dict['compliance_obligations']['incident_slas'])}")
        print(f"Risk Credits: {len(result_dict['risk_obligations']['service_credits'])}")
        print(f"Liability Exclusions: {len(result_dict['liability_obligations']['liability_exclusions'])}")
        
        print("\n" + "=" * 80)
        print("FULL EXTRACTED DATA")
        print("=" * 80)
        print(json.dumps(result_dict, indent=2))
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())

# Made with Bob
