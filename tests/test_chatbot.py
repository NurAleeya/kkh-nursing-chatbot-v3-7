import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import NursingChatbot

class TestNursingChatbot(unittest.TestCase):
    
    def setUp(self):
        self.chatbot = NursingChatbot()
    
    def test_fluid_calculation_pediatric(self):
        """Test pediatric fluid requirements calculation"""
        # Test case 1: 5kg infant
        result = self.chatbot.calculate_fluid_requirements(5.0)
        self.assertEqual(result['daily_ml'], 500)
        self.assertEqual(result['hourly_ml'], 20)
        
        # Test case 2: 15kg child  
        result = self.chatbot.calculate_fluid_requirements(15.0)
        self.assertEqual(result['daily_ml'], 1250)
        self.assertEqual(result['hourly_ml'], 50)
        
        # Test case 3: 25kg child
        result = self.chatbot.calculate_fluid_requirements(25.0)
        self.assertEqual(result['daily_ml'], 1600)
        self.assertEqual(result['hourly_ml'], 65)
    
    def test_knowledge_base_search(self):
        """Test knowledge base search functionality"""
        results = self.chatbot.search_knowledge_base("hand hygiene")
        self.assertGreater(len(results), 0)
        self.assertTrue(any("hand hygiene" in result.lower() for result in results))
    
    def test_calculation_request_detection(self):
        """Test detection of calculation requests"""
        calc_queries = [
            "calculate fluid requirements for 10kg patient",
            "what is the fluid calculation for 15kg child",
            "dosage calculation for medication"
        ]
        
        for query in calc_queries:
            response = self.chatbot.handle_calculation_request(query)
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)
    
    def test_knowledge_base_initialization(self):
        """Test that knowledge base is properly initialized"""
        self.assertIsNotNone(self.chatbot.knowledge_base)
        self.assertIn('protocols', self.chatbot.knowledge_base)
        self.assertIn('calculations', self.chatbot.knowledge_base)
        self.assertIn('emergency_procedures', self.chatbot.knowledge_base)

if __name__ == '__main__':
    unittest.main()
