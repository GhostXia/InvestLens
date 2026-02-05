# InvestLens 

> **Intelligent Investment Decision Support System**
>
> *(智能投资决策支持系统)*
>
> *Real-time Market Data, Multi-Model AI Consensus, and Quantitative Gating.*

**InvestLens** is a modern investment analysis dashboard. It empowers individual investors by combining real-time market data, AI-driven consensus analysis, and quantitative prediction models into a single, interactive interface.

*(InvestLens 是一个现代化投资分析仪表盘。它将实时行情、AI 多视角分析和量化预测模型整合在一个交互式界面中，赋予个人投资者更强的决策能力。)*

---

## Features / 功能特性

### 1. Real-time Market Insights (实时市场洞察)
- **Sub-second Latency**: Fetches real-time price and volatility data via `yfinance` Fast Info API.
  *(毫秒级行情：通过 yfinance Fast Info 接口获取实时价格波动。)*
- **Interactive Charts**: Dynamic Area Charts built with Recharts, supporting 1M/6M/1Y/YTD timeframes.
  *(动态图表：支持多周期切换的交互式 K 线图。)*

### 2. Multi-Model Consensus Engine (多模型共识引擎)
- **AI-Driven Analysis**: Automatically invokes LLMs (OpenAI, DeepSeek) to generate professional investment reports.
  *(AI 驱动分析：自动调用大模型生成专业报告。)*
- **Structured Output**: transforms unstructured reasoning into structured data (Bullish/Bearish Thesis, Confidence Score).
  *(结构化输出：自动提取看多/看空逻辑和置信度评分。)*

### 3. Quantitative Prediction (量化预测 - Quant Mode)
- **Monte Carlo Simulation**: Projects future price paths based on historical volatility.
  *(蒙特卡洛模拟：基于历史波动率预测未来价格路径。)*
- **Safety Gating**: Advanced features are gated behind a "Quant Mode" toggle with risk disclaimers.
  *(安全门控：高级功能需开启“量化模式”并签署风险告知后可见。)*
- **Visual Confidence Bands**: Visualizes the 95% confidence interval for predictions.
  *(置信区间：可视化展示 95% 概率下的价格波动范围。)*

### 4. Local-First Security (本地优先安全)
- **BYO-API Key**: Users bring their own API keys.
- **Zero-Persistence**: Keys are stored only in `localStorage` and passed via headers. No server-side storage.
  *(零服务端存储：Key 仅存于浏览器本地，不经过后端数据库。)*

---

## Tech Stack / 技术栈

| Layer | Technology | Details |
|-------|------------|---------|
| **Frontend** | Next.js 14 | App Router, TypeScript, Shadcn UI, Tailwind CSS |
| **State** | Zustand | Persist Middleware for Settings |
| **Backend** | FastAPI | Python 3.10+, Pydantic v2, AsyncIO |
| **Data** | yfinance | Real-time & Historical Market Data |
| **Quant** | NumPy | Monte Carlo Simulation, Volatility Calculation |
| **Infra** | Docker | Docker Compose for orchestration |

---

## Quick Start (Local) / 本地快速开始

### Prerequisites (前置要求)
- **Python 3.10+**
- **Node.js 18+**
- **API Key**: OpenAI or DeepSeek (compatible format).

### 🚀 One-Click Start (Windows)
We provide a handy batch script to launch both services at once.
*(我们提供了一个快捷脚本，可同时启动前后端服务。)*

Double-click **`start_app.bat`** in the root directory.

*Note: Ensure you have run the installation steps below at least once to create the `venv` and install `node_modules`.*

### 1. Start Backend (Kernel)
```bash
cd investlens-kernel

# Create Virtual Env
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate
# Activate (Mac/Linux)
# source venv/bin/activate

# Install Deps & Run
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```
> Backend runs at: `http://localhost:8000`

### 2. Start Frontend (Web)
```bash
cd investlens-web
npm install
npm run dev
```
> Frontend runs at: `http://localhost:3000`

---

## Deployment / 部署指南

### Option 1: Docker Compose (Recommended)
This is the easiest way to spin up the entire stack (Frontend + Backend + Redis Cache).
*(这是最简单的部署方式，一键启动前端、后端和缓存服务。)*

1. **Ensure Docker is installed**.
2. **Run Compose**:
   ```bash
   docker-compose up --build -d
   ```
3. **Access**:
   - Web App: `http://localhost:3000`
   - API Docs: `http://localhost:8000/docs`

### Option 2: Manual / VPS Deployment
If you prefer to run services manually or on a standard Linux VPS (Ubuntu/Debian).

#### 1. Backend Service
```bash
# In /investlens-kernel
pip install -r requirements.txt
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
```

#### 2. Frontend Build
```bash
# In /investlens-web
npm run build
npm start
# Or use PM2
pm2 start npm --name "investlens-web" -- start
```

#### 3. Environment Variables
- **Frontend**: Create `.env.local` to override defaults if API is on a different domain.
  `NEXT_PUBLIC_API_URL=http://your-server-ip:8000`
- **Backend**: Set `REDIS_URL` if using an external Redis instance.

---

## Project Structure / 项目结构

```
./InvestLens/
├── investlens-kernel/      # Python FastAPI Backend (The "Brain")
│   ├── app/services/       # Core Logic (Market Data, Consensus)
│   ├── app/models/         # Data Schemas
│   └── main.py             # API Entrypoint
│
├── investlens-web/         # Next.js Frontend (The "Face")
│   ├── app/                # Pages & Routes
│   ├── components/         # UI Components (Charts, Dashboard)
│   └── lib/store/          # State Management
│
└── docker-compose.yml      # Container Orchestration
```

---

## Disclaimer / 免责声明
**Educational Purpose Only.** InvestLens is a demonstration of AI-assisted financial analysis. It does not constitute financial advice. Predictions are statistical estimates, not guarantees.

*(本项目仅供教育和研究使用，不构成任何投资建议。市场有风险，投资需谨慎。)*

---


