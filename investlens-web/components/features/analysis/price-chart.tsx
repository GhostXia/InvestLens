"use client"

import { useEffect, useState } from "react"
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"
import { LineChart, ArrowUpRight, ArrowDownRight } from "lucide-react"

interface PriceChartProps {
    ticker: string
}

/**
 * PriceChart Component
 * 
 * Interactive Area Chart visualizing historical price action.
 * Uses Recharts for rendering SVG-based charts.
 * Support dynamic time-range switching (1M, 6M, 1Y).
 */
export function PriceChart({ ticker, quantMode = false }: { ticker: string, quantMode?: boolean }) {
    const [history, setHistory] = useState<any[]>([])
    const [prediction, setPrediction] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [period, setPeriod] = useState("6mo")
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true)
            setError(null)
            try {
                // 1. Fetch History
                const res = await fetch(`http://localhost:8000/api/v1/market/history/${ticker}?period=${period}`)
                if (!res.ok) throw new Error("Failed to load chart data")
                const json = await res.json()

                if (json.error || !json.candles) {
                    throw new Error(json.error || "No data available")
                }

                setHistory(json.candles)

                // 2. Fetch Prediction (if Quant Mode is ON)
                if (quantMode) {
                    try {
                        const predRes = await fetch(`http://localhost:8000/api/v1/market/prediction/${ticker}?days=7`)
                        const predJson = await predRes.json()
                        if (predJson.predictions) {
                            setPrediction(predJson.predictions)
                        }
                    } catch (e) {
                        console.warn("Prediction fetch failed", e)
                    }
                } else {
                    setPrediction([])
                }
            } catch (err: any) {
                setError(err.message)
            } finally {
                setLoading(false)
            }
        }

        if (ticker) fetchData()
    }, [ticker, period, quantMode])

    // Calculate chart color based on trend (green if last > first)
    const isUp = history.length > 0 && history[history.length - 1].close >= history[0].close
    const color = isUp ? "#22c55e" : "#ef4444"

    // Combine data for the chart (Recharts handles nulls for disconnected series)
    // We append prediction to the history array, but ensuring disjoint timestamps logic if needed
    // Simple approach: One big array? or separate Areas?
    // If we merge, we need "close" for history and "price/upper/lower" for prediction.
    const chartData = [
        ...history,
        ...prediction
    ]

    return (
        <Card className="min-h-[400px]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-base font-medium flex items-center gap-2">
                    <LineChart className="h-4 w-4 text-muted-foreground" />
                    Price Action
                    {quantMode && <span className="text-[10px] text-red-500 font-bold ml-2 animate-pulse border border-red-500 rounded px-1">QUANT MODE</span>}
                </CardTitle>
                <Tabs defaultValue="6mo" value={period} onValueChange={setPeriod} className="h-8">
                    <TabsList className="h-8">
                        <TabsTrigger value="1mo" className="text-xs h-6 px-2">1M</TabsTrigger>
                        <TabsTrigger value="6mo" className="text-xs h-6 px-2">6M</TabsTrigger>
                        <TabsTrigger value="1y" className="text-xs h-6 px-2">1Y</TabsTrigger>
                        <TabsTrigger value="ytd" className="text-xs h-6 px-2">YTD</TabsTrigger>
                    </TabsList>
                </Tabs>
            </CardHeader>
            <CardContent>
                {loading ? (
                    <div className="h-[300px] flex items-center justify-center">
                        <Skeleton className="h-full w-full" />
                    </div>
                ) : error ? (
                    <div className="h-[300px] flex items-center justify-center text-muted-foreground text-sm">
                        Chart data unavailable: {error}
                    </div>
                ) : (
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={chartData}>
                                <defs>
                                    <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                                        <stop offset="95%" stopColor={color} stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <XAxis
                                    dataKey="date"
                                    tickLine={false}
                                    axisLine={false}
                                    tickFormatter={(str) => {
                                        const date = new Date(str)
                                        return `${date.getMonth() + 1}/${date.getDate()}`
                                    }}
                                    interval="preserveStartEnd"
                                    minTickGap={50}
                                    fontSize={12}
                                    tick={{ fill: 'hsl(var(--muted-foreground))' }}
                                />
                                <YAxis
                                    domain={['auto', 'auto']}
                                    tickLine={false}
                                    axisLine={false}
                                    fontSize={12}
                                    tickFormatter={(val) => `$${val}`}
                                    tick={{ fill: 'hsl(var(--muted-foreground))' }}
                                    width={60}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: "hsl(var(--card))",
                                        borderColor: "hsl(var(--border))",
                                        borderRadius: "6px"
                                    }}
                                    itemStyle={{ color: "hsl(var(--foreground))" }}
                                    formatter={(value: any, name: string) => {
                                        if (typeof value !== 'number') return [value, name]
                                        if (name === "close") return [`$${value.toFixed(2)}`, "Close"]
                                        if (name === "price") return [`$${value.toFixed(2)}`, "Predicted"]
                                        if (name === "upper") return [`$${value.toFixed(2)}`, "Upper Band"]
                                        if (name === "lower") return [`$${value.toFixed(2)}`, "Lower Band"]
                                        return [value, name]
                                    }}
                                    labelFormatter={(label) => new Date(label).toLocaleDateString()}
                                />
                                {/* Historical Data */}
                                <Area
                                    type="monotone"
                                    dataKey="close"
                                    stroke={color}
                                    strokeWidth={2}
                                    fillOpacity={1}
                                    fill="url(#colorPrice)"
                                />
                                {/* Prediction Data */}
                                <Area
                                    type="monotone"
                                    dataKey="price"
                                    stroke="#ec4899" // Pink/Red for prediction
                                    strokeDasharray="5 5"
                                    strokeWidth={2}
                                    fill="none"
                                    connectNulls
                                />
                                <Area
                                    type="monotone"
                                    dataKey="upper"
                                    stroke="none"
                                    fill="#ec4899"
                                    fillOpacity={0.1}
                                    connectNulls
                                />
                                <Area
                                    type="monotone"
                                    dataKey="lower"
                                    stroke="none"
                                    fill="#ec4899"
                                    fillOpacity={0.1}
                                    connectNulls
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}
