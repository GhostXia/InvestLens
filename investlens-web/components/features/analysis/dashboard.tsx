"use client"

import { useEffect, useState } from "react"
import { TickerHeader } from "@/components/features/analysis/header"
import { PriceChart } from "@/components/features/analysis/price-chart"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"
import { Brain, LineChart, MessageSquare, AlertTriangle } from "lucide-react"
import ReactMarkdown from 'react-markdown'
import { useSettingsStore } from "@/lib/store/settings"
import { getApiUrl } from "@/lib/api-config"

interface AnalysisDashboardProps {
    ticker: string
}

/**
 * AnalysisDashboard Component
 * 
 * The orchestration container for the entire analysis view.
 * 
 * Responsibilities:
 * 1. Fetches real-time market data from the backend.
 * 2. Manages loading states.
 * 3. Lays out the sub-components (Header, Charts, Consensus).
 * 
 * @param {AnalysisDashboardProps} props - The ticker to analyze
 * @returns {JSX.Element} The dashboard grid layout
 */
export function AnalysisDashboard({ ticker }: AnalysisDashboardProps) {
    const { quantModeEnabled, apiKey, baseUrl, model } = useSettingsStore()
    const [marketData, setMarketData] = useState<any>(null)
    const [analysis, setAnalysis] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [analysisLoading, setAnalysisLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true)
            setAnalysisLoading(true)
            setError(null)
            try {
                // 1. Fetch Market Data
                const quoteRes = await fetch(getApiUrl(`/api/v1/quote/${ticker}`))
                if (!quoteRes.ok) throw new Error("Failed to fetch market data")
                const quote = await quoteRes.json()
                if (quote.error) throw new Error(quote.error)
                setMarketData(quote)
                setLoading(false) // Header can show now

                // 2. Fetch Consensus Analysis
                const headers = {
                    "Content-Type": "application/json",
                    ...(apiKey && { "X-LLM-API-Key": apiKey }),
                    ...(baseUrl && { "X-LLM-Base-URL": baseUrl }),
                    ...(model && { "X-LLM-Model": model })
                }

                console.log("Sending API request with headers:", { hasApiKey: !!apiKey, hasBaseUrl: !!baseUrl, hasModel: !!model, baseUrl, model })

                const analysisRes = await fetch(getApiUrl("/api/v1/analyze"), {
                    method: "POST",
                    headers: headers,
                    body: JSON.stringify({
                        ticker: ticker,
                        focus_areas: ["Technical", "Fundamental", "Market Sentiment"]
                    })
                })

                if (analysisRes.ok) {
                    const analysisData = await analysisRes.json()
                    setAnalysis(analysisData)
                }
            } catch (err: any) {
                setError(err.message || "Unknown error")
            } finally {
                setLoading(false)
                setAnalysisLoading(false)
            }
        }

        if (ticker) {
            fetchData()
        }
    }, [ticker])

    if (error) {
        return (
            <div className="flex h-[50vh] flex-col items-center justify-center gap-4 text-destructive">
                <AlertTriangle className="h-12 w-12" />
                <h2 className="text-xl font-bold">Analysis Failed</h2>
                <p>{error}</p>
            </div>
        )
    }

    return (
        <div className="max-w-6xl mx-auto space-y-6">
            {/* 1. Market Context Header */}
            <TickerHeader
                symbol={ticker}
                isLoading={loading}
                price={marketData?.price}
                change={marketData?.change}
                changePercent={marketData?.change_percent}
                name={marketData?.name}
                currency={marketData?.currency}
            />

            {/* 2. Main Content Grid */}
            <div className="grid gap-6 md:grid-cols-3 lg:grid-cols-4">

                {/* Left Column: Chart & Visuals (Span 2 or 3) */}
                <div className="md:col-span-2 lg:col-span-3 space-y-6">
                    <PriceChart ticker={ticker} quantMode={quantModeEnabled} />

                    {/* AI Consensus Engine Output Area */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Brain className="h-5 w-5 text-purple-500" />
                                Multi-Model Consensus
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <Tabs defaultValue="consensus" className="w-full">
                                <TabsList>
                                    <TabsTrigger value="consensus">Summary</TabsTrigger>
                                    <TabsTrigger value="bull">Bullish Case</TabsTrigger>
                                    <TabsTrigger value="bear">Bearish Case</TabsTrigger>
                                </TabsList>

                                <TabsContent value="consensus" className="p-6 bg-muted/20 rounded-md mt-2 min-h-[200px] prose dark:prose-invert max-w-none">
                                    {analysisLoading ? (
                                        <div className="space-y-4">
                                            <Skeleton className="h-4 w-3/4" />
                                            <Skeleton className="h-4 w-full" />
                                            <Skeleton className="h-4 w-5/6" />
                                            <p className="text-xs text-muted-foreground animate-pulse text-center pt-4">
                                                AI Agents are analyzing market data...
                                            </p>
                                        </div>
                                    ) : (
                                        <ReactMarkdown>{analysis?.summary}</ReactMarkdown>
                                    )}
                                </TabsContent>

                                <TabsContent value="bull" className="p-6 bg-green-500/10 rounded-md mt-2 min-h-[200px] prose dark:prose-invert max-w-none">
                                    <ReactMarkdown>{analysis?.bullish_case || "No Data"}</ReactMarkdown>
                                </TabsContent>

                                <TabsContent value="bear" className="p-6 bg-red-500/10 rounded-md mt-2 min-h-[200px] prose dark:prose-invert max-w-none">
                                    <ReactMarkdown>{analysis?.bearish_case || "No Data"}</ReactMarkdown>
                                </TabsContent>
                            </Tabs>
                        </CardContent>
                    </Card>
                </div>

                {/* Right Column: Key Stats & Signals (Span 1) */}
                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">Confidence Score</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex items-center justify-center py-4">
                                {analysisLoading ? (
                                    <Skeleton className="h-16 w-16 rounded-full" />
                                ) : (
                                    <div className={`text-4xl font-bold ${(analysis?.confidence_score || 0) > 70 ? 'text-green-500' :
                                        (analysis?.confidence_score || 0) > 40 ? 'text-yellow-500' : 'text-red-500'
                                        }`}>
                                        {analysis?.confidence_score}%
                                    </div>
                                )}
                            </div>
                            <p className="text-xs text-muted-foreground text-center">
                                AI conviction in data sufficiency
                            </p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">Key Statistics</CardTitle>
                        </CardHeader>
                        <CardContent className="grid gap-4">
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-muted-foreground">Volume</span>
                                <span className="font-mono font-medium">
                                    {marketData?.volume ? (marketData.volume / 1000000).toFixed(2) + "M" : "N/A"}
                                </span>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-muted-foreground">Market Cap</span>
                                <span className="font-mono font-medium">
                                    {marketData?.market_cap ? (marketData.market_cap / 1000000000).toFixed(2) + "B" : "N/A"}
                                </span>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-muted-foreground">P/E Ratio</span>
                                <span className="font-mono font-medium">
                                    {marketData?.pe_ratio ? marketData.pe_ratio.toFixed(2) : "N/A"}
                                </span>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="bg-primary/5 border-primary/20">
                        <CardHeader>
                            <CardTitle className="text-base flex items-center gap-2 text-primary">
                                <MessageSquare className="h-4 w-4" />
                                Analyst Vibe
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-sm prose dark:prose-invert">
                                {analysisLoading ? (
                                    <Skeleton className="h-20 w-full" />
                                ) : (
                                    <ReactMarkdown>
                                        {analysis?.sentiment_analysis || "Sentiment data unavailable."}
                                    </ReactMarkdown>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    )
}
