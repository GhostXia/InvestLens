# InvestLens 

> **Intelligent Investment Decision Support System**
>
> *Real-time Market Data, Multi-Model AI Consensus, and Quantitative Gating.*

**InvestLens** is a modern investment analysis dashboard. It empowers individual investors by combining real-time market data, AI-driven consensus analysis, and quantitative prediction models into a single, interactive interface.

---

## ✨ Features

### 1. Real-time Market Insights
- **Sub-second Latency**: Fetches real-time price and volatility data via yfinance and AkShare APIs
- **Multi-Market Support**: US stocks (Yahoo Finance) + China A-shares & Funds (AkShare)
- **Interactive Charts**: Dynamic charts built with Recharts, supporting 1M/6M/1Y/YTD timeframes

### 2. Multi-Model Consensus Engine
- **AI-Driven Analysis**: Automatically invokes LLMs (OpenAI, DeepSeek) to generate professional investment reports
- **Context-Aware Chat**: Floating AI assistant with real-time market data context
- **Structured Output**: Extracts Bullish/Bearish Thesis and Confidence Score

### 3. Quantitative Prediction (Quant Mode)
- **Monte Carlo Simulation**: Projects future price paths based on historical volatility
- **Visual Confidence Bands**: Displays 95% confidence interval for predictions
- **Safety Gating**: Advanced features gated behind "Quant Mode" toggle with risk disclaimers

### 4. Local-First Security
- **BYO-API Key**: Users bring their own API keys
- **Zero-Persistence**: Keys stored only in `localStorage`, passed via headers, no server-side storage

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS |
| **UI Components** | Radix UI, Shadcn UI, Lucide Icons |
| **Charts** | Recharts |
| **State** | Zustand with Persist Middleware |
| **Backend** | FastAPI, Python 3.10+, Pydantic v2 |
| **Market Data** | yfinance (US), AkShare (China) |
| **AI Integration** | OpenAI SDK (compatible with DeepSeek) |
| **Search** | DuckDuckGo Search API |
| **Infra** | Docker, Docker Compose |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- API Key: OpenAI or DeepSeek (compatible format)

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

## 📦 Third-Party Libraries & Attributions

This project uses the following open-source libraries. We are grateful to their maintainers and contributors.

### Backend (Python)

| Library | License | Description | Source |
|---------|---------|-------------|--------|
| [FastAPI](https://fastapi.tiangolo.com/) | MIT | Modern web framework for APIs | [GitHub](https://github.com/tiangolo/fastapi) |
| [Uvicorn](https://www.uvicorn.org/) | BSD-3-Clause | ASGI server implementation | [GitHub](https://github.com/encode/uvicorn) |
| [yfinance](https://github.com/ranaroussi/yfinance) | Apache-2.0 | Yahoo Finance market data | [GitHub](https://github.com/ranaroussi/yfinance) |
| [AkShare](https://akshare.akfamily.xyz/) | MIT | China financial data interface | [GitHub](https://github.com/akfamily/akshare) |
| [OpenAI Python](https://platform.openai.com/) | MIT | OpenAI API client | [GitHub](https://github.com/openai/openai-python) |
| [Pandas](https://pandas.pydata.org/) | BSD-3-Clause | Data analysis library | [GitHub](https://github.com/pandas-dev/pandas) |
| [NumPy](https://numpy.org/) | BSD-3-Clause | Scientific computing | [GitHub](https://github.com/numpy/numpy) |
| [Pydantic](https://docs.pydantic.dev/) | MIT | Data validation | [GitHub](https://github.com/pydantic/pydantic) |
| [DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/) | MIT | Search API wrapper | [GitHub](https://github.com/deedy5/duckduckgo_search) |
| [HTTPX](https://www.python-httpx.org/) | BSD-3-Clause | Async HTTP client | [GitHub](https://github.com/encode/httpx) |

### Frontend (Node.js)

| Library | License | Description | Source |
|---------|---------|-------------|--------|
| [Next.js](https://nextjs.org/) | MIT | React framework | [GitHub](https://github.com/vercel/next.js) |
| [React](https://react.dev/) | MIT | UI library | [GitHub](https://github.com/facebook/react) |
| [Radix UI](https://www.radix-ui.com/) | MIT | Unstyled accessible components | [GitHub](https://github.com/radix-ui/primitives) |
| [Tailwind CSS](https://tailwindcss.com/) | MIT | Utility-first CSS | [GitHub](https://github.com/tailwindlabs/tailwindcss) |
| [Recharts](https://recharts.org/) | MIT | Chart library for React | [GitHub](https://github.com/recharts/recharts) |
| [Zustand](https://zustand-demo.pmnd.rs/) | MIT | State management | [GitHub](https://github.com/pmndrs/zustand) |
| [Lucide Icons](https://lucide.dev/) | ISC | Icon library | [GitHub](https://github.com/lucide-icons/lucide) |
| [React Markdown](https://remarkjs.github.io/react-markdown/) | MIT | Markdown renderer | [GitHub](https://github.com/remarkjs/react-markdown) |
| [next-themes](https://github.com/pacocoursey/next-themes) | MIT | Theme switching | [GitHub](https://github.com/pacocoursey/next-themes) |
| [class-variance-authority](https://cva.style/) | Apache-2.0 | CSS variant utility | [GitHub](https://github.com/joe-bell/cva) |

### UI Component Library

This project uses [shadcn/ui](https://ui.shadcn.com/) components, which are built on top of Radix UI primitives. Shadcn/ui is not a traditional npm package but a collection of reusable components that you copy into your project.

---

## 📁 Project Structure

```
./InvestLens/
├── investlens-kernel/      # Python FastAPI Backend
│   ├── app/services/       # Core Logic (Market Data, Consensus)
│   ├── app/models/         # Data Schemas
│   └── main.py             # API Entrypoint
│
├── investlens-web/         # Next.js Frontend
│   ├── app/                # Pages & Routes
│   ├── components/         # UI Components
│   └── lib/store/          # State Management
│
└── docker-compose.yml      # Container Orchestration
```

---

## 🔒 Privacy Data Cleanup

InvestLens provides multiple ways to remove all privacy-sensitive data.

### Method 1: Settings UI (Recommended)
1. Navigate to **Settings** → **Danger Zone**
2. Click **"Clear All Privacy Data"**
3. Confirm in the dialog

### Method 2: Cleanup Script
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

## ⚠️ Disclaimer

**Educational Purpose Only.** InvestLens is a demonstration of AI-assisted financial analysis. It does not constitute financial advice. Predictions are statistical estimates, not guarantees. Market investments carry risk.

---

## 📄 License

This project is licensed under the MIT License. See individual library licenses above for third-party dependencies.
