# 🚀 Deployment Guide

This guide will help you deploy your Cancellable Content Checker to make it publicly accessible.

## 🌐 Option 1: Vercel Deployment (Recommended)

### Step 1: Prepare for GitHub

1. **Initialize Git repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Cancellable Content Checker"
   ```

2. **Create GitHub repository:**
   - Go to [GitHub.com](https://github.com) and create a new repository
   - Name it something like `cancellable-content-checker`
   - Make it public so you can deploy it for free

3. **Push to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/cancellable-content-checker.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Vercel

1. **Sign up for Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with your GitHub account

2. **Import your project:**
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect it's a Python project

3. **Configure environment variables:**
   - In Vercel dashboard, go to your project settings
   - Add environment variable: `GROQ_API_KEY` = your actual Groq API key
   - Optional: `STREAMLIT_SERVER_PORT` = 8501

4. **Deploy:**
   - Click "Deploy"
   - Wait for deployment to complete
   - Your app will be available at `https://your-project-name.vercel.app`

## 🌐 Option 2: Streamlit Community Cloud

### Step 1: Prepare Repository

1. **Push to GitHub** (same as Step 1 above)

2. **Update requirements.txt** (already done)

### Step 2: Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**

2. **Sign in with GitHub**

3. **Create new app:**
   - Repository: `YOUR_USERNAME/cancellable-content-checker`
   - Branch: `main`
   - Main file: `app.py`

4. **Add secrets:**
   - In Streamlit Cloud dashboard
   - Add secret: `GROQ_API_KEY` = your actual Groq API key

5. **Deploy:**
   - Click "Deploy"
   - Your app will be available at `https://your-app-name.streamlit.app`

## 🔧 Option 3: Railway (Alternative)

1. **Sign up at [railway.app](https://railway.app)**

2. **Connect GitHub repository**

3. **Set environment variables:**
   - `GROQ_API_KEY` = your actual Groq API key

4. **Deploy automatically**

## 📋 Pre-Deployment Checklist

- [ ] Remove your actual API key from `.streamlit/secrets.toml`
- [ ] Test locally with environment variables
- [ ] Ensure all dependencies are in `requirements.txt`
- [ ] Check `.gitignore` excludes sensitive files
- [ ] Update README.md with deployment instructions

## 🔐 Security Notes

- **Never commit API keys** to Git
- **Use environment variables** for production
- **Set up proper secrets management** in your deployment platform
- **Consider rate limiting** for production use

## 🎯 Post-Deployment

1. **Test your live app** thoroughly
2. **Share the public URL** with friends
3. **Monitor usage** and API costs
4. **Set up monitoring** if needed

## 🆘 Troubleshooting

### Common Issues:

1. **Import errors:** Ensure all dependencies are in `requirements.txt`
2. **API key issues:** Check environment variables are set correctly
3. **Timeout errors:** Some deployment platforms have time limits
4. **Memory issues:** Large dependencies like Playwright may need special configuration

### Getting Help:

- Check deployment platform logs
- Test locally first
- Verify all environment variables are set
- Check the deployment platform's documentation

## 🎉 Success!

Once deployed, you'll have a public URL like:
- Vercel: `https://cancellable-content-checker.vercel.app`
- Streamlit: `https://cancellable-content-checker.streamlit.app`
- Railway: `https://cancellable-content-checker.railway.app`

Share this URL with your friends to showcase your Cancellable Content Checker!
