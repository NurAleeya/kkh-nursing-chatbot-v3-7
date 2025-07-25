#!/bin/bash

# KKH Nursing Chatbot Deployment Script for Fly.io

echo "🏥 KKH Nursing Chatbot - Fly.io Deployment"
echo "=========================================="

# Check if fly CLI is installed
if ! command -v fly &> /dev/null; then
    echo "❌ Fly CLI is not installed. Please install it first:"
    echo "   https://fly.io/docs/getting-started/installing-flyctl/"
    exit 1
fi

# Check if user is logged in
if ! fly auth whoami &> /dev/null; then
    echo "🔐 Please log in to Fly.io first:"
    fly auth login
fi

# Create the app if it doesn't exist
echo "📱 Setting up Fly.io application..."
if ! fly apps list | grep -q "kkh-nursing-chatbot"; then
    echo "Creating new Fly.io app..."
    fly apps create kkh-nursing-chatbot --org personal
else
    echo "App already exists, proceeding with deployment..."
fi

# Deploy the application
echo "🚀 Deploying to Fly.io..."
fly deploy

# Open the application
echo "🌐 Opening application in browser..."
fly open

echo "✅ Deployment complete!"
echo ""
echo "📊 Useful commands:"
echo "   fly logs          - View application logs"
echo "   fly status        - Check application status"
echo "   fly ssh console   - SSH into the container"
echo "   fly scale count 1 - Ensure at least 1 machine is running"
echo ""
echo "🔗 Application URL: https://kkh-nursing-chatbot.fly.dev"
