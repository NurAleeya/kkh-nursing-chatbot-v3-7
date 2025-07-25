#!/usr/bin/env python3
"""
KKH Nursing Chatbot - Feature Demo Script
Demonstrates key functionality without requiring external LLM connection
"""

import json
from datetime import datetime

class DemoChatbot:
    """Demo version of the nursing chatbot for testing purposes"""
    
    def __init__(self):
        self.knowledge_base = {
            "protocols": {
                "hand_hygiene": "Hand hygiene protocol: 5 moments, 20-30 seconds alcohol rub...",
                "medication_admin": "Five rights: Right patient, drug, dose, route, time..."
            },
            "calculations": {
                "fluid_requirements": "Holliday-Segar method for pediatric fluids..."
            }
        }
    
    def calculate_fluid_requirements(self, weight_kg):
        """Calculate pediatric fluid requirements"""
        daily_ml = 0
        hourly_ml = 0
        
        if weight_kg <= 10:
            daily_ml = weight_kg * 100
            hourly_ml = weight_kg * 4
        elif weight_kg <= 20:
            daily_ml = 1000 + (weight_kg - 10) * 50
            hourly_ml = 40 + (weight_kg - 10) * 2
        else:
            daily_ml = 1500 + (weight_kg - 20) * 20
            hourly_ml = 60 + (weight_kg - 20) * 1
        
        return {
            "weight_kg": weight_kg,
            "daily_ml": daily_ml,
            "hourly_ml": hourly_ml,
            "daily_liters": daily_ml / 1000
        }
    
    def search_knowledge_base(self, query):
        """Simple search simulation"""
        results = []
        for category in self.knowledge_base.values():
            for key, content in category.items():
                if any(word.lower() in content.lower() for word in query.split()):
                    results.append(content)
        return results[:3]

def demo_features():
    """Demonstrate key chatbot features"""
    print("🏥 KKH Nursing Chatbot - Feature Demonstration")
    print("=" * 60)
    
    bot = DemoChatbot()
    
    # Feature 1: Fluid Calculations
    print("\n🧮 FLUID CALCULATION DEMO")
    print("-" * 30)
    test_weights = [5, 15, 25, 30]
    
    for weight in test_weights:
        result = bot.calculate_fluid_requirements(weight)
        print(f"Patient: {weight} kg")
        print(f"  Daily:  {result['daily_ml']} mL ({result['daily_liters']:.1f} L)")
        print(f"  Hourly: {result['hourly_ml']} mL/hr")
        print()
    
    # Feature 2: Knowledge Base Search
    print("🔍 KNOWLEDGE BASE SEARCH DEMO")
    print("-" * 30)
    queries = ["hand hygiene", "medication", "five rights"]
    
    for query in queries:
        results = bot.search_knowledge_base(query)
        print(f"Query: '{query}'")
        print(f"Results: {len(results)} found")
        for i, result in enumerate(results[:1], 1):
            print(f"  {i}. {result[:50]}...")
        print()
    
    # Feature 3: Educational Quiz Questions
    print("🎯 EDUCATIONAL QUIZ DEMO")
    print("-" * 30)
    quiz_questions = [
        {
            "question": "How long should alcohol-based hand rub be applied?",
            "options": ["10-15 seconds", "20-30 seconds", "45-60 seconds"],
            "correct": 1
        },
        {
            "question": "What is the first 'Right' in medication administration?",
            "options": ["Right time", "Right patient", "Right dose"],
            "correct": 1
        }
    ]
    
    for i, quiz in enumerate(quiz_questions, 1):
        print(f"Question {i}: {quiz['question']}")
        for j, option in enumerate(quiz['options']):
            marker = "✓" if j == quiz['correct'] else " "
            print(f"  {marker} {j+1}. {option}")
        print()
    
    # Feature 4: Clinical Scenarios
    print("🏥 CLINICAL SCENARIOS DEMO")
    print("-" * 30)
    scenarios = [
        "Pediatric patient with dehydration requiring fluid resuscitation",
        "Adult patient with suspected infection requiring isolation precautions",
        "Medication administration for high-alert drugs",
        "Emergency response for cardiac arrest"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario}")
    print()

def show_deployment_info():
    """Show deployment and usage information"""
    print("🚀 DEPLOYMENT INFORMATION")
    print("=" * 60)
    
    print("\n📋 Key Features:")
    print("• Information Retrieval - Nursing protocols, guidelines, procedures")
    print("• Clinical Calculations - Fluid requirements, drug dosages, IV rates")  
    print("• Educational Tools - Interactive quizzes, clinical scenarios")
    print("• Real-time Chat - Powered by Phi-2 model via LM Studio")
    print("• Semantic Search - all-MiniLM-L6-v2 embedding model")
    
    print("\n🔧 Technical Stack:")
    print("• Frontend: Streamlit web application")
    print("• Backend: Python with sentence-transformers")
    print("• LLM: Phi-2 model at http://10.175.5.70:1234")
    print("• Vector DB: FAISS for similarity search")
    print("• Deployment: Fly.io with Docker containers")
    
    print("\n🌐 Deployment URLs:")
    print("• Local Development: http://localhost:8501")
    print("• Production: https://kkh-nursing-chatbot.fly.dev")
    
    print("\n📚 Quick Start Commands:")
    print("• Local run: streamlit run app.py")
    print("• Deploy: fly deploy")
    print("• Test: python verify.py")
    
    print("\n🎯 Target Users:")
    print("• Nursing staff at KK Women's and Children's Hospital")
    print("• Healthcare students and trainees")
    print("• Medical professionals seeking quick reference")
    
    print("\n⚕️ Use Cases:")
    print("• Quick protocol lookup during patient care")
    print("• Accurate clinical calculations")
    print("• Continuing education and skill assessment")
    print("• Emergency procedure guidance")

def create_sample_config():
    """Create sample configuration for demonstration"""
    config = {
        "app_info": {
            "name": "KKH Nursing Assistant Chatbot",
            "version": "1.0.0",
            "description": "Intelligent nursing assistant for KKH",
            "target_users": "Healthcare professionals"
        },
        "features": {
            "information_retrieval": True,
            "clinical_calculations": True,
            "educational_tools": True,
            "interactive_chat": True
        },
        "technical_specs": {
            "llm_model": "phi-2",
            "embedding_model": "all-MiniLM-L6-v2",
            "vector_db": "faiss",
            "framework": "streamlit"
        },
        "deployment": {
            "platform": "fly.io",
            "region": "singapore",
            "auto_scale": True,
            "https_enabled": True
        }
    }
    
    print("\n📄 Configuration Summary:")
    print(json.dumps(config, indent=2))

def main():
    """Main demonstration function"""
    print("🏥 KKH NURSING CHATBOT - COMPLETE DEMO")
    print("=" * 70)
    print(f"Demo generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run feature demonstrations
    demo_features()
    
    # Show deployment information
    show_deployment_info()
    
    # Show configuration
    create_sample_config()
    
    print("\n" + "=" * 70)
    print("✅ Demo completed successfully!")
    print("🚀 Ready for deployment to Fly.io")
    print("📖 See DEPLOYMENT.md for detailed deployment instructions")
    print("🔧 Run 'python verify.py' to test the installation")

if __name__ == "__main__":
    main()
