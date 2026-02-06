
export interface WikiArticle {
    slug: string
    title: string
    category: "Guide" | "Features" | "Concepts" | "FAQ"
    description: string
    content: string
}

export const WIKI_ARTICLES: WikiArticle[] = [
    {
        slug: "getting-started",
        title: "InvestLens 入门指南",
        category: "Guide",
        description: "快速了解 InvestLens 的核心功能和使用方法。",
        content: `
# InvestLens 入门指南

欢迎来到 **InvestLens** —— 您的下一代智能投资助手。

## 什么是 InvestLens?

InvestLens 是一个集成了多模态 AI 模型的投资分析平台。它不仅仅是一个看盘软件，更是一个能像专业分析师一样"思考"的智能体。

## 核心功能

1. **AI 共识分析 (Consensus Analysis)**
   - 我们同时运行多个 AI "人格"（多头与空头）对同一资产进行辩论。
   - 最终由一个 "法官" 模型综合各方观点，给出客观的分析报告。

2. **全市场支持**
   - **A股/港股/美股**: 只要输入代码，我们就能通过 AkShare 和 Yahoo Finance 获取数据。
   - **实时行情**: 价格变动秒级更新。

3. **自选列表 (Watchlist)**
   - 点击任何股票页面的⭐️图标加入关注。
   - 在左侧菜单随时查看您的投资组合概览。

## 下一步

- 尝试在搜索栏输入 \`NVDA\` 或 \`600519\` 查看分析。
- 阅读 [量化模式说明](/wiki/quant-mode) 了解高级功能。
        `
    },
    {
        slug: "consensus-engine",
        title: "多重人格辩论引擎",
        category: "Concepts",
        description: "深入了解 AI 是如何产生客观分析的。",
        content: `
# 多重人格辩论引擎

传统的 AI 往往会产生幻觉或只给出一个模棱两可的答案。InvestLens 采用了独特的 **"辩论-裁决"** 架构来解决这个问题。

## 工作原理

### 1. 🐂 The Bull (多头)
- **任务**: 寻找所有买入的理由。
- **关注点**: 增长潜力、技术突破、市场情绪、宏观顺风。

### 2. 🐻 The Bear (空头)
- **任务**: 寻找所有做空的理由。
- **关注点**: 估值过高、竞争风险、供应链问题、宏观逆风。

### 3. ⚖️ The Judge (法官)
- **任务**: 听取双方陈述，结合实时数据，做出裁决。
- **输出**: 一个包含置信度评分 (Confidence Score) 的最终报告。

这种机制迫使 AI 考虑对立观点，从而显著减少偏见，提高分析的实用性。
        `
    },
    {
        slug: "quant-mode",
        title: "量化模式 (Quant Mode)",
        category: "Features",
        description: "解锁针对专业交易者的各种高级工具。",
        content: `
# 量化模式 (Quant Mode)

量化模式是为有经验的交易者设计的。开启此模式将解锁更激进、更专业的功能。

## 如何开启

前往 **Settings (设置)** 页面，找到 "Enable Quant Mode" 开关并开启。

## 专属功能

### 1. 结构化交易计划
在分析报告中，AI 将不再模棱两可，而是被强制要求输出：
- **Action**: 明确的 BUY/SELL/HOLD 建议。
- **Entry Zone**: 具体买入价格区间。
- **Stop Loss**: 严格的止损位。

### 2. AI 毒舌评测 (High Risk)
- 在 **自选列表** 页面解锁。
- AI 这次化身为无情的对冲基金经理，对您的持仓进行"毁灭性"打击。
- **警告**: 此模式不提供安慰，只提供基于数据的残酷真相。

## 风险提示

量化模式下的建议仅供参考。AI 说明的任何"交易计划"都不构成财务建议。请自行承担交易风险。
        `
    },
    {
        slug: "data-privacy",
        title: "数据隐私与安全",
        category: "FAQ",
        description: "我们要如何处理您的数据？",
        content: `
# 数据隐私说明

InvestLens 遵循 **"Local First"** (本地优先) 的设计理念。

## API Key 存储
- 您的 OpenAI/DeepSeek API Key **仅存储在您的浏览器本地 (Local Storage)**。
- 它们**永远不会**发送到我们的服务器数据库。
- 只有在您发起分析请求的那一刻，Key 才会被发送到 LLM 提供商。

## 自选列表
- 您的自选列表数据存储在本地文件系统 (Local JSON Config)。
- 这是一个单用户桌面应用架构，您的数据完全掌握在自己手中。

## 外部请求
- 为了获取行情，应用会直接请求 Yahoo Finance 和 AkShare (GitHub) 的接口。
        `
    }
]
