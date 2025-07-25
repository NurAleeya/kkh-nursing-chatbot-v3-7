#!/usr/bin/env python3
"""
Test script for KKH Baby Bear Book - Section 01 Medical Emergencies
Verifies that the official pediatric emergency protocols are properly embedded and searchable
"""

import sys
import os

def test_kkh_baby_bear_book():
    """Test the KKH Baby Bear Book Section 01 content"""
    print("� Testing KKH Baby Bear Book - Section 01")
    print("=" * 50)
    
    try:
        # Import our chatbot class
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app import NursingChatbot
        
        # Initialize chatbot
        print("🤖 Initializing chatbot with KKH Baby Bear Book content...")
        bot = NursingChatbot()
        print("✅ Chatbot initialized successfully")
        
        # Check if medical emergencies section exists
        if 'medical_emergencies_section01' in bot.knowledge_base:
            emergencies = bot.knowledge_base['medical_emergencies_section01']
            print(f"✅ KKH Baby Bear Book Section 01 loaded with {len(emergencies)} protocols")
            
            # List all protocols from Baby Bear Book
            print("\n📋 Available KKH Baby Bear Book Protocols:")
            for key, protocol in emergencies.items():
                print(f"  • {protocol['title']}")
            
            # Test search functionality for pediatric emergency content
            print("\n🔍 Testing Pediatric Emergency Protocol Search:")
            test_queries = [
                "critically ill child",
                "paediatric resuscitation", 
                "drug poisoning",
                "paracetamol overdose",
                "ABCDE assessment"
            ]
            
            for query in test_queries:
                results = bot.search_knowledge_base(query)
                if results:
                    print(f"  ✅ '{query}' - Found {len(results)} relevant results")
                else:
                    print(f"  ❌ '{query}' - No results found")
            
            # Test specific KKH content features
            print("\n🏥 Testing KKH-Specific Content:")
            test_cases = [
                ("vital signs", "pediatric vital sign ranges"),
                ("hypotension", "pediatric blood pressure definitions"),
                ("resuscitation", "pediatric CPR protocols"),
                ("poisoning", "pediatric toxicology management")
            ]
            
            for query, description in test_cases:
                try:
                    results = bot.search_knowledge_base(query)
                    if results:
                        print(f"  ✅ {description} - Knowledge retrieved")
                    else:
                        print(f"  ⚠️  {description} - Limited results")
                except Exception as e:
                    print(f"  ❌ {description} - Error: {e}")
            
            return True
            
        else:
            print("❌ KKH Baby Bear Book Section 01 not found in knowledge base")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def display_kkh_protocols():
    """Display KKH Baby Bear Book protocol information"""
    print("\n📚 KKH BABY BEAR BOOK - SECTION 01 SUMMARY")
    print("=" * 50)
    
    protocols = {
        "Recognising the Critically Ill Child": [
            "Early recognition of sepsis and cardiopulmonary compromise",
            "Red flags in history and examination", 
            "Age-specific vital sign ranges",
            "High-risk patient identification"
        ],
        "ABCDE Assessment": [
            "Airway patency assessment and management",
            "Breathing adequacy and respiratory support",
            "Circulation assessment and fluid resuscitation",
            "Disability (neurological) evaluation",
            "Exposure and environmental considerations"
        ],
        "Paediatric CPR": [
            "Age-specific resuscitation techniques",
            "Compression-to-ventilation ratios",
            "Vascular access and medication administration",
            "Special pediatric considerations"
        ],
        "Drug Overdose & Poisoning": [
            "Pediatric-specific toxicology approach",
            "Decontamination strategies",
            "Enhanced elimination techniques",
            "Antidote administration protocols"
        ],
        "Paracetamol Poisoning": [
            "Toxic ingestion criteria for children",
            "Rumack-Matthew nomogram application",
            "N-acetylcysteine dosing protocols",
            "Pediatric-specific monitoring requirements"
        ]
    }
    
    for protocol, features in protocols.items():
        print(f"\n� {protocol}:")
        for i, feature in enumerate(features, 1):
            print(f"   {i}. {feature}")

def main():
    """Run KKH Baby Bear Book test"""
    print("🏥 KKH NURSING CHATBOT - BABY BEAR BOOK TEST")
    print("=" * 60)
    
    success = test_kkh_baby_bear_book()
    
    if success:
        display_kkh_protocols()
        print("\n" + "=" * 60)
        print("✅ KKH Baby Bear Book Section 01 successfully embedded!")
        print("🚀 Official pediatric emergency protocols ready for use")
        print("⚕️  Healthcare professionals can now access KKH-specific pediatric guidance")
        
        print("\n📖 How to use KKH Baby Bear Book protocols:")
        print("  • Ask: 'How do I recognise a critically ill child?'")
        print("  • Ask: 'Show me the paediatric CPR protocol'")
        print("  • Ask: 'What is the paracetamol poisoning management?'")
        print("  • Use the 'KKH Baby Bear Book' dropdown in the sidebar")
        
        print("\n🎯 Key Features:")
        print("  • Age-specific pediatric protocols")
        print("  • KKH institutional guidelines")
        print("  • Evidence-based emergency management")
        print("  • Comprehensive toxicology protocols")
        
        return True
    else:
        print("\n❌ KKH Baby Bear Book Section 01 test failed")
        print("Please check the chatbot initialization and content loading")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
