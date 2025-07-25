# KKH Nursing Chatbot

An intelligent nursing assistant chatbot designed for KK Women's and Children's Hospital, providing healthcare professionals with instant access to nursing protocols, clinical calculations, and educational resources.

## Features

### 🔍 Information Retrieval
- **Nursing Protocols**: Hand hygiene, medication administration, infection control
- **Clinical Guidelines**: Evidence-based practices and procedures
- **Emergency Procedures**: CPR, first aid, and critical care protocols
- **Medical Emergencies Section 01**: Comprehensive emergency management protocols
- **Medication Information**: Drug calculations, administration routes, safety checks

### 🧮 Clinical Calculations
- **Fluid Requirements**: Pediatric fluid calculations using Holliday-Segar method
- **Drug Dosage**: Medication dosing calculations based on weight and indication
- **IV Flow Rates**: Infusion rate calculations for various medications
- **Laboratory Values**: Reference ranges and interpretation guidelines

### 📚 Educational Support
- **Interactive Quizzes**: Knowledge assessment with instant feedback
- **Clinical Scenarios**: Case-based learning exercises
- **Best Practices**: Evidence-based nursing care guidelines
- **Continuing Education**: Regular updates on nursing protocols

## Technology Stack

- **Frontend**: Streamlit web application
- **Backend**: Python with LangChain integration
- **LLM**: Phi-2 model via LM Studio (hosted at http://10.175.5.70:1234)
- **Embeddings**: all-MiniLM-L6-v2 for semantic search
- **Vector Database**: FAISS for efficient similarity search
- **Deployment**: Fly.io platform with Docker containers

## Local Development

### Prerequisites
- Python 3.11+
- Access to LM Studio instance at http://10.175.5.70:1234

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd kkh-nursing-chatbot-v3
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Deployment on Fly.io

### Prerequisites
- Fly.io account and CLI installed
- Docker installed locally

### Deployment Steps

1. Login to Fly.io:
```bash
fly auth login
```

2. Deploy the application:
```bash
fly deploy
```

3. Open the deployed application:
```bash
fly open
```

### Environment Configuration

The application is configured to run on Fly.io with:
- **Region**: Singapore (sin)
- **Memory**: 1GB RAM
- **CPU**: 1 shared CPU
- **Port**: 8501 (Streamlit default)
- **Auto-scaling**: Enabled with minimum 0 machines

## Usage Guide

### Basic Queries
- "What is the hand hygiene protocol?"
- "Show me the five rights of medication administration"
- "How do I calculate fluid requirements for a 25kg patient?"

### Medical Emergency Queries
- "What is the anaphylaxis management protocol?"
- "Show me the cardiac arrest procedure"
- "How do I manage acute respiratory failure?"
- "What are the signs of shock and how do I treat it?"
- "What should I do for status epilepticus?"

### Calculation Examples
- "Calculate fluid requirements for 15kg child"
- "What is the dosage calculation for paracetamol?"
- "How do I calculate IV flow rates?"

### Educational Features
- Complete interactive quizzes in the sidebar
- Explore clinical scenarios for case-based learning
- Access quick reference protocols

## Knowledge Base

The chatbot includes comprehensive nursing knowledge covering:

### Protocols & Guidelines
- Hand hygiene procedures
- Medication administration (5 Rights)
- Infection control and standard precautions
- Emergency response procedures
- **Medical Emergencies Section 01**:
  - Anaphylaxis management
  - Adult cardiac arrest (Advanced Life Support)
  - Acute respiratory failure
  - Shock recognition and management
  - Seizure and status epilepticus

### Clinical Calculations
- Pediatric fluid requirements (Holliday-Segar method)
- Drug dosage calculations
- IV flow rate calculations
- Laboratory value interpretations

### Safety Features
- Emphasizes patient safety in all responses
- Recommends verification with institutional policies
- Provides evidence-based practice guidelines
- Includes appropriate precautions and contraindications

## API Integration

### LM Studio Integration
The chatbot connects to a Phi-2 model hosted via LM Studio:
- **Endpoint**: `http://10.175.5.70:1234/v1/chat/completions`
- **Model**: phi-2
- **Temperature**: 0.7 (balanced creativity and consistency)
- **Max Tokens**: 1000

### Embedding Model
Uses SentenceTransformers for semantic search:
- **Model**: all-MiniLM-L6-v2
- **Purpose**: Document similarity and knowledge retrieval
- **Vector Store**: FAISS index for efficient search

## Security Considerations

- All medical information emphasizes verification with current policies
- Responses include appropriate disclaimers about clinical decision-making
- Knowledge base focuses on established, evidence-based practices
- System encourages consultation with supervisors for complex cases

## Contributing

This project is developed as part of a Final Year Project for Republic Polytechnic in collaboration with KK Women's and Children's Hospital.

### Development Guidelines
- Follow evidence-based nursing practices
- Ensure all medical information is accurate and current
- Include appropriate safety warnings and disclaimers
- Test all clinical calculations thoroughly

## License

This project is developed for educational and healthcare improvement purposes. All medical protocols and guidelines are based on established nursing standards and should be verified with current institutional policies.

## Support

For technical issues or medical protocol updates, please contact the development team or the nursing education department at KKH.

---

**Disclaimer**: This chatbot is designed to assist healthcare professionals and should not replace clinical judgment, institutional policies, or consultation with physicians and supervisors. Always verify information with current guidelines and seek appropriate supervision for complex clinical decisions.
