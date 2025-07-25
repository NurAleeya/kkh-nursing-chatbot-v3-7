# KKH Nursing Chatbot - Quick Start Guide

## 🚀 Quick Start (5 minutes)

### 1. Local Development
```bash
# Windows
run_local.bat

# Manual setup
pip install -r requirements.txt
streamlit run app.py
```
Access at: http://localhost:8501

### 2. Deploy to Fly.io
```bash
# Install Fly CLI and login
fly auth login

# Deploy
fly deploy

# Open in browser
fly open
```

## 📋 Key Features

### Information Retrieval
- **Hand Hygiene Protocol**: WHO 5 moments, proper technique
- **Medication Safety**: Five rights of administration
- **Infection Control**: Standard and transmission-based precautions
- **Emergency Procedures**: CPR, first aid protocols

### Clinical Calculations
- **Fluid Requirements**: Holliday-Segar method for pediatrics
- **Drug Dosages**: Weight-based medication calculations
- **IV Flow Rates**: Infusion rate calculations

### Educational Tools
- **Interactive Quizzes**: Knowledge assessment with feedback
- **Clinical Scenarios**: Case-based learning exercises
- **Quick References**: Instant access to protocols

## 🔧 Technical Details

- **LLM Model**: Phi-2 via LM Studio (http://10.175.5.70:1234)
- **Embeddings**: all-MiniLM-L6-v2 for semantic search
- **Framework**: Streamlit for web interface
- **Vector DB**: FAISS for knowledge retrieval
- **Deployment**: Fly.io with auto-scaling

## 💡 Usage Examples

### Ask Questions
- "What is the hand hygiene protocol?"
- "How do I calculate fluid requirements?"
- "Show me medication administration guidelines"

### Perform Calculations
- "Calculate fluid requirements for 15kg patient"
- "What is the dosage for paracetamol?"

### Educational Activities
- Complete quizzes in the sidebar
- Explore clinical scenarios
- Test knowledge with Q&A

## 🆘 Troubleshooting

### Common Issues
1. **LLM Connection**: Verify http://10.175.5.70:1234 is accessible
2. **Slow Performance**: Check memory allocation with `fly scale memory 2048`
3. **Deployment Issues**: Run `fly logs` to check for errors

### Support Commands
```bash
fly status          # Check app status
fly logs            # View application logs
fly ssh console     # Access container
python verify.py    # Test functionality
```

## 📞 Support
- Technical issues: Check logs and restart with `fly restart`
- Content updates: Contact KKH Nursing Education
- Medical accuracy: Verify with current institutional policies

---
**Ready to use!** 🎉 The chatbot is designed specifically for KKH nursing staff to improve efficiency and patient care quality.
