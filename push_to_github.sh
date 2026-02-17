#!/bin/bash

# Helper script to push to GitHub and deploy to Streamlit Cloud

echo "🚀 Preparing to push to GitHub..."
echo ""

# Check if remote is already set
if git remote get-url origin &>/dev/null; then
    echo "✅ GitHub remote already configured"
    REMOTE_URL=$(git remote get-url origin)
    echo "   Remote: $REMOTE_URL"
else
    echo "📝 Setting up GitHub remote..."
    echo ""
    read -p "Enter your GitHub username: " GITHUB_USER
    read -p "Enter your repository name (or press Enter for 'stock-lookup-app'): " REPO_NAME
    REPO_NAME=${REPO_NAME:-stock-lookup-app}
    
    echo ""
    echo "Creating repository URL: https://github.com/$GITHUB_USER/$REPO_NAME"
    read -p "Is this correct? (y/n): " confirm
    
    if [ "$confirm" = "y" ]; then
        git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
        echo "✅ Remote added"
    else
        echo "❌ Cancelled. You can add the remote manually with:"
        echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
        exit 1
    fi
fi

echo ""
echo "📦 Adding all files..."
git add .

echo ""
read -p "Enter commit message (or press Enter for 'Update for Streamlit Cloud'): " COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-Update for Streamlit Cloud}

git commit -m "$COMMIT_MSG"

echo ""
echo "🌐 Pushing to GitHub..."
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Go to https://share.streamlit.io"
    echo "   2. Sign in with GitHub"
    echo "   3. Click 'New app'"
    echo "   4. Select your repository: $(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')"
    echo "   5. Main file: app.py"
    echo "   6. Add your API key in Secrets:"
    echo "      FINNHUB_API_KEY = \"your_api_key_here\""
    echo "   7. Click Deploy!"
    echo ""
else
    echo ""
    echo "❌ Push failed. Make sure:"
    echo "   - You have a GitHub repository created"
    echo "   - You have push access to the repository"
    echo "   - Your GitHub credentials are configured"
fi
