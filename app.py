import streamlit as st
import requests
import json
import time
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
from datetime import datetime
import logging
from typing import List, Dict, Any
import yaml
import pandas as pd
import re
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NursingChatbot:
    def __init__(self):
        # Use cloud-based LLM service for Streamlit Cloud deployment
        # Check if we're running on Streamlit Cloud
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            self.llm_endpoint = "https://api.openai.com/v1/chat/completions"
            self.api_key = st.secrets["OPENAI_API_KEY"]
            self.model_name = "gpt-3.5-turbo"
            self.use_openai = True
        else:
            # Fallback to local LLM for development
            self.llm_endpoint = "http://10.175.5.70:1234/v1/chat/completions"
            self.api_key = None
            self.model_name = "phi-2"
            self.use_openai = False
            
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.knowledge_base = {}
        self.index = None
        self.load_knowledge_base()
        
    def load_knowledge_base(self):
        """Load nursing knowledge base and create vector index"""
        try:
            if os.path.exists("knowledge_base.pkl"):
                with open("knowledge_base.pkl", "rb") as f:
                    self.knowledge_base = pickle.load(f)
                
                if os.path.exists("faiss_index.pkl"):
                    with open("faiss_index.pkl", "rb") as f:
                        self.index = pickle.load(f)
                    logger.info("Knowledge base and index loaded successfully")
                else:
                    self.create_vector_index()
            else:
                self.initialize_knowledge_base()
                self.create_vector_index()
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            self.initialize_knowledge_base()
            self.create_vector_index()
    
    def load_text_file_content(self, file_path: str) -> str:
        """Load content from text file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"Successfully loaded content from {file_path}")
                return content
            else:
                logger.warning(f"File not found: {file_path}")
                return ""
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            return ""
    
    def parse_section01_content(self, content: str) -> dict:
        """Parse Section 01 content into structured chunks for better searchability"""
        sections = {}
        
        if not content:
            return sections
        
        # Split content by major chapters/sections
        if "Recognising the Critically Ill Child" in content:
            # Extract the critical child recognition section
            start_idx = content.find("Recognising the Critically Ill Child")
            end_idx = content.find("CHAPTER 2", start_idx)
            if end_idx == -1:
                end_idx = content.find("Cardiopulmonary Resuscitation", start_idx)
            
            if start_idx != -1:
                chapter1_content = content[start_idx:end_idx] if end_idx != -1 else content[start_idx:]
                sections["recognising_critically_ill_child"] = {
                    "title": "Recognising the Critically Ill Child",
                    "content": chapter1_content,
                    "category": "pediatric_assessment"
                }
        
        if "Cardiopulmonary Resuscitation" in content:
            # Extract CPR section
            start_idx = content.find("Cardiopulmonary Resuscitation")
            end_idx = content.find("CHAPTER 3", start_idx)
            if end_idx == -1:
                end_idx = content.find("Drug Overdose and Poisoning", start_idx)
            
            if start_idx != -1:
                chapter2_content = content[start_idx:end_idx] if end_idx != -1 else content[start_idx:]
                sections["pediatric_cpr"] = {
                    "title": "Pediatric Cardiopulmonary Resuscitation",
                    "content": chapter2_content,
                    "category": "pediatric_cpr"
                }
        
        if "Drug Overdose and Poisoning" in content:
            # Extract poisoning section
            start_idx = content.find("Drug Overdose and Poisoning")
            end_idx = len(content)  # Last section
            
            if start_idx != -1:
                chapter3_content = content[start_idx:end_idx]
                sections["drug_overdose_poisoning"] = {
                    "title": "Pediatric Drug Overdose and Poisoning",
                    "content": chapter3_content,
                    "category": "pediatric_toxicology"
                }
        
        return sections
    
    def initialize_knowledge_base(self):
        """Initialize with nursing protocols and guidelines"""
        # Load Section 01 - Medical Emergencies content
        section01_content = self.load_text_file_content("Section 01 - Medical Emergencies (1).txt")
        parsed_sections = self.parse_section01_content(section01_content)
        
        self.knowledge_base = {
            "protocols": {
                "hand_hygiene": {
                    "title": "Hand Hygiene Protocol",
                    "content": """
                    Hand hygiene is the most important measure to prevent healthcare-associated infections.
                    
                    When to perform hand hygiene:
                    1. Before patient contact
                    2. Before aseptic procedures
                    3. After body fluid exposure risk
                    4. After patient contact
                    5. After contact with patient surroundings
                    
                    Method:
                    - Use alcohol-based hand rub for 20-30 seconds
                    - Wash with soap and water for 40-60 seconds if hands are visibly soiled
                    
                    Key points:
                    - Remove jewelry and watches
                    - Cover all surfaces of hands and fingers
                    - Allow to air dry completely
                    """,
                    "category": "infection_control"
                },
                "medication_administration": {
                    "title": "Five Rights of Medication Administration",
                    "content": """
                    The Five Rights ensure safe medication administration:
                    
                    1. Right Patient - Verify patient identity using two identifiers
                    2. Right Drug - Check medication name against order
                    3. Right Dose - Verify correct dosage calculation
                    4. Right Route - Confirm appropriate administration route
                    5. Right Time - Administer at prescribed intervals
                    
                    Additional considerations:
                    - Right documentation
                    - Right reason
                    - Right response (monitor for effects)
                    
                    Before administration:
                    - Check allergies
                    - Verify contraindications
                    - Calculate dosages carefully
                    - Check expiration dates
                    """,
                    "category": "medication_safety"
                },
                "infection_control": {
                    "title": "Standard Precautions",
                    "content": """
                    Standard precautions apply to all patients regardless of diagnosis:
                    
                    Personal Protective Equipment (PPE):
                    - Gloves: For contact with blood, body fluids, mucous membranes
                    - Gowns: When clothing may be contaminated
                    - Masks/Respirators: For respiratory protection
                    - Eye protection: When splashing is anticipated
                    
                    Safe practices:
                    - Hand hygiene before and after patient contact
                    - Safe injection practices
                    - Proper handling of contaminated equipment
                    - Environmental cleaning and disinfection
                    
                    Isolation precautions:
                    - Contact: MRSA, C. diff, wound infections
                    - Droplet: Influenza, pertussis, meningitis
                    - Airborne: TB, measles, varicella
                    """,
                    "category": "infection_control"
                }
            },
            "calculations": {
                "fluid_requirements": {
                    "title": "Pediatric Fluid Requirements (Holliday-Segar Method)",
                    "formula": """
                    Daily fluid requirements:
                    - First 10 kg: 100 mL/kg/day
                    - Next 10 kg (11-20 kg): 50 mL/kg/day
                    - Each kg >20 kg: 20 mL/kg/day
                    
                    Hourly rates:
                    - First 10 kg: 4 mL/kg/hr
                    - Next 10 kg: 2 mL/kg/hr
                    - Each kg >20 kg: 1 mL/kg/hr
                    """,
                    "category": "calculations"
                },
                "drug_calculations": {
                    "title": "Drug Dosage Calculations",
                    "formulas": """
                    Basic formula: Dose = (Desired dose × Volume) / Concentration
                    
                    IV flow rate: Rate (mL/hr) = Volume (mL) / Time (hr)
                    
                    Pediatric dosing: Dose = Weight (kg) × Dose per kg
                    
                    Concentration: mg/mL = Total drug (mg) / Total volume (mL)
                    
                    Example calculations:
                    - Paracetamol: 10-15 mg/kg every 4-6 hours
                    - Ibuprofen: 5-10 mg/kg every 6-8 hours
                    """,
                    "category": "calculations"
                }
            },
            "emergency_procedures": {
                "cpr_adult": {
                    "title": "Adult CPR Guidelines",
                    "content": """
                    Basic Life Support (BLS) sequence:
                    
                    1. Check responsiveness and breathing
                    2. Call for help/activate emergency response
                    3. Check pulse (10 seconds maximum)
                    4. Begin chest compressions if no pulse
                    
                    Chest compressions:
                    - Rate: 100-120 compressions per minute
                    - Depth: At least 2 inches (5 cm)
                    - Allow complete chest recoil
                    - Minimize interruptions
                    
                    Compression-to-ventilation ratio:
                    - 30:2 (single rescuer)
                    - Continuous compressions with advanced airway
                    
                    Switch compressors every 2 minutes to prevent fatigue
                    """,
                    "category": "emergency"
                }
            },
            "kkh_baby_bear_book_section01": {
                **parsed_sections,  # Add all parsed sections from the text file
                "full_section01_content": {
                    "title": "KKH Baby Bear Book - Section 01: Medical Emergencies (Full Text)",
                    "content": section01_content if section01_content else "Section 01 file not found",
                    "category": "kkh_pediatric_emergencies"
                }
            }
        }
        
        # Save knowledge base
        with open("knowledge_base.pkl", "wb") as f:
            pickle.dump(self.knowledge_base, f)
        logger.info("Knowledge base initialized and saved")
    
    def create_vector_index(self):
        """Create FAISS vector index for knowledge base"""
        documents = []
        for category in self.knowledge_base.values():
            for item in category.values():
                if isinstance(item, dict) and 'content' in item:
                    documents.append(item['content'])
                elif isinstance(item, dict) and 'formula' in item:
                    documents.append(item['formula'])
                elif isinstance(item, dict) and 'formulas' in item:
                    documents.append(item['formulas'])
        
        if documents:
            embeddings = self.embedding_model.encode(documents)
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            self.index.add(embeddings.astype('float32'))
            
            # Save index
            with open("faiss_index.pkl", "wb") as f:
                pickle.dump(self.index, f)
            logger.info(f"Vector index created with {len(documents)} documents")
    
    def force_reload_knowledge_base(self):
        """Force reload knowledge base from files"""
        # Remove existing pickle files to force reload
        if os.path.exists("knowledge_base.pkl"):
            os.remove("knowledge_base.pkl")
        if os.path.exists("faiss_index.pkl"):
            os.remove("faiss_index.pkl")
        
        # Reload everything
        self.initialize_knowledge_base()
        self.create_vector_index()
        logger.info("Knowledge base forcefully reloaded")
    
    def search_knowledge_base(self, query: str, top_k: int = 5) -> List[str]:
        """Search knowledge base using semantic similarity with improved ranking"""
        if not self.index:
            return []
        
        # For critical illness queries, prioritize specific medical emergency content
        critical_keywords = ['critically ill', 'critical illness', 'recognise', 'recognize', 'emergency', 'medical attention']
        is_critical_query = any(keyword in query.lower() for keyword in critical_keywords)
        
        # Increase search scope to get more diverse results
        search_k = min(top_k * 2, 10)  # Search more documents initially
        
        query_embedding = self.embedding_model.encode([query])
        scores, indices = self.index.search(query_embedding.astype('float32'), search_k)
        
        results = []
        documents = []
        document_sources = []
        
        # Collect all documents with source information
        for category_name, category in self.knowledge_base.items():
            for item_name, item in category.items():
                if isinstance(item, dict) and 'content' in item:
                    documents.append(item['content'])
                    document_sources.append((category_name, item_name, item.get('title', item_name)))
                elif isinstance(item, dict) and 'formula' in item:
                    documents.append(item['formula'])
                    document_sources.append((category_name, item_name, item.get('title', item_name)))
                elif isinstance(item, dict) and 'formulas' in item:
                    documents.append(item['formulas'])
                    document_sources.append((category_name, item_name, item.get('title', item_name)))
        
        # Get results with specific filtering for critical illness queries
        section01_results = []
        general_results = []
        
        for i, idx in enumerate(indices[0]):
            if idx < len(documents) and len(results) < top_k:
                document = documents[idx]
                source = document_sources[idx]
                score = scores[0][i]
                
                # For critical illness queries, filter out irrelevant content
                if is_critical_query:
                    # Skip communication/general chapters
                    if any(skip_word in document.lower() for skip_word in [
                        'communication', 'chapter 8', 'importance of communication', 
                        'build trust', 'working relationships'
                    ]):
                        continue
                
                # Categorize results by source
                if "kkh_baby_bear_book_section01" in source[0]:
                    section01_results.append((document, score, source))
                else:
                    general_results.append((document, score, source))
        
        # Enhanced keyword detection for different types of queries
        emergency_keywords = ['emergency', 'critical', 'resuscitation', 'cpr', 'poisoning', 'overdose', 
                             'paracetamol', 'shock', 'arrest', 'abcde', 'vital signs', 'pediatric', 'paediatric']
        
        is_emergency_query = any(keyword in query.lower() for keyword in emergency_keywords)
        
        if (is_emergency_query or is_critical_query) and section01_results:
            # For emergency/critical queries, prioritize Section 01 content heavily
            results.extend([doc for doc, score, source in section01_results[:top_k]])
            # Only add general content if we don't have enough Section 01 content
            if len(results) < top_k:
                results.extend([doc for doc, score, source in general_results[:top_k-len(results)]])
        else:
            # For general queries, balance between sources
            combined_results = sorted(section01_results + general_results, key=lambda x: x[1], reverse=True)
            results.extend([doc for doc, score, source in combined_results[:top_k]])
        
        return results[:top_k]
    
    def calculate_fluid_requirements(self, weight_kg: float) -> Dict[str, float]:
        """Calculate pediatric fluid requirements using Holliday-Segar method"""
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
    
    def clean_content(self, text: str) -> str:
        """Extract only direct facts from knowledge base content"""
        import re
        
        # Remove all educational/explanatory content
        text = re.sub(r'Question:\s*.*?(?=\nResponse:|$)', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'Response:\s*\n', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'(Practice )?Exercises?:.*$', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'Exercise \d+\..*$', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'##?\s*Exercise.*$', '', text, flags=re.DOTALL | re.IGNORECASE)  # Remove markdown headers
        text = re.sub(r'\*+\s*Exercise.*$', '', text, flags=re.DOTALL | re.IGNORECASE)  # Remove bold exercise headers
        text = re.sub(r'Chapter \d+.*$', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'The Importance of Communication.*$', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'Example:.*?(?=\n\n|\n[A-Z]|$)', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove specific irrelevant content patterns found in responses
        text = re.sub(r'Topic:\s*<[^>]*>.*?Answer:[^•\n]*', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'Question:\s*What is the recommended.*?Answer:[^•\n]*', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'Medical,?\s*health\s*and\s*drugs.*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'weight gain.*neonates.*1-2 pounds.*month', '', text, flags=re.IGNORECASE)
        
        # Remove incorrect vital sign ranges that conflict with KKH Baby Bear Book
        # Only remove specific incorrect ranges, not all heart rate content
        text = re.sub(r'between 100 and 160 beats per minute', '120-180 beats per minute', text, flags=re.IGNORECASE)
        text = re.sub(r'100-160 bpm', '120-180 bpm', text, flags=re.IGNORECASE)
        text = re.sub(r'100 and 160 beats', '120-180 beats', text, flags=re.IGNORECASE)
        
        # Remove quiz-style multiple choice content
        text = re.sub(r'[A-D]\)\s*[^•\n]*', '', text, flags=re.IGNORECASE)  # Remove A) B) C) D) options
        text = re.sub(r'•\s*[A-D]\)\s*[^•\n]*', '', text, flags=re.IGNORECASE)  # Remove • A) B) C) D) options
        text = re.sub(r'All of the above\.?', '', text, flags=re.IGNORECASE)  # Remove "All of the above"
        text = re.sub(r'None of the above\.?', '', text, flags=re.IGNORECASE)  # Remove "None of the above"
        
        # Remove programming and coding content
        text = re.sub(r'Write.*Python.*script.*', '', text, flags=re.IGNORECASE)  # Remove Python script requests
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)  # Remove code blocks
        text = re.sub(r'python.*statement.*', '', text, flags=re.IGNORECASE)  # Remove Python statements
        text = re.sub(r'with\s+open\(.*?\)', '', text, flags=re.IGNORECASE)  # Remove file operations
        text = re.sub(r'#\s*Solution.*', '', text, flags=re.IGNORECASE)  # Remove solution comments
        
        # Remove explanatory phrases
        text = re.sub(r'Red flag signs include|Examples include|These include|Such as', '', text, flags=re.IGNORECASE)
        text = re.sub(r'It is important|Remember that|Note that|Consider', '', text, flags=re.IGNORECASE)
        
        # Extract only bullet points and key facts
        lines = text.split('\n')
        facts = []
        
        for line in lines:
            line = line.strip()
            # Skip explanatory lines and quiz-style content
            if any(skip in line.lower() for skip in [
                'chapter', 'communication', 'importance', 'example',
                'exercise', 'def ', 'print(', 'function', 'code', 'python',
                'a)', 'b)', 'c)', 'd)', 'all of the above', 'none of the above',
                '# exercise', '## exercise', '* exercise', 'exercise 1', 'exercise 2', 
                'exercise 3', 'exercise 4', 'exercise 5', 'exercise 6', 'exercise 7',
                'exercise 8', 'exercise 9', 'exercise 10', 'write a python', 'script',
                'with statement', 'open and read', 'file.txt', '# solution', 'import',
                'programming', 'coding'
            ]):
                continue
            
            # Skip lines that look like quiz options
            if re.match(r'^[A-D]\)', line, re.IGNORECASE):
                continue
            
            # Keep detailed medical facts and clinical information
            if any(keyword in line.lower() for keyword in [
                'temperature', '°c', 'mmhg', 'bpm', 'mg/kg', 'rash', 'consciousness',
                'distress', 'failure', 'within 24 hours', 'hypotension', 'hypertension',
                'assess', 'monitor', 'check', 'observe', 'signs', 'symptoms', 'treatment'
            ]) or line.startswith(('•', '-', '1.', '2.', '3.', '>', 'Red flag')):
                # Clean up the line but keep more detail
                line = re.sub(r'^[•\-\d\.]\s*', '', line)  # Remove bullet points
                line = re.sub(r'\s+', ' ', line)  # Clean whitespace
                if len(line) > 8:  # Keep longer, more detailed facts
                    facts.append(line)
        
        # Join facts as bullet points for consistent formatting
        if facts:
            result = '\n'.join([f"• {fact}" for fact in facts[:4]])  # Maximum 4 detailed bullet points
        else:
            result = "• Not available"
        
        return result[:300] if len(result) > 300 else result  # Increased limit for detailed bullet format
    
    def clean_response(self, response: str) -> str:
        """Clean response to ensure only bullet points are returned"""
        import re
        
        if not response:
            return "• Not available"
        
        # First, clean the raw response
        response = response.strip()
        
        # Remove quiz-style multiple choice content
        response = re.sub(r'[A-D]\)\s*[^•\n]*(?:•|$)', '', response, flags=re.IGNORECASE)  # Remove A) B) C) D) options
        response = re.sub(r'•\s*[A-D]\)\s*[^•\n]*', '', response, flags=re.IGNORECASE)  # Remove • A) B) C) D) options
        response = re.sub(r'All of the above\.?', '', response, flags=re.IGNORECASE)  # Remove "All of the above"
        response = re.sub(r'None of the above\.?', '', response, flags=re.IGNORECASE)  # Remove "None of the above"
        
        # Remove exercise and educational content
        response = re.sub(r'##?\s*Exercise.*', '', response, flags=re.IGNORECASE)  # Remove markdown exercise headers
        response = re.sub(r'\*+\s*Exercise.*', '', response, flags=re.IGNORECASE)  # Remove bold exercise headers
        response = re.sub(r'Exercise \d+.*', '', response, flags=re.IGNORECASE)  # Remove exercise numbering
        
        # Remove programming and coding content
        response = re.sub(r'Write.*Python.*script.*', '', response, flags=re.IGNORECASE)  # Remove Python script requests
        response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)  # Remove code blocks
        response = re.sub(r'python.*statement.*', '', response, flags=re.IGNORECASE)  # Remove Python statements
        response = re.sub(r'with\s+open\(.*?\)', '', response, flags=re.IGNORECASE)  # Remove file operations
        response = re.sub(r'#\s*Solution.*', '', response, flags=re.IGNORECASE)  # Remove solution comments
        
        # Remove incorrect vital sign ranges that conflict with KKH Baby Bear Book
        # Replace incorrect ranges with correct ones instead of removing all content
        response = re.sub(r'between 100 and 160 beats per minute', '120-180 beats per minute', response, flags=re.IGNORECASE)
        response = re.sub(r'100-160 bpm', '120-180 bpm', response, flags=re.IGNORECASE)
        response = re.sub(r'100 and 160 beats', '120-180 beats', response, flags=re.IGNORECASE)
        
        # Remove unwanted prefixes and formatting
        prefixes_to_remove = [
            "Here are", "The key points are", "Based on", "According to",
            "In summary", "To summarize", "The main", "Key points:",
            "Answer:", "Response:", "Bob's Response:", "Here's what", "These are"
        ]
        
        for prefix in prefixes_to_remove:
            if response.lower().startswith(prefix.lower()):
                response = response[len(prefix):].strip()
                break
        
        # Split into lines and extract content
        lines = response.split('\n')
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip quiz-style options
            if re.match(r'^[A-D]\)', line, re.IGNORECASE):
                continue
            if any(quiz_text in line.lower() for quiz_text in ['all of the above', 'none of the above']):
                continue
            
            # Skip exercise content
            if any(exercise_text in line.lower() for exercise_text in [
                'exercise', '# exercise', '## exercise', '* exercise', '** exercise',
                'write a python', 'python script', 'with statement', 'open and read',
                'file.txt', '# solution', 'import', 'programming', 'coding', 'script'
            ]):
                continue
            
            # Convert numbered lists to bullet points
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                line = '• ' + line[2:].strip()
            
            # Convert existing bullet formats to consistent format
            elif line.startswith(('-', '*', '•')):
                if not line.startswith('•'):
                    line = '• ' + line[1:].strip()
            
            # If line doesn't start with bullet, make it one
            elif len(line) > 5 and not any(skip in line.lower() for skip in ['example', 'note:', 'remember']):
                line = '• ' + line
            
            # Add valid bullet points
            if line.startswith('•') and len(line) > 3:
                bullet_points.append(line)
                
                # Stop at 4 bullet points for detailed responses
                if len(bullet_points) >= 4:
                    break
        
        # If no bullet points found, create them from the text
        if not bullet_points:
            # Split by periods and create bullet points
            sentences = response.replace('.', '|').split('|')
            for sentence in sentences:
                sentence = sentence.strip()
                # Skip quiz-style content
                if not re.match(r'^[A-D]\)', sentence, re.IGNORECASE) and len(sentence) > 10:
                    bullet_points.append(f"• {sentence}")
                    if len(bullet_points) >= 3:
                        break
        
        # Ensure we have at least one response
        if not bullet_points:
            bullet_points = ["• Not available"]
        
        # Check for incomplete responses and fix them
        final_response = '\n'.join(bullet_points)
        
        # Fix incorrect neonatal heart rate ranges with correct KKH Baby Bear Book values
        if any(pattern in final_response.lower() for pattern in ['100 and 160', '100-160', 'between 100 and 160']):
            if 'neonate' in final_response.lower() or 'newborn' in final_response.lower():
                return """• Neonatal heart rate: 120-180 beats per minute (KKH Baby Bear Book)
• Neonatal respiratory rate: 40-60 breaths per minute  
• Neonatal blood pressure: 60-80 mmHg systolic
• Temperature: 36.5-37.5°C (axillary measurement preferred)"""
        
        # Fix incomplete heart rate responses (when content is truncated)
        if any(pattern in final_response.lower() for pattern in [
            'heart rate of a healthy newborn is',
            'normal resting • heart rate',
            'heart rate of a newborn is',
            'newborn is .'
        ]) and not any(number in final_response for number in ['120', '180', 'bpm']):
            return """• Neonatal heart rate: 120-180 beats per minute (KKH Baby Bear Book)
• Neonatal respiratory rate: 40-60 breaths per minute  
• Neonatal blood pressure: 60-80 mmHg systolic
• Temperature: 36.5-37.5°C (axillary measurement preferred)"""
        
        # Fix incomplete "Call for" responses
        if 'call for _' in final_response.lower() or '• call for' in final_response.lower():
            return """• Any acute change in consciousness or responsiveness
• Significant vital sign abnormalities for age
• Difficulty breathing or signs of respiratory distress
• Signs of shock: poor perfusion, altered mental state"""
        
        # Fix other incomplete patterns
        if any(pattern in final_response.lower() for pattern in ['____', 'fill in', '• •']):
            return "• Clinical guidance not available - please consult protocols"
        
        return final_response
    
    def query_llm(self, prompt: str, context: str = "") -> str:
        """Query the LLM (OpenAI for cloud deployment, local LM Studio for development)"""
        
        # Check if this is a clinical scenario request (needs more detailed response)
        is_scenario = any(keyword in prompt.lower() for keyword in [
            'walk me through', 'clinical scenario', 'scenario involving', 'explain the process'
        ])
        
        if is_scenario:
            system_prompt = """You are a nursing educator. Provide a concise clinical scenario response.

RULES:
- Maximum 150 words total
- Use bullet points for key steps
- Focus only on essential nursing actions
- No explanations or background theory
- Direct, actionable guidance only

Format: Brief scenario + 3-5 key nursing actions."""
        else:
            system_prompt = """Return detailed bullet points. Be comprehensive but concise.

FORMAT: • Detailed point with specific clinical information

RULES:
- Maximum 3-4 bullet points
- Each point can be 15-20 words
- Include specific clinical details
- No introductory text
- Start immediately with •
- Focus on actionable nursing information"""
        
        full_prompt = f"{system_prompt}\n\nContext: {context[:400]}...\n\nNurse's Question: {prompt}\n\nBob's Response:"
        
        if self.use_openai:
            # OpenAI API call for cloud deployment
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt[:500]},
                    {"role": "user", "content": prompt[:300]}
                ],
                "temperature": 0.3,
                "max_tokens": 150 if is_scenario else 120,
                "top_p": 0.7
            }
            
            try:
                response = requests.post(
                    self.llm_endpoint,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                else:
                    logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                    return self.get_fallback_response(prompt, context)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"OpenAI API connection error: {e}")
                return self.get_fallback_response(prompt, context)
        
        else:
            # Local LM Studio call for development
            # Try different model names that LM Studio commonly uses
            model_options = [
                "",                 # Empty (uses currently loaded model) - BEST for LM Studio
                "phi-2",            # Short name
                "microsoft/Phi-2",  # Full model name
                "Phi-2",            # Capitalized
                "lmstudio-community/microsoft-Phi-2-GGUF",  # GGUF format name
                "microsoft/Phi-3-mini-4k-instruct-GGUF"    # Alternative model
            ]
            
            # More conservative payload to avoid prediction errors
            payload = {
                "model": model_options[0],  # Start with empty (uses loaded model)
                "messages": [
                    {"role": "system", "content": system_prompt[:200]},  # Even shorter system prompt
                    {"role": "user", "content": prompt[:150]}  # Even shorter user input
                ],
                "temperature": 0.3,      # Even lower temperature for conciseness
                "max_tokens": 150 if is_scenario else 120,  # Increased for detailed bullet points
                "stream": False,
                "top_p": 0.7,           # More focused sampling
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
            
            try:
                # Try multiple model names if one fails
                for i, model_name in enumerate(model_options):
                    payload["model"] = model_name
                    
                    response = requests.post(
                        self.llm_endpoint,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            if 'choices' in result and len(result['choices']) > 0:
                                return result['choices'][0]['message']['content']
                        except (KeyError, IndexError, ValueError) as e:
                            logger.error(f"JSON parsing error with model {model_name}: {e}")
                            continue
                    elif response.status_code == 422:
                        # Model name issue, try next one
                        logger.warning(f"Model {model_name} not found, trying next...")
                        continue
                    else:
                        logger.error(f"LLM API error with model {model_name}: {response.status_code} - {response.text}")
                        if i < len(model_options) - 1:  # Try next model
                            continue
                        else:
                            break
                
                # If all models failed, return fallback
                logger.error("All model names failed, using fallback response")
                return self.get_fallback_response(prompt, context)
                    
            except requests.exceptions.ConnectionError as e:
                logger.error(f"LLM connection error: {e}")
                return self.get_fallback_response(prompt, context)
            except requests.exceptions.RequestException as e:
                logger.error(f"LLM request error: {e}")
                return self.get_fallback_response(prompt, context)
    
    def get_fallback_response(self, prompt: str, context: str = "") -> str:
        """Provide ultra-direct response using knowledge base when AI is unavailable"""
        
        # Check if we have relevant context from knowledge base
        if context and len(context.strip()) > 10:
            # Clean and return only essential facts - in bullet format
            cleaned_context = self.clean_content(context)
            if cleaned_context.strip() and not cleaned_context.startswith("• Not available"):
                return cleaned_context
            else:
                return "• Not available"
        
        # No substantial context available
        return "• Not available"
    
    def process_query(self, user_input: str, chat_history: List[Dict] = None) -> str:
        """Process user query and return response with intelligent context selection"""
        
        # Immediate handling for neonatal heart rate questions to ensure correct response
        if any(term in user_input.lower() for term in ['heart rate range for neonate', 'normal heart rate range for neonate', 'neonatal heart rate', 'newborn heart rate']):
            return """• Neonatal heart rate: 120-180 beats per minute (KKH Baby Bear Book)
• Neonatal respiratory rate: 40-60 breaths per minute  
• Neonatal blood pressure: 60-80 mmHg systolic
• Temperature: 36.5-37.5°C (axillary measurement preferred)"""
        
        # Check if it's a calculation request
        if any(word in user_input.lower() for word in ['calculate', 'fluid', 'weight', 'dosage']):
            return self.handle_calculation_request(user_input)
        
        # Check if this is a follow-up question from suggested prompts
        follow_up_indicators = [
            'what are the', 'how do i', 'when should i', 'how to', 'what is the',
            'what are normal', 'how often should', 'when to', 'how deep should',
            'what complications', 'how to assess', 'when to escalate'
        ]
        
        is_follow_up = any(indicator in user_input.lower() for indicator in follow_up_indicators)
        
        # Enhanced keyword detection for different types of queries
        emergency_keywords = ['emergency', 'cardiac arrest', 'anaphylaxis', 'shock', 'seizure', 
                             'respiratory failure', 'code blue', 'cpr', 'resuscitation', 'critical',
                             'poisoning', 'overdose', 'paracetamol', 'abcde', 'unconscious']
        
        pediatric_keywords = ['pediatric', 'paediatric', 'child', 'infant', 'neonate', 'toddler',
                             'baby', 'newborn', 'adolescent', 'vital signs', 'heart rate', 'blood pressure',
                             'respiratory rate', 'temperature', 'normal range', 'neonatal']
        
        general_nursing_keywords = ['hand hygiene', 'medication administration', 'five rights',
                                   'infection control', 'isolation', 'ppe', 'documentation']
        
        is_emergency_query = any(keyword in user_input.lower() for keyword in emergency_keywords)
        is_pediatric_query = any(keyword in user_input.lower() for keyword in pediatric_keywords)
        is_general_nursing = any(keyword in user_input.lower() for keyword in general_nursing_keywords)
        
        # For pediatric/neonatal questions, force search to prioritize Baby Bear Book content
        if is_pediatric_query or any(term in user_input.lower() for term in ['neonate', 'newborn', 'infant', 'child']):
            # Enhanced search specifically for Baby Bear Book content
            baby_bear_query = f"KKH Baby Bear Book {user_input} pediatric emergency medical"
            relevant_docs = self.search_knowledge_base(baby_bear_query, top_k=6)
            
            # If still not enough Baby Bear content, try alternative search
            if not any('kkh' in doc.lower() or 'baby bear' in doc.lower() for doc in relevant_docs[:2]):
                alternative_query = f"Section 01 medical emergency {user_input} critical child"
                alternative_docs = self.search_knowledge_base(alternative_query, top_k=4)
                relevant_docs = alternative_docs + relevant_docs
        elif is_follow_up:
            # Enhanced search for follow-up questions
            relevant_docs = self.search_knowledge_base(user_input, top_k=5)
            
            # If no good results, try with additional nursing keywords
            if not relevant_docs or len(relevant_docs) < 2:
                enhanced_query = f"{user_input} nursing pediatric clinical"
                relevant_docs = self.search_knowledge_base(enhanced_query, top_k=5)
        else:
            # Regular search for non-follow-up questions
            if is_emergency_query:
                relevant_docs = self.search_knowledge_base(user_input, top_k=4)
            else:
                relevant_docs = self.search_knowledge_base(user_input, top_k=3)
        
        # Clean the content before building context
        cleaned_docs = [self.clean_content(doc) for doc in relevant_docs]
        
        # Filter for Baby Bear Book content if this is a pediatric query
        if is_pediatric_query or any(term in user_input.lower() for term in ['neonate', 'newborn', 'infant', 'child']):
            # Prioritize Baby Bear Book and Section 01 content
            baby_bear_docs = [doc for doc in cleaned_docs if any(term in doc.lower() for term in ['kkh', 'section 01', 'baby bear', 'pediatric', 'child'])]
            if baby_bear_docs:
                context = "\n\n".join(baby_bear_docs[:3])  # Use Baby Bear content
            else:
                context = "\n\n".join(cleaned_docs[:2])  # Fallback to general content
        elif is_emergency_query:
            # Emergency queries get priority Section 01 content - limited
            context = "\n\n".join(cleaned_docs[:2])  # Only top 2 results
        else:
            # General nursing queries get balanced content - minimal
            context = cleaned_docs[0] if cleaned_docs else ""  # Only top result
        
        # Limit context length to prevent token overflow
        if len(context) > 800:  # Keep context under 800 characters
            context = context[:800] + "..."
        
        # Add conversation history for context if available
        if chat_history and len(chat_history) > 1:
            recent_messages = chat_history[-3:]  # Last 3 messages for context
            conversation_context = "\n\nRecent conversation:\n"
            for msg in recent_messages:
                role = "Nurse" if msg["role"] == "user" else "Sarah"
                conversation_context += f"{role}: {msg['content'][:150]}...\n"
            context = conversation_context + "\n\nKnowledge base context:\n" + context
        
        # Enhanced system message based on query type
        if is_pediatric_query or any(term in user_input.lower() for term in ['neonate', 'newborn', 'infant', 'child']):
            enhanced_context = f"""PRIORITY CONTEXT - KKH Baby Bear Book Pediatric Guidelines:
            
{context}

This query is about pediatric/neonatal care. Please prioritize information from the KKH Baby Bear Book and provide age-appropriate clinical values and protocols."""
        elif is_emergency_query:
            enhanced_context = f"""PRIORITY CONTEXT - KKH Baby Bear Book Section 01 Medical Emergencies:
            
{context}

This query appears to be about pediatric emergencies or critical care. Please prioritize information from the KKH Baby Bear Book Section 01 while also providing practical nursing guidance."""
        else:
            enhanced_context = context
        
        # Query LLM with enhanced context
        response = self.query_llm(user_input, enhanced_context)
        
        # Clean response to ensure only bullet points
        response = self.clean_response(response)
        
        # For follow-up questions, if response is not nursing-related, provide a specific fallback
        if is_follow_up:
            nursing_check = any(term in response.lower() for term in [
                'temperature', 'vital signs', 'medication', 'treatment', 'assessment',
                'monitor', 'nursing', 'patient', 'clinical', 'medical', 'emergency'
            ])
            
            # Check for incomplete or nonsense responses
            incomplete_indicators = [
                'call for _', '• call for', 'not available', '• not available',
                'specific clinical guidance not available', len(response.strip()) < 20,
                '____' in response, 'fill in' in response.lower()
            ]
            
            is_incomplete = any(indicator in response.lower() if isinstance(indicator, str) else indicator for indicator in incomplete_indicators)
            
            if not nursing_check or is_incomplete:
                # Provide a nursing-specific fallback based on the question type
                if any(term in user_input.lower() for term in ['abcde', 'assessment']):
                    response = """• Airway - Check for obstruction or stridor
• Breathing - Assess respiratory rate, effort, and oxygen saturation
• Circulation - Monitor heart rate, blood pressure, and capillary refill
• Disability - Assess consciousness level using AVPU or GCS
• Exposure - Check for rashes, injuries, or temperature"""
                elif any(term in user_input.lower() for term in ['vital signs', 'normal ranges', 'heart rate', 'neonatal', 'neonate', 'newborn heart rate', 'normal heart rate range for neonate']):
                    if any(neonatal_term in user_input.lower() for neonatal_term in ['neonate', 'neonatal', 'newborn']):
                        response = """• Neonatal heart rate: 120-180 beats per minute (KKH Baby Bear Book)
• Neonatal respiratory rate: 40-60 breaths per minute  
• Neonatal blood pressure: 60-80 mmHg systolic
• Temperature: 36.5-37.5°C (axillary measurement preferred)"""
                    else:
                        response = """• Heart rate varies by age: newborn 120-180, infant 80-140, child 70-120 bpm
• Respiratory rate: newborn 40-60, infant 24-38, child 18-30 breaths/min
• Blood pressure increases with age and size
• Temperature normal range: 36.5-37.5°C (97.7-99.5°F)"""
                elif any(term in user_input.lower() for term in ['medication', 'drug', 'dose']):
                    response = """• Always verify patient identity with two identifiers
• Check medication name, dose, route, and timing
• Calculate pediatric doses based on weight (mg/kg)
• Verify allergies and contraindications before administration"""
                elif any(term in user_input.lower() for term in ['call for help', 'immediate help', 'when should i call', 'when to call']):
                    response = """• Any acute change in consciousness or responsiveness
• Significant vital sign abnormalities for age
• Difficulty breathing or signs of respiratory distress
• Signs of shock: poor perfusion, altered mental state, cool extremities
• Seizures or abnormal movements
• Severe pain or distress that cannot be managed
• Any situation where you feel uncertain about patient safety"""
                elif any(term in user_input.lower() for term in ['when to escalate', 'escalate']):
                    response = """• Deteriorating vital signs despite interventions
• New or worsening symptoms
• Patient or family expressing serious concerns
• Any change that makes you worried about patient safety
• When clinical indicators suggest need for higher level of care"""
                else:
                    response = """• Monitor patient closely for any changes
• Document all observations and interventions
• Communicate concerns to medical team
• Follow hospital protocols and guidelines"""
        
        return response
    
    def handle_calculation_request(self, user_input: str) -> str:
        """Handle calculation requests in a conversational way"""
        if 'fluid' in user_input.lower():
            # Try to extract weight from input
            weight_match = re.search(r'(\d+(?:\.\d+)?)\s*kg', user_input.lower())
            if weight_match:
                weight = float(weight_match.group(1))
                calc_result = self.calculate_fluid_requirements(weight)
                return f"""Great question! Let me calculate those fluid requirements for your {weight} kg patient. 💧

**Here's what I found:**
• **Daily requirement:** {calc_result['daily_ml']:.0f} mL ({calc_result['daily_liters']:.1f} L)
• **Hourly rate:** {calc_result['hourly_ml']:.1f} mL/hr

*I used the Holliday-Segar method for this calculation*

**Clinical reminders:** 🏥
- Please adjust these numbers based on the patient's clinical condition, fever, or ongoing losses
- Don't forget to monitor electrolytes and renal function regularly
- Consider whether you need maintenance fluids vs. replacement therapy
- Always double-check with the physician's orders

Is there anything specific about this patient's fluid management you'd like me to help explain? I'm happy to dive deeper into the clinical considerations! 😊"""
            else:
                return """I'd love to help you calculate fluid requirements! 💧 I just need to know the patient's weight in kg first.

For example, you could ask: *"Calculate fluid requirements for 25 kg patient"*

**Here's a quick reminder of the Holliday-Segar Method:**
• First 10 kg: 100 mL/kg/day (4 mL/kg/hr)
• Next 10 kg: 50 mL/kg/day (2 mL/kg/hr)  
• Each kg >20 kg: 20 mL/kg/day (1 mL/kg/hr)

What's the weight of your patient? I'll calculate it right away! 🤗"""
        
        return self.query_llm(user_input, "")

def create_new_chat_session() -> str:
    """Create a new chat session and return its ID"""
    session_id = str(uuid.uuid4())
    st.session_state.chat_sessions[session_id] = {
        'name': 'New Chat',
        'messages': [
            {
                "role": "assistant",
                "content": "KKH Nursing Assistant ready. Ask your clinical question."
            }
        ],
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    return session_id

def delete_chat_session(session_id: str):
    """Delete a chat session"""
    if session_id in st.session_state.chat_sessions and len(st.session_state.chat_sessions) > 1:
        del st.session_state.chat_sessions[session_id]
        # If we deleted the current session, switch to the first available session
        if st.session_state.current_session_id == session_id:
            st.session_state.current_session_id = list(st.session_state.chat_sessions.keys())[0]
            st.session_state.messages = st.session_state.chat_sessions[st.session_state.current_session_id]['messages']

def rename_chat_session(session_id: str, new_name: str):
    """Rename a chat session"""
    if session_id in st.session_state.chat_sessions:
        st.session_state.chat_sessions[session_id]['name'] = new_name

def switch_chat_session(session_id: str):
    """Switch to a different chat session"""
    if session_id in st.session_state.chat_sessions:
        # Save current messages to current session
        st.session_state.chat_sessions[st.session_state.current_session_id]['messages'] = st.session_state.messages
        # Switch to new session
        st.session_state.current_session_id = session_id
        st.session_state.messages = st.session_state.chat_sessions[session_id]['messages']

def get_chat_preview(messages: List[Dict]) -> str:
    """Get a preview of the chat for display in sidebar"""
    user_messages = [msg['content'] for msg in messages if msg['role'] == 'user']
    if user_messages:
        preview = user_messages[0]
        return preview[:40] + "..." if len(preview) > 40 else preview
    return "New Chat"

def generate_contextual_prompts(messages: List[Dict]) -> List[str]:
    """Generate contextual follow-up prompts based on chat history"""
    if len(messages) < 2:
        return []
    
    # Get the last assistant response to check if it's nursing-related
    last_assistant_message = None
    for msg in reversed(messages):
        if msg['role'] == 'assistant':
            last_assistant_message = msg['content'].lower()
            break
    
    if not last_assistant_message:
        return []
    
    # Check if the last response is actually nursing-related
    nursing_indicators = [
        'temperature', 'vital signs', 'blood pressure', 'heart rate', 'respiratory',
        'medication', 'treatment', 'symptoms', 'assessment', 'monitor', 'nursing',
        'patient', 'clinical', 'medical', 'emergency', 'pediatric', 'paediatric',
        'infection', 'hygiene', 'ppe', 'fluid', 'dose', 'mg/kg', 'oxygen',
        'breathing', 'consciousness', 'distress', 'poisoning', 'overdose'
    ]
    
    # If the response doesn't contain nursing content, don't show follow-up questions
    if not any(indicator in last_assistant_message for indicator in nursing_indicators):
        return []
    
    # Check if response contains non-nursing content that should exclude follow-ups
    non_nursing_indicators = [
        'favorite color', 'python script', 'programming', 'coding', 'write a',
        'personal preference', 'opinion', 'not available', 'exercise', 'solution'
    ]
    
    if any(indicator in last_assistant_message for indicator in non_nursing_indicators):
        return []
    
    # Get the last few messages for context
    recent_messages = messages[-4:] if len(messages) >= 4 else messages
    
    # Extract keywords from recent user messages
    user_messages = [msg['content'].lower() for msg in recent_messages if msg['role'] == 'user']
    if not user_messages:
        return []
    
    last_user_message = user_messages[-1]
    
    # Define contextual prompt categories based on keywords
    prompt_categories = {
        'critical_illness': {
            'keywords': ['critical', 'emergency', 'urgent', 'deteriorating', 'shock', 'unconscious', 'collapse'],
            'prompts': [
                "What are the ABCDE assessment steps?",
                "How do I recognize pediatric shock?",
                "When should I call for immediate help?",
                "What are pediatric early warning signs?",
                "How to prepare for emergency response?"
            ]
        },
        'pediatric_cpr': {
            'keywords': ['cpr', 'resuscitation', 'cardiac arrest', 'not breathing', 'no pulse'],
            'prompts': [
                "What's the compression rate for children?",
                "How deep should chest compressions be?",
                "What's the ventilation ratio for pediatric CPR?",
                "When do I use AED on children?",
                "How to check for pulse in infants?"
            ]
        },
        'poisoning': {
            'keywords': ['poison', 'overdose', 'ingestion', 'toxic', 'paracetamol', 'acetaminophen'],
            'prompts': [
                "What's the antidote for paracetamol overdose?",
                "How do I calculate N-acetylcysteine dose?",
                "When is activated charcoal indicated?",
                "What are contraindications for charcoal?",
                "How to assess severity of poisoning?"
            ]
        },
        'vital_signs': {
            'keywords': ['vital signs', 'heart rate', 'blood pressure', 'temperature', 'respiratory rate', 'oxygen'],
            'prompts': [
                "What are normal ranges for this age?",
                "How often should I monitor vitals?",
                "What indicates abnormal findings?",
                "When to escalate vital sign concerns?",
                "How to document vital signs properly?"
            ]
        },
        'medication': {
            'keywords': ['medication', 'drug', 'dose', 'administration', 'calculate', 'mg/kg'],
            'prompts': [
                "How do I calculate pediatric doses?",
                "What are the five rights of medication?",
                "How to check for drug allergies?",
                "What's the maximum safe dose?",
                "How to monitor for side effects?"
            ]
        },
        'infection_control': {
            'keywords': ['infection', 'isolation', 'ppe', 'hand hygiene', 'mrsa', 'contact precautions'],
            'prompts': [
                "What PPE do I need for this case?",
                "How long should hand hygiene take?",
                "When to use contact precautions?",
                "How to properly don and doff PPE?",
                "What are standard precautions?"
            ]
        },
        'fluid_management': {
            'keywords': ['fluid', 'dehydration', 'iv', 'maintenance', 'replacement', 'ml/kg'],
            'prompts': [
                "How to calculate maintenance fluids?",
                "What are signs of dehydration?",
                "When to start IV fluids?",
                "How to monitor fluid balance?",
                "What fluid type should I use?"
            ]
        },
        'respiratory': {
            'keywords': ['breathing', 'respiratory', 'oxygen', 'wheeze', 'stridor', 'asthma'],
            'prompts': [
                "How to assess breathing difficulty?",
                "When to give supplemental oxygen?",
                "What are signs of respiratory distress?",
                "How to position for optimal breathing?",
                "When to prepare for intubation?"
            ]
        }
    }
    
    # Find matching categories
    matching_prompts = []
    for category, data in prompt_categories.items():
        if any(keyword in last_user_message for keyword in data['keywords']):
            # Add 2-3 most relevant prompts from this category
            matching_prompts.extend(data['prompts'][:3])
    
    # If no specific matches, provide general follow-up prompts
    if not matching_prompts:
        general_prompts = [
            "Can you explain this in more detail?",
            "What are the key nursing considerations?",
            "How do I document this properly?",
            "What complications should I watch for?",
            "When should I escalate to the doctor?"
        ]
        matching_prompts = general_prompts[:3]
    
    # Remove duplicates and limit to 6 prompts max
    unique_prompts = list(dict.fromkeys(matching_prompts))
    return unique_prompts[:6]

def main():
    st.set_page_config(
        page_title="KKH Nursing Assistant",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2d5aa0 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .logo-section {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.5rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #1f4e79;
        background-color: #f8f9fa;
    }
    .calculator-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #bee5eb;
    }
    
    /* Conversational chat styling */
    .stChatMessage {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #1f4e79 0%, #2d5aa0 100%);
        color: white;
        margin-left: 20%;
    }
    
    .stChatMessage[data-testid="assistant-message"] {
        background: linear-gradient(135deg, #e8f4f8 0%, #d1ecf1 100%);
        margin-right: 20%;
        border-left: 4px solid #1f4e79;
    }
    
    /* Chat input styling */
    .stChatInputContainer {
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 25px;
        padding: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Chat history styling */
    
    .chat-session-name {
        font-weight: 600 !important;
        color: #1f4e79 !important;
        font-size: 0.9rem !important;
        margin-bottom: 4px !important;
    }
    
    .chat-session-preview {
        font-size: 0.75rem !important;
        color: #6c757d !important;
        font-style: italic !important;
        opacity: 0.8 !important;
    }
    
    .chat-history-header {
        background: linear-gradient(135deg, #1f4e79 0%, #2d5aa0 100%) !important;
        color: white !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        margin-bottom: 15px !important;
        box-shadow: 0 2px 6px rgba(31, 78, 121, 0.3) !important;
    }
    
    .new-chat-btn {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
        border: none !important;
        border-radius: 50% !important;
        width: 35px !important;
        height: 35px !important;
        box-shadow: 0 2px 6px rgba(40, 167, 69, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .new-chat-btn:hover {
        transform: scale(1.1) !important;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4) !important;
    }
    
    .action-btn {
        background: linear-gradient(135deg, #17a2b8 0%, #20c997 100%) !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 4px 8px !important;
        color: white !important;
        font-size: 0.8rem !important;
        transition: all 0.3s ease !important;
    }
    
    .action-btn:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 6px rgba(23, 162, 184, 0.3) !important;
    }
    
    .delete-btn {
        background: linear-gradient(135deg, #dc3545 0%, #e74c3c 100%) !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 4px 8px !important;
        color: white !important;
        font-size: 0.8rem !important;
        transition: all 0.3s ease !important;
    }
    
    .delete-btn:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 6px rgba(220, 53, 69, 0.3) !important;
    }
    
    /* Sidebar improvements */
    .sidebar .stSelectbox > div > div {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
        border-radius: 8px !important;
        border: 1px solid #dee2e6 !important;
    }
    
    .sidebar .stButton > button {
        background: linear-gradient(135deg, #1f4e79 0%, #2d5aa0 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
    }
    
    .sidebar .stButton > button:hover {
        background: linear-gradient(135deg, #2d5aa0 0%, #3d6bb0 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(31, 78, 121, 0.3) !important;
    }
    
    /* Text input styling for rename */
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
        border: 2px solid #dee2e6 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1f77b4 !important;
        box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.1) !important;
    }
    
    /* Improve spacing and typography */
    .sidebar h2, .sidebar h3 {
        color: #1f4e79 !important;
        font-weight: 600 !important;
        margin-bottom: 15px !important;
    }
    
    .sidebar .stMarkdown {
        color: #495057 !important;
        line-height: 1.5 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with KKH Logo
    col1, col2 = st.columns([1, 4])
    
    with col1:
        # Display KKH Logo
        try:
            st.image("KKH Logo.jpg", width=120)
        except:
            st.markdown("🏥", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="main-header">
            <h1 style="color: white; margin: 0; font-size: 2.5rem;">KKH Nursing Assistant Chatbot</h1>
            <p style="color: #e6f3ff; margin: 0; font-size: 1.1rem;">Your intelligent companion for nursing protocols, calculations, and education</p>
            <p style="color: #b3d9ff; margin: 0; font-size: 0.9rem; font-style: italic;">KK Women's and Children's Hospital • Baby Bear Book Integration</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        with st.spinner("Initializing nursing knowledge base..."):
            st.session_state.chatbot = NursingChatbot()
            # Force reload to ensure we get the latest Section 01 content
            st.session_state.chatbot.force_reload_knowledge_base()
        
    # Initialize chat sessions management
    if 'chat_sessions' not in st.session_state:
        st.session_state.chat_sessions = {
            'default': {
                'name': 'New Chat',
                'messages': [
                    {
                        "role": "assistant",
                        "content": "KKH Nursing Assistant ready. Ask your clinical question."
                    }
                ],
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        }
    
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = 'default'
    
    # Initialize messages from current session
    if 'messages' not in st.session_state:
        st.session_state.messages = st.session_state.chat_sessions[st.session_state.current_session_id]['messages']
    
    # Sync current messages with active session
    st.session_state.chat_sessions[st.session_state.current_session_id]['messages'] = st.session_state.messages
    
    # Sidebar for navigation and chat history
    with st.sidebar:
        st.header("🔧 Navigation")
        
        # Initialize page selection
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "💬 Chat"
        
        # Main navigation for sidebar
        page_selection = st.radio(
            "Select a section:",
            ["💬 Chat", "🧮 Calculators", "🎯 Quiz"],
            horizontal=False,
            index=["💬 Chat", "🧮 Calculators", "🎯 Quiz"].index(st.session_state.current_page) if st.session_state.current_page in ["💬 Chat", "🧮 Calculators", "🎯 Quiz"] else 0
        )
        
        # Chat History Management (only show on chat page)
        if page_selection == "💬 Chat":
            st.markdown("---")
            
            # Chat history header with new chat button - styled
            st.markdown("""
            <div class="chat-history-header">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center;">
                        <span style="font-size: 1.1rem; font-weight: 600;">💬 Chat History</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # New chat button - centered and styled
            col_center = st.columns([1, 2, 1])
            with col_center[1]:
                if st.button("➕ New Chat", key="new_chat_btn", help="Start a new conversation", use_container_width=True):
                    new_session_id = create_new_chat_session()
                    switch_chat_session(new_session_id)
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Display chat sessions with enhanced styling
            sessions_to_display = list(st.session_state.chat_sessions.items())
            sessions_to_display.sort(key=lambda x: x[1]['created_at'], reverse=True)
            
            for session_id, session_data in sessions_to_display:
                # Session container with enhanced styling
                is_current = session_id == st.session_state.current_session_id
                container_class = "chat-session-active" if is_current else "chat-session-inactive"
                
                st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
                
                # Session info and actions in a cleaner layout
                session_name = session_data['name']
                if len(session_name) > 30:
                    display_name = session_name[:30] + "..."
                else:
                    display_name = session_name
                
                # Main session button
                col1, col2, col3 = st.columns([6, 1, 1])
                
                with col1:
                    if st.button(f"📄 {display_name}", key=f"select_{session_id}", 
                               help=f"Created: {session_data['created_at']}", 
                               use_container_width=True):
                        switch_chat_session(session_id)
                        st.rerun()
                    
                    # Show preview of conversation
                    preview = get_chat_preview(session_data['messages'])
                    if preview != "New Chat":
                        st.markdown(f'<div class="chat-session-preview">💭 {preview}</div>', unsafe_allow_html=True)
                
                with col2:
                    # Rename button with better styling
                    if st.button("✏️", key=f"rename_{session_id}", help="Rename this chat"):
                        st.session_state[f'rename_mode_{session_id}'] = True
                        st.rerun()
                
                with col3:
                    # Delete button (only if more than one session exists)
                    if len(st.session_state.chat_sessions) > 1:
                        if st.button("🗑️", key=f"delete_{session_id}", help="Delete this chat"):
                            delete_chat_session(session_id)
                            st.rerun()
                
                # Rename mode with better styling
                if st.session_state.get(f'rename_mode_{session_id}', False):
                    st.markdown("<br>", unsafe_allow_html=True)
                    new_name = st.text_input(
                        "Enter new name:", 
                        value=session_data['name'],
                        key=f"rename_input_{session_id}",
                        max_chars=50,
                        placeholder="Give this chat a meaningful name..."
                    )
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("💾 Save", key=f"save_rename_{session_id}", use_container_width=True):
                            if new_name.strip():
                                rename_chat_session(session_id, new_name.strip())
                            st.session_state[f'rename_mode_{session_id}'] = False
                            st.rerun()
                    with col_cancel:
                        if st.button("❌ Cancel", key=f"cancel_rename_{session_id}", use_container_width=True):
                            st.session_state[f'rename_mode_{session_id}'] = False
                            st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("---")
        
        # Clinical scenarios section
        st.subheader("🏥 Clinical Scenarios")
        st.write("**Practice with realistic situations:**")
        
        scenarios = [
            "Recognising a critically ill infant",
            "Paediatric medication error prevention", 
            "Isolation precautions for infectious child",
            "Paediatric emergency response protocols",
            "Drug poisoning in toddler",
            "Paracetamol overdose management",
            "Paediatric shock recognition",
            "Respiratory distress in child"
        ]
        
        selected_scenario = st.selectbox("Select a scenario:", scenarios, key="sidebar_scenario")
        if st.button("Explore Scenario", key="sidebar_explore"):
            scenario_prompt = f"Walk me through a clinical scenario involving: {selected_scenario}"
            st.session_state.messages.append({
                "role": "user",
                "content": scenario_prompt
            })
            # Force page to Chat and trigger response generation
            page_selection = "💬 Chat"
        
        # Update current page
        st.session_state.current_page = page_selection
        

        
    
    # Main content area - display based on page selection
    if st.session_state.current_page == "💬 Chat":
        # Chat interface - full width
        col1, col2 = st.columns([6, 1])
        
        with col2:
            if st.button("🗑️ Clear Chat", help="Start a fresh conversation"):
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": "KKH Nursing Assistant ready. Ask your clinical question."
                    }
                ]
                st.rerun()
        
        with col1:
            st.markdown("### 💬 Chat with Sarah - Your KKH Nursing Assistant")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Show follow-up prompts after assistant responses (for existing conversations)
        if len(st.session_state.messages) > 1 and st.session_state.messages[-1]["role"] == "assistant":
            follow_up_prompts = generate_contextual_prompts(st.session_state.messages)
            
            if follow_up_prompts:
                st.markdown("### 💡 Suggested Follow-up Questions")
                
                # Create columns for prompt buttons
                num_prompts = len(follow_up_prompts)
                if num_prompts <= 3:
                    cols = st.columns(num_prompts)
                    for i, prompt in enumerate(follow_up_prompts):
                        with cols[i]:
                            if st.button(prompt, key=f"followup_display_{i}_{len(st.session_state.messages)}", use_container_width=True):
                                # Add the selected prompt as a user message
                                st.session_state.messages.append({
                                    "role": "user", 
                                    "content": prompt
                                })
                                st.rerun()
                else:
                    # If more than 3 prompts, create rows of 3
                    rows = (num_prompts + 2) // 3
                    for row in range(rows):
                        cols = st.columns(3)
                        for col_idx in range(3):
                            prompt_idx = row * 3 + col_idx
                            if prompt_idx < num_prompts:
                                with cols[col_idx]:
                                    if st.button(follow_up_prompts[prompt_idx], key=f"followup_display_{prompt_idx}_{len(st.session_state.messages)}", use_container_width=True):
                                        # Add the selected prompt as a user message
                                        st.session_state.messages.append({
                                            "role": "user",
                                            "content": follow_up_prompts[prompt_idx]
                                        })
                                        st.rerun()
        
        # Check if we need to generate a response for the last user message
        if len(st.session_state.messages) > 1 and st.session_state.messages[-1]["role"] == "user":
            # Get the last user message
            last_user_message = st.session_state.messages[-1]["content"]
            
            # Ensure current session is synchronized
            st.session_state.chat_sessions[st.session_state.current_session_id]['messages'] = st.session_state.messages
            
            # Generate response with conversation history
            with st.chat_message("assistant"):
                with st.spinner("Sarah is thinking... 🤔"):
                    response = st.session_state.chatbot.process_query(last_user_message, st.session_state.messages)
                st.markdown(response)
            
            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Sync the updated messages back to the session
            st.session_state.chat_sessions[st.session_state.current_session_id]['messages'] = st.session_state.messages
            st.rerun()
        
        # Chat input
        if prompt := st.chat_input("Hi Sarah! I need help with... 💬"):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Auto-rename session if it's the first user message and session name is still "New Chat"
            current_session = st.session_state.chat_sessions[st.session_state.current_session_id]
            if current_session['name'] == 'New Chat':
                # Count user messages to see if this is the first one
                user_messages = [msg for msg in st.session_state.messages if msg['role'] == 'user']
                if len(user_messages) == 1:  # This is the first user message
                    # Create a smart name from the first message
                    smart_name = prompt[:30] + "..." if len(prompt) > 30 else prompt
                    rename_chat_session(st.session_state.current_session_id, smart_name)
            
            st.rerun()
    
    elif st.session_state.current_page == "🧮 Calculators":
        # Calculator Section
        st.header("🧮 Clinical Calculators")
        st.write("Professional clinical calculation tools for nursing practice")
        
        # Create tabs for different calculators
        calc_tabs = st.tabs(["💧 Fluid Requirements", "💊 Medication Dosage", "🩸 IV Flow Rate", "📏 BMI Calculator", "🌡️ Paracetamol Dose", "❤️ Vital Signs Check"])
        
        with calc_tabs[0]:
            st.subheader("💧 Fluid Requirements Calculator")
            st.write("Calculate pediatric fluid requirements using the Holliday-Segar method")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                weight = st.number_input("Patient weight (kg)", min_value=0.1, max_value=200.0, value=10.0, step=0.1, key="fluid_weight")
                if st.button("Calculate Fluid Requirements", key="calc_fluid_main"):
                    calc_result = st.session_state.chatbot.calculate_fluid_requirements(weight)
                    with col2:
                        st.success(f"""
                        **Daily Requirement:**
                        {calc_result['daily_ml']:.0f} mL ({calc_result['daily_liters']:.1f} L)
                        
                        **Hourly Rate:**
                        {calc_result['hourly_ml']:.1f} mL/hr
                        
                        **Weight:** {weight} kg
                        """)
        
        with calc_tabs[1]:
            st.subheader("💊 Medication Dosage Calculator")
            st.write("Calculate medication doses based on patient weight")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                med_weight = st.number_input("Patient weight (kg)", min_value=0.1, max_value=200.0, value=10.0, step=0.1, key="med_weight_main")
                dose_per_kg = st.number_input("Dose per kg (mg/kg)", min_value=0.1, max_value=100.0, value=10.0, step=0.1, key="dose_per_kg_main")
                if st.button("Calculate Dose", key="calc_dose_main"):
                    total_dose = med_weight * dose_per_kg
                    with col2:
                        st.success(f"""
                        **Total Dose:** {total_dose:.1f} mg
                        
                        **Calculation:**
                        {med_weight} kg × {dose_per_kg} mg/kg = {total_dose:.1f} mg
                        """)
        
        with calc_tabs[2]:
            st.subheader("🩸 IV Flow Rate Calculator")
            st.write("Calculate intravenous infusion flow rates")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                volume = st.number_input("Volume (mL)", min_value=1, max_value=2000, value=100, step=1, key="volume_main")
                time_hours = st.number_input("Time (hours)", min_value=0.5, max_value=24.0, value=1.0, step=0.5, key="time_main")
                if st.button("Calculate Flow Rate", key="calc_flow_main"):
                    flow_rate = volume / time_hours
                    with col2:
                        st.success(f"""
                        **Flow Rate:** {flow_rate:.1f} mL/hr
                        
                        **Calculation:**
                        {volume} mL ÷ {time_hours} hours = {flow_rate:.1f} mL/hr
                        """)
        
        with calc_tabs[3]:
            st.subheader("📏 BMI Calculator")
            st.write("Calculate Body Mass Index and category")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                height_cm = st.number_input("Height (cm)", min_value=30, max_value=250, value=150, step=1, key="height_main")
                bmi_weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=50.0, step=0.1, key="bmi_weight_main")
                if st.button("Calculate BMI", key="calc_bmi_main"):
                    height_m = height_cm / 100
                    bmi = bmi_weight / (height_m ** 2)
                    
                    if bmi < 18.5:
                        category = "Underweight"
                        color = "blue"
                    elif bmi < 25:
                        category = "Normal weight"
                        color = "green"
                    elif bmi < 30:
                        category = "Overweight"
                        color = "orange"
                    else:
                        category = "Obese"
                        color = "red"
                    
                    with col2:
                        st.success(f"""
                        **BMI:** {bmi:.1f}
                        
                        **Category:** {category}
                        
                        **Height:** {height_cm} cm
                        **Weight:** {bmi_weight} kg
                        """)
        
        with calc_tabs[4]:
            st.subheader("🌡️ Paracetamol Dose Calculator")
            st.write("Calculate safe paracetamol dosing for pediatric patients")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                para_weight = st.number_input("Patient weight (kg)", min_value=1.0, max_value=100.0, value=10.0, step=0.1, key="para_weight_main")
                age_months = st.number_input("Age (months)", min_value=1, max_value=216, value=12, step=1, key="age_main")
                if st.button("Calculate Paracetamol Dose", key="calc_para_main"):
                    min_dose = para_weight * 10
                    max_dose = para_weight * 15
                    daily_max = para_weight * 60
                    
                    with col2:
                        st.success(f"""
                        **Single Dose Range:**
                        {min_dose:.0f} - {max_dose:.0f} mg
                        
                        **Frequency:** Every 4-6 hours
                        
                        **Daily Maximum:** {daily_max:.0f} mg
                        
                        **Weight:** {para_weight} kg
                        **Age:** {age_months} months
                        """)
            
            st.warning("⚠️ Always verify dosing with current prescribing guidelines and consider patient-specific factors.")
        
        with calc_tabs[5]:
            st.subheader("❤️ Vital Signs Assessment")
            st.write("Check vital signs against age-appropriate normal ranges")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                vs_age = st.selectbox("Age Group", [
                    "Neonate", "Infant (1m-1yr)", "Toddler (1-2yr)", 
                    "Young child (2-7yr)", "Older child (7-12yr)", "Adult"
                ], key="vs_age_main")
                
                hr_input = st.number_input("Heart Rate (bpm)", min_value=20, max_value=220, value=80, step=1, key="hr_main")
                rr_input = st.number_input("Respiratory Rate (/min)", min_value=5, max_value=80, value=20, step=1, key="rr_main")
                sbp_input = st.number_input("Systolic BP (mmHg)", min_value=30, max_value=200, value=100, step=1, key="sbp_main")
                
                if st.button("Check Vital Signs", key="calc_vitals_main"):
                    ranges = {
                        "Neonate": {"HR": (120, 180), "RR": (40, 60), "SBP": (60, 80)},
                        "Infant (1m-1yr)": {"HR": (110, 160), "RR": (30, 40), "SBP": (70, 90)},
                        "Toddler (1-2yr)": {"HR": (100, 150), "RR": (25, 35), "SBP": (80, 95)},
                        "Young child (2-7yr)": {"HR": (95, 140), "RR": (25, 30), "SBP": (90, 110)},
                        "Older child (7-12yr)": {"HR": (80, 120), "RR": (20, 25), "SBP": (100, 120)},
                        "Adult": {"HR": (60, 100), "RR": (12, 20), "SBP": (90, 140)}
                    }
                    
                    normal_range = ranges[vs_age]
                    hr_status = "✅ Normal" if normal_range["HR"][0] <= hr_input <= normal_range["HR"][1] else "⚠️ Abnormal"
                    rr_status = "✅ Normal" if normal_range["RR"][0] <= rr_input <= normal_range["RR"][1] else "⚠️ Abnormal"
                    sbp_status = "✅ Normal" if normal_range["SBP"][0] <= sbp_input <= normal_range["SBP"][1] else "⚠️ Abnormal"
                    
                    with col2:
                        st.info(f"""
                        **Assessment for {vs_age}:**
                        
                        **HR:** {hr_input} bpm {hr_status}
                        Normal: {normal_range["HR"][0]}-{normal_range["HR"][1]} bpm
                        
                        **RR:** {rr_input} /min {rr_status}
                        Normal: {normal_range["RR"][0]}-{normal_range["RR"][1]} /min
                        
                        **SBP:** {sbp_input} mmHg {sbp_status}
                        Normal: {normal_range["SBP"][0]}-{normal_range["SBP"][1]} mmHg
                        """)
    
    elif st.session_state.current_page == "🎯 Quiz":
        # Combined Quiz Section
        st.header("🎯 Knowledge Assessment")
        st.write("Test your nursing knowledge with general concepts and KKH-specific protocols")
        
        # Create tabs for different quiz types
        quiz_tabs = st.tabs(["📚 General Nursing", "🏥 KKH Baby Bear Book"])
        
        with quiz_tabs[0]:
            st.subheader("📚 General Nursing Knowledge Quiz")
            st.write("Test your knowledge of fundamental nursing concepts")
            
            general_quiz_questions = [
                {
                    "question": "How long should alcohol-based hand rub be applied?",
                    "options": ["10-15 seconds", "20-30 seconds", "45-60 seconds"],
                    "correct": 1,
                    "explanation": "Alcohol-based hand rub should be applied for 20-30 seconds to be effective."
                },
                {
                    "question": "What is the first step in the nursing process?",
                    "options": ["Planning", "Assessment", "Implementation"],
                    "correct": 1,
                    "explanation": "Assessment is the first step in the nursing process, gathering comprehensive patient data."
                },
                {
                    "question": "Normal adult respiratory rate per minute:",
                    "options": ["8-12", "12-20", "20-30"],
                    "correct": 1,
                    "explanation": "Normal adult respiratory rate is 12-20 breaths per minute at rest."
                },
                {
                    "question": "Which of the five rights of medication administration includes patient identification?",
                    "options": ["Right Drug", "Right Patient", "Right Dose"],
                    "correct": 1,
                    "explanation": "Right Patient requires verifying patient identity using two identifiers before medication administration."
                },
                {
                    "question": "What type of isolation is required for MRSA?",
                    "options": ["Airborne", "Contact", "Droplet"],
                    "correct": 1,
                    "explanation": "MRSA requires contact precautions including gowns and gloves."
                },
                {
                    "question": "Normal adult heart rate range at rest:",
                    "options": ["50-80 bpm", "60-100 bpm", "80-120 bpm"],
                    "correct": 1,
                    "explanation": "Normal adult resting heart rate is 60-100 beats per minute."
                },
                {
                    "question": "Which position is best for a patient with difficulty breathing?",
                    "options": ["Supine", "Fowler's position", "Prone"],
                    "correct": 1,
                    "explanation": "Fowler's position (sitting upright) promotes lung expansion and eases breathing."
                },
                {
                    "question": "What is the normal range for adult blood pressure?",
                    "options": ["90/60 - 120/80 mmHg", "100/70 - 140/90 mmHg", "110/80 - 150/100 mmHg"],
                    "correct": 0,
                    "explanation": "Normal adult blood pressure is less than 120/80 mmHg, with 90/60-120/80 being the optimal range."
                },
                {
                    "question": "How often should bed-bound patients be repositioned to prevent pressure ulcers?",
                    "options": ["Every 4 hours", "Every 2 hours", "Every 6 hours"],
                    "correct": 1,
                    "explanation": "Bed-bound patients should be repositioned every 2 hours to prevent pressure ulcer development."
                },
                {
                    "question": "What is the universal precaution for all patient care?",
                    "options": ["Wearing gloves only", "Hand hygiene", "Using masks"],
                    "correct": 1,
                    "explanation": "Hand hygiene is the single most important universal precaution to prevent infection transmission."
                }
            ]
            
            if 'current_general_quiz' not in st.session_state:
                st.session_state.current_general_quiz = 0
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                if st.session_state.current_general_quiz < len(general_quiz_questions):
                    quiz = general_quiz_questions[st.session_state.current_general_quiz]
                    
                    st.write(f"**Question {st.session_state.current_general_quiz + 1} of {len(general_quiz_questions)}**")
                    st.write(f"**{quiz['question']}**")
                    
                    # Initialize answer state for this question
                    answer_key = f"general_answer_{st.session_state.current_general_quiz}"
                    if answer_key not in st.session_state:
                        st.session_state[answer_key] = None
                    
                    selected = st.radio("Choose your answer:", ["Select an option"] + quiz["options"], key=f"general_quiz_{st.session_state.current_general_quiz}")
                    
                    # Only show submit button if user has selected an option
                    if selected != "Select an option":
                        col_a, col_b, col_c = st.columns([1, 1, 1])
                        with col_a:
                            if st.button("Submit Answer", key="submit_general"):
                                if quiz["options"].index(selected) == quiz["correct"]:
                                    st.success("✅ Correct!")
                                else:
                                    st.error("❌ Incorrect!")
                                st.info(f"**Explanation:** {quiz['explanation']}")
                                st.session_state[answer_key] = selected
                        
                        # Show Next button only after answer is submitted
                        if st.session_state[answer_key] is not None:
                            with col_b:
                                if st.button("Next Question", key="next_general"):
                                    st.session_state.current_general_quiz += 1
                                    # Show balloons when completing the last question
                                    if st.session_state.current_general_quiz == len(general_quiz_questions):
                                        st.balloons()
                                    st.rerun()
                        
                        with col_c:
                            if st.button("Skip Question", key="skip_general"):
                                st.session_state.current_general_quiz += 1
                                st.rerun()
                else:
                    st.success("🎉 General Quiz completed!")
                    # Balloons are shown when user clicks "Next Question" on the last question
                    if st.button("Restart General Quiz", key="restart_general"):
                        st.session_state.current_general_quiz = 0
                        st.rerun()
            
            with col2:
                # Progress tracking
                progress = st.session_state.current_general_quiz / len(general_quiz_questions)
                st.metric("Progress", f"{st.session_state.current_general_quiz}/{len(general_quiz_questions)}")
                st.progress(progress)
                
                st.info("""
                **Quiz Topics:**
                • Hand hygiene protocols
                • Nursing process steps
                • Vital signs assessment
                • Medication safety
                • Infection control
                """)
        
        with quiz_tabs[1]:
            st.subheader("🏥 KKH Baby Bear Book Quiz")
            st.write("Test your knowledge of KKH-specific protocols and procedures")
            
            kkh_quiz_questions = [
                {
                    "question": "What is the normal heart rate range for a neonate?",
                    "options": ["100-150 bpm", "120-180 bpm", "80-120 bpm"],
                    "correct": 1,
                    "explanation": "Normal neonatal heart rate is 120-180 bpm according to KKH Baby Bear Book."
                },
                {
                    "question": "At what systolic BP is hypotension defined in neonates?",
                    "options": ["<50 mmHg", "<60 mmHg", "<70 mmHg"],
                    "correct": 1,
                    "explanation": "Hypotension in neonates is defined as systolic BP <60 mmHg per KKH guidelines."
                },
                {
                    "question": "What is the compression-to-ventilation ratio for pediatric CPR with ≥2 rescuers?",
                    "options": ["30:2", "15:2", "5:1"],
                    "correct": 1,
                    "explanation": "For children ≤12 years with ≥2 rescuers, use 15:2 compression-to-ventilation ratio."
                },
                {
                    "question": "What is the activated charcoal dose for pediatric poisoning?",
                    "options": ["0.5 g/kg", "1 g/kg", "2 g/kg"],
                    "correct": 1,
                    "explanation": "Activated charcoal dose is 1 g/kg (max 50g if <12 years) for pediatric poisoning cases."
                },
                {
                    "question": "What is the N-acetylcysteine dose in Phase 1 of paracetamol poisoning treatment?",
                    "options": ["100 mg/kg", "200 mg/kg", "300 mg/kg"],
                    "correct": 1,
                    "explanation": "Phase 1 NAC dose is 200 mg/kg over 4 hours for paracetamol poisoning."
                },
                {
                    "question": "What is the normal respiratory rate for a 2-year-old child?",
                    "options": ["12-20 /min", "25-35 /min", "40-60 /min"],
                    "correct": 1,
                    "explanation": "Normal respiratory rate for toddlers (1-2 years) is 25-35 breaths per minute."
                },
                {
                    "question": "What is the minimum compression depth for pediatric CPR in children?",
                    "options": ["At least 1/3 chest depth", "At least 1/2 chest depth", "At least 2 inches"],
                    "correct": 0,
                    "explanation": "For children, compress at least 1/3 the depth of the chest (about 2 inches/5cm)."
                },
                {
                    "question": "What is the maximum single dose of paracetamol for a 20kg child?",
                    "options": ["200mg", "300mg", "400mg"],
                    "correct": 1,
                    "explanation": "Maximum single dose is 15mg/kg, so for 20kg child: 20 × 15 = 300mg."
                },
                {
                    "question": "In pediatric ABCDE assessment, what does 'D' stand for?",
                    "options": ["Disability/Neurological", "Dehydration", "Drug history"],
                    "correct": 0,
                    "explanation": "In ABCDE assessment, 'D' stands for Disability/Neurological assessment including consciousness level."
                },
                {
                    "question": "What is the normal systolic blood pressure for a 5-year-old child?",
                    "options": ["70-90 mmHg", "90-110 mmHg", "110-130 mmHg"],
                    "correct": 1,
                    "explanation": "Normal systolic BP for 2-7 year olds is approximately 90-110 mmHg according to KKH guidelines."
                }
            ]
            
            if 'current_kkh_quiz' not in st.session_state:
                st.session_state.current_kkh_quiz = 0
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                if st.session_state.current_kkh_quiz < len(kkh_quiz_questions):
                    quiz = kkh_quiz_questions[st.session_state.current_kkh_quiz]
                    
                    st.write(f"**Question {st.session_state.current_kkh_quiz + 1} of {len(kkh_quiz_questions)}**")
                    st.write(f"**{quiz['question']}**")
                    
                    # Initialize answer state for this question
                    answer_key = f"kkh_answer_{st.session_state.current_kkh_quiz}"
                    if answer_key not in st.session_state:
                        st.session_state[answer_key] = None
                    
                    selected = st.radio("Choose your answer:", ["Select an option"] + quiz["options"], key=f"kkh_quiz_{st.session_state.current_kkh_quiz}")
                    
                    # Only show submit button if user has selected an option
                    if selected != "Select an option":
                        col_a, col_b, col_c = st.columns([1, 1, 1])
                        with col_a:
                            if st.button("Submit Answer", key="submit_kkh"):
                                if quiz["options"].index(selected) == quiz["correct"]:
                                    st.success("✅ Correct!")
                                else:
                                    st.error("❌ Incorrect!")
                                st.info(f"**Explanation:** {quiz['explanation']}")
                                st.session_state[answer_key] = selected
                        
                        # Show Next button only after answer is submitted
                        if st.session_state[answer_key] is not None:
                            with col_b:
                                if st.button("Next Question", key="next_kkh"):
                                    st.session_state.current_kkh_quiz += 1
                                    # Show balloons when completing the last question
                                    if st.session_state.current_kkh_quiz == len(kkh_quiz_questions):
                                        st.balloons()
                                    st.rerun()
                        
                        with col_c:
                            if st.button("Skip Question", key="skip_kkh"):
                                st.session_state.current_kkh_quiz += 1
                                st.rerun()
                else:
                    st.success("🎉 KKH Baby Bear Quiz completed!")
                    # Balloons are shown when user clicks "Next Question" on the last question
                    if st.button("Restart KKH Quiz", key="restart_kkh"):
                        st.session_state.current_kkh_quiz = 0
                        st.rerun()
            
            with col2:
                # Progress tracking
                progress = st.session_state.current_kkh_quiz / len(kkh_quiz_questions)
                st.metric("Progress", f"{st.session_state.current_kkh_quiz}/{len(kkh_quiz_questions)}")
                st.progress(progress)
                
                st.info("""
                **KKH Topics:**
                • Pediatric vital signs
                • Emergency protocols
                • CPR guidelines
                • Poisoning management
                • Drug calculations
                """)
    
    elif st.session_state.current_page == "💡 Quick Prompts":
        # Quick Prompts Section
        st.header("💡 Quick Access Prompts")
        st.write("Click any prompt to quickly ask the chatbot common questions")
        
        prompt_categories = {
            "🩺 Assessment": [
                "Show me vital signs assessment for different age groups",
                "How do I perform ABCDE assessment?",
                "What are red flags in pediatric patients?",
                "Explain pediatric pain assessment scales",
                "How do I assess fluid status in children?"
            ],
            "🚨 Emergency": [
                "Walk me through pediatric CPR steps",
                "How do I manage anaphylaxis in children?",
                "What is the approach to drug poisoning?",
                "Show me sepsis recognition and management",
                "Explain pediatric shock management"
            ],
            "💊 Medications": [
                "Calculate paracetamol dose for 15kg child",
                "Show me N-acetylcysteine protocol",
                "What are the five rights of medication administration?",
                "Explain pediatric medication safety checks",
                "How do I prepare IV medications safely?"
            ],
            "🧮 Calculations": [
                "Calculate fluid requirements for 25kg patient",
                "How do I calculate medication dosages?",
                "Show me IV flow rate calculations",
                "Explain BMI calculation and interpretation",
                "How do I calculate drip rates?"
            ]
        }
        
        tabs = st.tabs(["🩺 Assessment", "🚨 Emergency", "💊 Medications", "🧮 Calculations"])
        
        for i, (category, prompts) in enumerate(prompt_categories.items()):
            with tabs[i]:
                st.subheader(f"{category}")
                st.write(f"**Common {category.split()[1].lower()} questions:**")
                
                for j, prompt in enumerate(prompts):
                    if st.button(prompt, key=f"prompt_main_{category}_{j}"):
                        # Switch to chat and add the prompt
                        st.session_state.current_page = "💬 Chat"
                        st.session_state.messages.append({
                            "role": "user",
                            "content": prompt
                        })
                        st.rerun()
    
if __name__ == "__main__":
    main()