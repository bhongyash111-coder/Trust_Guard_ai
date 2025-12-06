# TrustGuard AI - Deployment Guide

Your TrustGuard AI application consists of:
- **Frontend**: Next.js 16 React app (TypeScript)
- **Backend**: FastAPI Python server
- **APIs**: NVIDIA LLM + Firecrawl integration

---

## Quick Deployment Options

### Option 1: Vercel (Recommended for Frontend)
**Vercel** is perfect for Next.js apps and offers free tier with great performance.

#### Frontend Deployment Steps:
1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Click "New Project" → Select your GitHub repo
4. Configure:
   - **Root Directory**: `trustguard-frontend`
   - **Build Command**: `npm run build`
   - **Start Command**: `npm start`
5. Add Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-api.com
   ```
6. Deploy with one click

---

### Option 2: Render (For Backend + Frontend)
**Render** offers free tier for both web services and cron jobs.

#### Backend Deployment (Render):
1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Create new Web Service
4. Configure:
   - **Repository**: Your GitHub repo
   - **Root Directory**: `trustguard-backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
5. Add Environment Variables:
   ```
   LLM_API_KEY=your_api_key_here
   FIRECRAWL_API_KEY=your_firecrawl_key_here
   FIRECRAWL_TIMEOUT=30
   ```
6. Deploy

#### Frontend Deployment (Render):
1. Create another Web Service
2. Configure:
   - **Root Directory**: `trustguard-frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`
3. Add Environment:
   ```
   NEXT_PUBLIC_API_URL=https://your-render-backend.onrender.com
   ```

---

### Option 3: Docker + Railway / Heroku (Professional)
**Railway** or **Heroku** for containerized deployment.

#### Create Docker Files:

**trustguard-backend/Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**trustguard-frontend/Dockerfile**:
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json .
COPY --from=builder /app/node_modules ./node_modules

CMD ["npm", "start"]
```

#### Deploy to Railway:
1. Install Railway CLI
2. Run:
   ```powershell
   railway login
   railway init
   railway up
   ```

---

### Option 4: AWS (Scalable but more complex)

#### Frontend → CloudFront + S3:
1. Build Next.js: `npm run build && npm start`
2. Upload to S3 bucket
3. Create CloudFront distribution
4. Set API gateway for backend

#### Backend → EC2 or ECS:
1. Create EC2 instance (t3.micro free tier)
2. Install Python, dependencies
3. Run FastAPI with supervisor/systemd
4. Use RDS for MongoDB (if needed)

---

## Step-by-Step: Recommended (Vercel + Render)

### Step 1: Prepare GitHub Repository
```powershell
cd C:\Users\roshn\TrustGuard-AI
git init
git add .
git commit -m "Initial commit: TrustGuard AI"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/TrustGuard-AI.git
git push -u origin main
```

### Step 2: Deploy Backend to Render
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. New Web Service → Connect GitHub repo
4. Settings:
   - Name: `trustguard-api`
   - Root Directory: `trustguard-backend`
   - Runtime: Python 3.11
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
5. Environment Variables tab, add:
   ```
   LLM_API_KEY=your_nvidia_key
   FIRECRAWL_API_KEY=your_firecrawl_key
   FIRECRAWL_TIMEOUT=30
   ```
6. Create Web Service

**Your backend URL will be**: `https://trustguard-api.onrender.com`

### Step 3: Deploy Frontend to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Import → GitHub → Select your repo
3. Framework: Next.js
4. Root Directory: `trustguard-frontend`
5. Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://trustguard-api.onrender.com
   ```
6. Deploy

**Your frontend URL will be**: `https://trustguard-ai.vercel.app`

### Step 4: Update Frontend API Configuration
Edit `trustguard-frontend/app/utils/api.ts`:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8081';
```

Redeploy to apply changes.

---

## Environment Variables Checklist

### Backend (.env)
```
LLM_API_KEY=nvapi-xxx
FIRECRAWL_API_KEY=fc-xxx
FIRECRAWL_TIMEOUT=30
```

### Frontend (.env.local or Vercel dashboard)
```
NEXT_PUBLIC_API_URL=https://your-backend-api.com
```

---

## Post-Deployment Checklist

- [ ] Test landing page at `/welcome`
- [ ] Test analyze page at `/analyze`
- [ ] Enter test job posting and click "Analyze Job"
- [ ] Verify API responses come from backend
- [ ] Check console for CORS errors
- [ ] Monitor backend logs on Render dashboard
- [ ] Set up error tracking (Sentry recommended)

---

## Troubleshooting

### CORS Errors
Add to `trustguard-backend/app/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://trustguard-ai.vercel.app", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Timeouts
Increase timeout in Render:
- Settings → Timeout: 120s

### Port Issues
- Render automatically assigns PORT env var
- Use `os.getenv('PORT', '8000')` in backend

---

## Cost Estimation

| Service | Free Tier | Paid |
|---------|-----------|------|
| Vercel | ✓ Up to 100 deployments/day | ~$20/mo |
| Render | ✓ Up to 750 hours/month | ~$7/mo |
| Railway | ✓ $5 credits/month | Pay-as-you-go |
| AWS | ✓ EC2 t3.micro + S3 | ~$5-50/mo |

**Recommended**: Vercel (Free) + Render (Free) = **$0/month** to start

---

## Monitoring & Logs

**Vercel**: Dashboard → Deployments → Logs
**Render**: Services → Logs

Setup error tracking:
```bash
npm install @sentry/nextjs
npm install @sentry/fastapi
```

---

Need help with any specific platform? Let me know!
