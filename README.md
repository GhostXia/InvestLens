# InvestLens 🔍

[![English](https://img.shields.io/badge/Lang-English-blue)](README.md)
[![中文](https://img.shields.io/badge/Lang-中文-red)](README-zh.md)
![Visitors](https://visitor-badge.laobi.icu/badge?page_id=GhostXia.InvestLens)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Intelligent Investment Decision Support System**
>
> *Real-time Market Data, Multi-Model AI Consensus, and Quantitative Gating.*

**InvestLens** is a modern investment analysis dashboard that empowers individual investors by combining real-time market data, AI-driven consensus analysis, and quantitative prediction models into a single, interactive interface.

---

## ✨ Features

### 1. Real-time Market Insights
- **Sub-second Latency**: Fetches real-time price and volatility data via yfinance and AkShare APIs
- **Multi-Market Support**:
  - 🇺🇸 **US Stocks** — NYSE, NASDAQ (via Yahoo Finance)
  - 🇭🇰 **Hong Kong Stocks** — HKEX (via Yahoo Finance, suffix `.HK`)
  - 🇨🇳 **China A-Shares** — SSE, SZSE (via AkShare)
  - 🇨🇳 **China Funds & ETFs** — Open-end funds, ETFs (via AkShare)
  - 🌐 **Global Markets** — Major indices, commodities, forex (via Yahoo Finance)
  - ₿ **Crypto** — BTC, ETH, and major cryptocurrencies (via Yahoo Finance)
- **Interactive Charts**: Dynamic charts built with Recharts, supporting 1M/6M/1Y/YTD timeframes

### 2. Multi-Model Consensus Engine (LLM-as-a-Judge)
- **Multi-Provider Support**: Configure multiple LLM providers (OpenAI, DeepSeek, Ollama, etc.) simultaneously
- **Dual-Perspective Analysis**: Each model generates both **Bull** (optimistic) and **Bear** (skeptical) perspectives
- **Judge Synthesis**: A final "Judge" persona synthesizes all perspectives into a balanced investment report
- **Streaming Debate View**: Watch the AI debate in real-time with SSE-powered live updates
- **Context-Aware Chat**: Floating AI assistant with real-time market data context
- **Structured Output**: Extracts Bullish/Bearish Thesis, Confidence Score, and optional Trading Plan

### 3. Live Debate Visualization
- **Real-time Streaming**: Server-Sent Events (SSE) power live updates as AI agents "think"
- **Three-Tab Interface**: Switch between Bull, Bear, and Judge perspectives
- **Status Indicators**: Visual feedback showing which agent is currently analyzing
- **Toggle On/Off**: Enable debate view with the "View Debate" button

### 4. Quantitative Prediction (Quant Mode)
- **Monte Carlo Simulation**: Projects future price paths based on historical volatility
- **Visual Confidence Bands**: Displays 95% confidence interval for predictions
- **High Risk Trading Plan**: AI generates specific entry/exit prices and position sizing
- **Safety Gating**: Advanced features gated behind "Quant Mode" toggle with risk disclaimers

### 5. Local-First Security
- **BYO-API Key**: Users bring their own API keys
- **Zero-Persistence**: Keys stored only in `localStorage`, passed via headers, no server-side storage
- **Config Isolation**: Sensitive configs (`sources.json`) excluded from Git

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ Dashboard │  │  Charts  │  │ Settings │  │  DebateViewer   │ │
│  │  Header   │  │ Recharts │  │   Page   │  │  (SSE Client)   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
│                         ↓ HTTP/SSE ↓                             │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ /api/v1/quote│  │ /api/v1/     │  │ /api/v1/analyze/stream │ │
│  │ Market Data  │  │   analyze    │  │      (SSE Endpoint)    │ │
│  └──────────────┘  └──────────────┘  └────────────────────────┘ │
│                              │                                   │
│  ┌───────────────────────────┴───────────────────────────────┐  │
│  │                  Consensus Engine                          │  │
│  │   ┌───────┐    ┌───────┐    ┌───────┐                     │  │
│  │   │ Bull  │ →  │ Bear  │ →  │ Judge │ → Final Report      │  │
│  │   └───────┘    └───────┘    └───────┘                     │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ↓                   ↓                   ↓
    ┌──────────┐       ┌──────────┐       ┌──────────┐
    │ yfinance │       │  AkShare │       │  OpenAI  │
    │ US/HK/🌐 │       │ A股/基金 │       │ DeepSeek │
    │  Crypto  │       │  ETF/债  │       │  Ollama  │
    └──────────┘       └──────────┘       └──────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS |
| **UI Components** | Radix UI, Shadcn UI, Lucide Icons |
| **Charts** | Recharts |
| **State** | Zustand with Persist Middleware |
| **Backend** | FastAPI, Python 3.10+, Pydantic v2 |
| **Streaming** | Server-Sent Events (SSE), StreamingResponse |
| **Market Data** | yfinance (US), AkShare (China) |
| **AI Integration** | OpenAI SDK (compatible with DeepSeek, Ollama) |
| **Search** | DuckDuckGo Search API |
| **Infra** | Docker, Docker Compose |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- API Key: OpenAI, DeepSeek, or any OpenAI-compatible provider

### One-Click Start (Windows)
Double-click **`start_app.bat`** in the root directory.

### Manual Start

**1. Backend**
```bash
cd investlens-kernel
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

**2. Frontend**
```bash
cd investlens-web
npm install
npm run dev
```

> Backend: `http://localhost:8000` | Frontend: `http://localhost:3000`

---

## ⚙️ Configuration

### AI Model Providers
Navigate to **Settings** → **AI Model Providers** to configure:
- **Provider Name**: Display name (e.g., "GPT-4", "DeepSeek")
- **Base URL**: API endpoint (e.g., `https://api.openai.com/v1`)
- **API Key**: Your provider API key
- **Model**: Model identifier (use refresh button to fetch available models)
- **Enabled**: Toggle to include in consensus analysis

### Data Sources
Configure external data providers in **Settings** → **Data Sources** for Alpha Vantage and other APIs.

---

## 📁 Project Structure

```
./InvestLens/
├── investlens-kernel/          # Python FastAPI Backend
│   ├── app/
│   │   ├── services/
│   │   │   ├── consensus.py    # Multi-model consensus engine
│   │   │   ├── market_data.py  # Price & fundamentals
│   │   │   ├── llm_provider.py # LLM API wrapper
│   │   │   └── prompts.py      # Bull/Bear/Judge personas
│   │   ├── models/             # Pydantic schemas
│   │   └── routers/            # API route modules
│   └── main.py                 # FastAPI entrypoint
│
├── investlens-web/             # Next.js Frontend
│   ├── app/                    # Pages & Routes
│   │   ├── analysis/           # Analysis dashboard
│   │   └── settings/           # Configuration page
│   ├── components/
│   │   ├── features/analysis/
│   │   │   ├── dashboard.tsx   # Main analysis view
│   │   │   └── DebateViewer.tsx# SSE debate visualization
│   │   └── settings/
│   │       └── ModelConfigEditor.tsx
│   └── lib/store/              # Zustand state management
│
└── docker-compose.yml          # Container orchestration
```

---

## 🔒 Privacy & Security

### Data Storage
| Data Type | Storage Location | Persistence |
|-----------|-----------------|-------------|
| LLM API Keys | Browser localStorage | Local only |
| Data Source Configs | `config/sources.json` | Local file (.gitignored) |
| Analysis Results | Memory only | Session only |

### Cleanup Options
**Method 1: Settings UI**
1. Navigate to **Settings** → **Danger Zone**
2. Click **"Clear All Privacy Data"**

**Method 2: Cleanup Script**
```bash
# Windows
.\clear_privacy_data.bat

# Linux/Mac
chmod +x clear_privacy_data.sh && ./clear_privacy_data.sh
```

---

## 🐳 Deployment

### Docker Compose (Recommended)
```bash
docker-compose up --build -d
```
- Web App: `http://localhost:3000`
- API Docs: `http://localhost:8000/docs`

### Manual Deployment
See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

---

## 📦 Third-Party Libraries

### Backend (Python)
| Library | License | Description |
|---------|---------|-------------|
| [FastAPI](https://fastapi.tiangolo.com/) | MIT | Modern web framework |
| [Uvicorn](https://www.uvicorn.org/) | BSD-3 | ASGI server |
| [yfinance](https://github.com/ranaroussi/yfinance) | Apache-2.0 | Yahoo Finance data |
| [AkShare](https://akshare.akfamily.xyz/) | MIT | China financial data |
| [OpenAI Python](https://platform.openai.com/) | MIT | LLM API client |
| [Pydantic](https://docs.pydantic.dev/) | MIT | Data validation |

### Frontend (Node.js)
| Library | License | Description |
|---------|---------|-------------|
| [Next.js](https://nextjs.org/) | MIT | React framework |
| [Radix UI](https://www.radix-ui.com/) | MIT | Accessible components |
| [Tailwind CSS](https://tailwindcss.com/) | MIT | Utility-first CSS |
| [Recharts](https://recharts.org/) | MIT | React charts |
| [Zustand](https://zustand-demo.pmnd.rs/) | MIT | State management |

---

## ⚠️ Disclaimer

**Educational Purpose Only.** InvestLens is a demonstration of AI-assisted financial analysis. It does not constitute financial advice. Predictions are statistical estimates, not guarantees. Market investments carry risk.

---

## 📄 License

This project is licensed under the MIT License. See individual library licenses for third-party dependencies.
