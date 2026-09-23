# Production Deployment Guide: RootLayer / AegisScan

This guide details how to publish **RootLayer** (FastAPI Backend + Next.js Frontend) online using **Render** (or Railway) for the backend and **Vercel** for the frontend.

---

## Architecture Overview

- **Frontend**: Next.js 14 deployed on **Vercel** (Global Edge CDN, automatic HTTPS, custom domains).
- **Backend API**: FastAPI deployed on **Render.com** (Python 3.11+, automatic SSL, background async workers).
- **Continuous Deployment (CI/CD)**: Connected to GitHub. Any `git push` automatically rebuilds and deploys both services.

---

## Step 1: Push Code to GitHub

1. Create a new repository on [GitHub.com](https://github.com/new) (e.g. `rootlayer` or `aegisscan`).
   *Note: Keep it Private or Public as desired, and do NOT initialize with a README (already included).*

2. Link your local repository to GitHub and push:
   ```bash
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>.git
   git push -u origin main
   ```

---

## Step 2: Deploy Backend on Render.com (Free Tier)

1. Go to [Render.com](https://dashboard.render.com/) and sign in with GitHub.
2. Click **New +** → **Web Service**.
3. Select **Build and deploy from a Git repository** and pick your newly created repository.
4. Configure the Web Service settings:
   - **Name**: `rootlayer-api` (or `aegisscan-api`)
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
5. Under **Environment Variables**, add:
   - `ENVIRONMENT` = `production`
   - `DEBUG` = `False`
   - `SECRET_KEY` = *(click "Generate" or enter a secure 32+ character string)*
   - `ADMIN_DEFAULT_EMAIL` = `admin@rootlayer.io`
   - `ADMIN_DEFAULT_PASSWORD` = *(your secure admin password)*
   - `CORS_ORIGINS` = `https://<YOUR_VERCEL_APP>.vercel.app,http://localhost:3000`
6. Click **Deploy Web Service**.
7. Once deployed, copy your live backend URL (e.g. `https://rootlayer-api.onrender.com`).

---

## Step 3: Deploy Frontend on Vercel (Free Tier)

1. Go to [Vercel.com](https://vercel.com/) and sign in with GitHub.
2. Click **Add New...** → **Project**.
3. Import your GitHub repository.
4. In the configuration screen:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: Click **Edit** and select `frontend`.
5. Under **Environment Variables**, add:
   - `NEXT_PUBLIC_API_URL` = `https://<YOUR_BACKEND_URL>/api/v1`  
     *(e.g., `https://rootlayer-api.onrender.com/api/v1`)*
6. Click **Deploy**.
7. Vercel will build and assign you a free production URL (e.g., `https://rootlayer.vercel.app`).

---

## Step 4: Final Link Verification

1. Go back to your Render backend dashboard → **Environment**.
2. Ensure `CORS_ORIGINS` includes your live Vercel URL:
   ```
   CORS_ORIGINS = https://rootlayer.vercel.app,http://localhost:3000
   ```
3. Open your Vercel URL in your browser:
   - Run a test **Website Security Audit** on `example.com`.
   - Run a test **URL Threat Check**.
   - Verify the clean bug bounty report is generated live online!

---

## Custom Domain (Optional)

- In Vercel: Go to **Settings** → **Domains** → Add your custom domain (e.g. `rootlayer.io`).
- In Render: Go to **Settings** → **Custom Domains** → Add `api.rootlayer.io`.
- Update DNS records with your registrar (e.g. Namecheap, GoDaddy, Cloudflare) according to the instructions provided by Vercel and Render.
