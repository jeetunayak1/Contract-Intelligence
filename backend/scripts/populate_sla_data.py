"""
Populate SLA Data for SOW Obligations
Adds realistic deadlines and penalty amounts to existing SOW obligations
"""
import asyncio
from datetime import datetime, timedelta
import random
from app.core.cloudant_db import cloudant_db


async def populate_sla_data():
    """Add SLA terms to all SOW obligations"""
    
    print("🔍 Fetching SOWs...")
    sows = await cloudant_db.query_documents({"type": "sow"}, limit=100)
    
    if not sows:
        print("❌ No SOWs found")
        return
    
    print(f"✅ Found {len(sows)} SOWs")
    
    for sow in sows:
        sow_id = sow.get("_id")
        obligations = sow.get("obligations", [])
        
        if not obligations:
            print(f"⚠️  {sow_id}: No obligations")
            continue
        
        print(f"\n📋 Processing {sow_id}...")
        print(f"   Obligations: {len(obligations)}")
        
        updated = False
        for i, obligation in enumerate(obligations):
            # Skip if already has deadline and penalty
            if obligation.get("deadline") and obligation.get("penalty_amount"):
                continue
            
            # Add realistic deadline
            if i == 0:
                # First obligation - some overdue
                days_offset = random.randint(-5, 14)
            elif i == 1:
                # Second obligation - upcoming
                days_offset = random.randint(7, 30)
            else:
                # Others - future
                days_offset = random.randint(14, 60)
            
            deadline = (datetime.utcnow() + timedelta(days=days_offset)).isoformat() + "Z"
            
            # Add realistic penalty
            penalties = [1000, 2000, 3000, 5000, 10000]
            penalty_amount = random.choice(penalties)
            
            # Determine priority based on penalty
            if penalty_amount >= 5000:
                priority = "critical"
                risk_level = "critical"
            elif penalty_amount >= 2000:
                priority = "high"
                risk_level = "high"
            else:
                priority = "medium"
                risk_level = "medium"
            
            # Update obligation
            obligation["deadline"] = deadline
            obligation["penalty_amount"] = float(penalty_amount)
            obligation["penalty_per_day"] = float(penalty_amount)
            obligation["priority"] = priority
            obligation["risk_level"] = risk_level
            obligation["status"] = "in_progress" if days_offset > 0 else "at_risk"
            
            updated = True
            print(f"   ✅ Obligation {i+1}: ${penalty_amount}/day, Due: {deadline[:10]}")
        
        if updated:
            # Update financial summary
            total_penalties = sum(o.get("penalty_amount", 0) for o in obligations)
            high_risk_count = sum(1 for o in obligations if o.get("risk_level") in ["critical", "high"])
            
            sow["financial_summary"] = {
                "total_penalties_at_risk": total_penalties,
                "high_risk_obligations": high_risk_count,
                "penalties_avoided": 0,
                "margin_protected": 0,
                "scope_creep_value": 0
            }
            
            # Save updated SOW
            try:
                await cloudant_db.update_document(sow_id, sow)
                print(f"   💾 Saved: Total penalty exposure ${total_penalties:,.0f}")
            except Exception as e:
                print(f"   ❌ Error saving: {e}")
    
    print("\n✨ SLA data population complete!")


if __name__ == "__main__":
    asyncio.run(populate_sla_data())

# Made with Bob
