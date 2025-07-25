# KKH Nursing Chatbot - Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the KKH Nursing Chatbot to Fly.io, ensuring it's accessible for healthcare professionals at KK Women's and Children's Hospital.

## Prerequisites

### Local Development Requirements
- Python 3.11 or higher
- Git (for version control)
- Internet connection
- Access to LM Studio instance at `http://10.175.5.70:1234`

### Fly.io Deployment Requirements
- Fly.io account (free tier available)
- Fly CLI installed
- Docker installed (for local testing)

## Step 1: Local Development Setup

### Windows Setup
1. Run the automated setup:
```batch
run_local.bat
```

### Manual Setup (All Platforms)
1. Clone or navigate to the project directory:
```bash
cd kkh-nursing-chatbot-v3
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate
# macOS/Linux  
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
streamlit run app.py
```

6. Access at: `http://localhost:8501`

## Step 2: Fly.io Account Setup

1. **Create Fly.io Account**:
   - Visit [https://fly.io](https://fly.io)
   - Sign up for a free account
   - Verify your email address

2. **Install Fly CLI**:
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   
   # macOS
   brew install flyctl
   
   # Linux
   curl -L https://fly.io/install.sh | sh
   ```

3. **Login to Fly.io**:
   ```bash
   fly auth login
   ```

## Step 3: Deploy to Fly.io

### Automated Deployment
1. Run the deployment script:
```bash
# Linux/macOS
chmod +x deploy.sh
./deploy.sh

# Windows (Git Bash or WSL)
bash deploy.sh
```

### Manual Deployment
1. **Initialize Fly.io App**:
   ```bash
   fly apps create kkh-nursing-chatbot --org personal
   ```

2. **Deploy the Application**:
   ```bash
   fly deploy
   ```

3. **Open the Application**:
   ```bash
   fly open
   ```

## Step 4: Post-Deployment Configuration

### Verify Deployment
1. Check application status:
```bash
fly status
```

2. View logs:
```bash
fly logs
```

3. Monitor performance:
```bash
fly dashboard
```

### Scale Application (if needed)
```bash
# Ensure at least 1 machine is running
fly scale count 1

# Scale memory if needed
fly scale memory 2048
```

## Step 5: Access and Testing

### Application URLs
- **Production**: `https://kkh-nursing-chatbot.fly.dev`
- **Local Development**: `http://localhost:8501`

### Testing Checklist
- [ ] Application loads successfully
- [ ] LLM connection works (test with a simple query)
- [ ] Knowledge base search functions properly
- [ ] Fluid calculation tools work correctly
- [ ] Quiz functionality operates as expected
- [ ] All sidebar tools are functional

### Sample Test Queries
1. **Information Retrieval**:
   - "What is the hand hygiene protocol?"
   - "Show me the five rights of medication administration"

2. **Calculations**:
   - "Calculate fluid requirements for 15kg patient"
   - "What is the Holliday-Segar method?"

3. **Educational**:
   - Complete the quiz in the sidebar
   - Try clinical scenarios

## Troubleshooting

### Common Issues

#### 1. LM Studio Connection Errors
**Problem**: Cannot connect to LM Studio at `http://10.175.5.70:1234`
**Solutions**:
- Verify LM Studio is running and accessible
- Check network connectivity to the endpoint
- Ensure firewall settings allow the connection
- Test the endpoint directly: `curl http://10.175.5.70:1234/v1/models`

#### 2. Memory Issues
**Problem**: Application crashes due to memory constraints
**Solutions**:
```bash
# Increase memory allocation
fly scale memory 2048

# Monitor memory usage
fly logs --app kkh-nursing-chatbot
```

#### 3. Slow Response Times
**Problem**: Chatbot responses are slow
**Solutions**:
- Check LM Studio performance
- Monitor Fly.io machine performance
- Consider scaling to higher performance tier

#### 4. Knowledge Base Loading Issues
**Problem**: Knowledge base fails to load
**Solutions**:
- Check application logs: `fly logs`
- Restart the application: `fly restart`
- Verify file permissions and paths

### Debug Commands
```bash
# SSH into the container
fly ssh console

# View detailed logs
fly logs --app kkh-nursing-chatbot

# Check application health
fly status --app kkh-nursing-chatbot

# Restart the application
fly restart --app kkh-nursing-chatbot
```

## Security Considerations

### Production Security
1. **Network Security**:
   - Ensure LM Studio endpoint is properly secured
   - Use HTTPS for all external communications
   - Implement proper firewall rules

2. **Data Privacy**:
   - No patient data should be stored permanently
   - Chat histories are session-based only
   - All communications are encrypted in transit

3. **Access Control**:
   - Consider implementing authentication for production use
   - Monitor usage patterns and access logs
   - Regular security updates for dependencies

## Monitoring and Maintenance

### Regular Tasks
1. **Weekly**:
   - Check application logs for errors
   - Monitor response times and performance
   - Verify LM Studio connectivity

2. **Monthly**:
   - Update Python dependencies
   - Review and update knowledge base content
   - Check Fly.io billing and usage

3. **Quarterly**:
   - Update nursing protocols based on new guidelines
   - Gather user feedback and implement improvements
   - Security audit and dependency updates

### Metrics to Monitor
- Response time to user queries
- LM Studio API success rate
- Application uptime and availability
- Memory and CPU usage patterns
- User engagement with educational features

## Scaling for Production

### Performance Optimization
1. **Caching**:
   - Implement response caching for common queries
   - Cache knowledge base search results
   - Use CDN for static assets

2. **Load Balancing**:
   ```bash
   # Scale to multiple machines
   fly scale count 3
   
   # Use higher performance machines
   fly scale vm performance-2x
   ```

3. **Database Optimization**:
   - Consider moving to a persistent vector database
   - Implement proper indexing strategies
   - Regular database maintenance

## Support and Contact

### Technical Support
- **Repository Issues**: GitHub Issues (if applicable)
- **Fly.io Support**: [https://fly.io/docs/about/support/](https://fly.io/docs/about/support/)
- **Emergency**: Contact development team

### Content Updates
- **Nursing Protocols**: Contact KKH Nursing Education Department
- **Medical Guidelines**: Verify with current institutional policies
- **Educational Content**: Collaborate with nursing staff for feedback

---

## Quick Reference Commands

```bash
# Local development
streamlit run app.py

# Deploy to Fly.io
fly deploy

# Check status
fly status

# View logs
fly logs

# Scale application
fly scale count 1

# Open in browser
fly open

# SSH into container
fly ssh console
```

This deployment guide ensures the KKH Nursing Chatbot is successfully deployed and accessible for healthcare professionals while maintaining security and performance standards.
