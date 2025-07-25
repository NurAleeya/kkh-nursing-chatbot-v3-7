# Streamlit Cloud Deployment Guide

## Prerequisites

1. **GitHub Repository**: Your code must be in a GitHub repository
2. **OpenAI API Key**: You'll need an OpenAI API key for the LLM functionality
3. **Streamlit Cloud Account**: Sign up at https://share.streamlit.io/

## Step-by-Step Deployment

### 1. Prepare Your Repository

Make sure your repository contains:
- `app.py` (main Streamlit application)
- `requirements.txt` (dependencies)
- `.streamlit/secrets.toml` (secrets template)
- All data files (`knowledge_base.pkl`, `faiss_index.pkl`)

### 2. Push to GitHub

```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 3. Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository
5. Choose the branch (usually `main`)
6. Set the main file path to `app.py`
7. Click "Deploy!"

### 4. Configure Secrets

1. After deployment, go to your app's settings
2. Click on "Secrets" in the left sidebar
3. Add your OpenAI API key:

```toml
OPENAI_API_KEY = "sk-your-actual-openai-api-key-here"
```

4. Save the secrets
5. Your app will automatically restart

## Important Notes

- **LLM Service**: The app automatically detects if it's running on Streamlit Cloud and uses OpenAI's API instead of the local LM Studio server
- **Development vs Production**: 
  - Local development: Uses local LM Studio server
  - Streamlit Cloud: Uses OpenAI API
- **Cost Considerations**: OpenAI API calls will incur costs based on usage
- **Performance**: The embedding model and FAISS index will load on startup (may take 30-60 seconds)

## Troubleshooting

### Common Issues:

1. **App won't start**: Check requirements.txt for compatibility issues
2. **LLM not responding**: Verify your OpenAI API key is correctly set in secrets
3. **Knowledge base missing**: Ensure `knowledge_base.pkl` and `faiss_index.pkl` are in the repository
4. **Memory issues**: Streamlit Cloud has memory limits; consider using lighter models if needed

### File Size Limits:

- Streamlit Cloud has file size limits
- If your `.pkl` files are too large, consider:
  - Compressing the knowledge base
  - Using cloud storage for large files
  - Regenerating embeddings on startup

## Testing Locally

Before deploying, test locally with OpenAI API:

1. Set environment variable:
   ```bash
   export OPENAI_API_KEY=your-key-here
   ```

2. Modify app.py temporarily to use OpenAI in local testing

3. Run:
   ```bash
   streamlit run app.py
   ```

## App URL

After successful deployment, your app will be available at:
`https://[your-app-name].streamlit.app/`

## Support

- Streamlit Cloud Documentation: https://docs.streamlit.io/streamlit-cloud
- OpenAI API Documentation: https://platform.openai.com/docs
