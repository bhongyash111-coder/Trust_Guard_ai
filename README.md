# TrustGuard AI 🛡️

**AI-Powered Scam Detection & Risk Analysis**

TrustGuard AI is an advanced tool designed to analyze job postings, messages, and websites instantly. It detects scams, hidden fees, and phishing attempts using powerful AI models, providing you with a detailed risk analysis to keep you safe.

## 🚀 Live Demo
[**Try TrustGuard AI**](https://trust-guard-ai-taupe.vercel.app/analyze)

## 📺 Video Explanation
[![Watch the Demo](https://img.youtube.com/vi/9h4Fr6SAoy4/hqdefault.jpg)](https://youtu.be/9h4Fr6SAoy4)
> *Click the image above to watch the video with sound on YouTube.*

## ✨ Features
- **Scam Detection**: Analyze text or URLs for potential fraud.
- **Risk Analysis**: Get a trust score and detailed breakdown of risks.
- **Company Verification**: Cross-reference company details with known databases.
- **Instant Feedback**: Real-time analysis powered by AI.

## 📸 Screenshots

![Dashboard](assets/preview_1.png)
*Intuitive Dashboard for checking scams*

![Analysis Result](assets/preview_2.png)
*Detailed Risk Analysis Report*

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 16
- **Library**: React 19
- **Styling**: Tailwind CSS 4
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB
- **Scraping**: FireCrawl, BeautifulSoup4
- **AI/LLM**: Google Gemini (via API)

## 📦 Installation

### Prerequisites
- Node.js (v18+)
- Python (v3.9+)
- MongoDB instance
- Google Gemini API Key
- FireCrawl API Key

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd trustguard-backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (create `.env`):
   ```env
   MONGODB_URI=your_mongodb_uri
   GEMINI_API_KEY=your_gemini_key
   FIRECRAWL_API_KEY=your_firecrawl_key
   ```
4. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd trustguard-frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## 🤝 Contribution
Contributions are welcome! Please feel free to submit a Pull Request.
