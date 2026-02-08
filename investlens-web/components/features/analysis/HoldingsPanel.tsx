"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { ChevronDown, ChevronUp, RefreshCw, TrendingUp, TrendingDown, Minus } from "lucide-react"
import { getApiUrl } from "@/lib/api-config"

interface Holding {
    code: string
    name: string
    weight: number
    shares?: number
    market_value?: number
    price?: number
    change?: number
    change_pct?: number
    // Legacy field names (for backward compatibility)
    stock_code?: string
    stock_name?: string
    ratio?: number
    current_price?: number
    change_percent?: number
}

interface HoldingsData {
    symbol: string
    asset_type?: string
    name?: string
    holdings: Holding[]
    report_date?: string
    total_count?: number
    note?: string
    error?: string
    // Legacy fields
    fund_code?: string
    total_holdings?: number
}

interface HoldingsPanelProps {
    symbol: string
}

/**
 * HoldingsPanel Component (Universal)
 * 
 * Displays holdings/constituents for any supported asset:
 * - China funds/ETFs
 * - US ETFs  
 * - HK ETFs
 * - Index constituents
 * 
 * Supports expand/collapse and real-time price tracking.
 */
export function HoldingsPanel({ symbol }: HoldingsPanelProps) {
    const [holdingsData, setHoldingsData] = useState<HoldingsData | null>(null)
    const [loading, setLoading] = useState(false)
    const [expanded, setExpanded] = useState(false)
    const [showRealtime, setShowRealtime] = useState(false)
    const [hasHoldings, setHasHoldings] = useState<boolean | null>(null)

    const fetchHoldings = async (withRealtime: boolean = false) => {
        setLoading(true)
        try {
            // Use new unified endpoint
            const endpoint = withRealtime
                ? `/holdings/${symbol}/realtime`
                : `/holdings/${symbol}`

            const res = await fetch(getApiUrl(endpoint))
            if (res.ok) {
                const data = await res.json()
                setHoldingsData(data)
                setShowRealtime(withRealtime)
                setHasHoldings(data.holdings && data.holdings.length > 0)
            } else {
                setHasHoldings(false)
            }
        } catch (err) {
            console.error("Failed to fetch holdings:", err)
            setHasHoldings(false)
        } finally {
            setLoading(false)
        }
    }

    // Auto-fetch on mount
    useEffect(() => {
        if (symbol) {
            fetchHoldings(false)
        }
    }, [symbol])

    // Don't render if we confirmed no holdings
    if (hasHoldings === false) {
        return null
    }

    // INITIAL LOAD: Don't render while loading the first time (prevents flash for stocks)
    if (loading && !holdingsData) {
        return null
    }

    // Don't render if no data and not loading (fallback)
    if (!holdingsData && !loading && hasHoldings === null) {
        return null
    }

    // Normalize holding data (handle legacy and new formats)
    const normalizeHolding = (h: Holding) => ({
        code: h.code || h.stock_code || "",
        name: h.name || h.stock_name || "",
        weight: h.weight || h.ratio || 0,
        price: h.price || h.current_price,
        change: h.change,
        change_pct: h.change_pct || h.change_percent,
    })

    const getTitle = () => {
        const type = holdingsData?.asset_type
        if (type === "china_fund") return "📊 基金持仓"
        if (type === "china_etf") return "📊 ETF 持仓"
        if (type === "us_etf") return "📊 ETF Holdings"
        if (type === "hk_etf") return "📊 ETF 持仓"
        if (type === "index") return "📊 指数成分"
        if (type === "stock") return "🏆 机构持仓"
        return "📊 持仓/成分"
    }

    const renderChangeIndicator = (change?: number, changePct?: number) => {
        if (change === undefined || change === null) {
            return <span className="text-muted-foreground">--</span>
        }

        const isPositive = change > 0
        const isNeutral = change === 0

        if (isNeutral) {
            return (
                <span className="text-muted-foreground flex items-center gap-1">
                    <Minus className="h-3 w-3" />
                    0.00%
                </span>
            )
        }

        return (
            <span className={`flex items-center gap-1 ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
                {isPositive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                {changePct !== undefined ? `${changePct > 0 ? '+' : ''}${changePct.toFixed(2)}%` : '--'}
            </span>
        )
    }

    const isStock = holdingsData?.asset_type === 'stock'

    return (
        <Card>
            <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center justify-between">
                    <span className="flex items-center gap-2">
                        {getTitle()}
                        {holdingsData?.report_date && (
                            <Badge variant="secondary" className="text-xs">
                                {holdingsData.report_date}
                            </Badge>
                        )}
                        {holdingsData?.asset_type && (
                            <Badge variant="outline" className="text-xs">
                                {holdingsData.asset_type.replace("_", " ")}
                            </Badge>
                        )}
                    </span>
                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => fetchHoldings(!showRealtime)}
                            disabled={loading}
                            className="text-xs"
                        >
                            <RefreshCw className={`h-3 w-3 mr-1 ${loading ? 'animate-spin' : ''}`} />
                            {showRealtime ? '静态' : '实时'}
                        </Button>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setExpanded(!expanded)}
                        >
                            {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                        </Button>
                    </div>
                </CardTitle>
            </CardHeader>

            {expanded && (
                <CardContent>
                    {loading ? (
                        <div className="space-y-2">
                            {[...Array(5)].map((_, i) => (
                                <Skeleton key={i} className="h-8 w-full" />
                            ))}
                        </div>
                    ) : holdingsData?.error ? (
                        <p className="text-sm text-muted-foreground text-center py-4">
                            {holdingsData.error}
                        </p>
                    ) : holdingsData?.note && (!holdingsData.holdings || holdingsData.holdings.length === 0) ? (
                        <p className="text-sm text-muted-foreground text-center py-4">
                            {holdingsData.note}
                        </p>
                    ) : (
                        <div className="space-y-1">
                            {/* Table Header */}
                            <div className="grid grid-cols-12 gap-2 text-xs text-muted-foreground font-medium py-1 border-b">
                                <div className="col-span-1">#</div>
                                <div className="col-span-5">{isStock ? "机构名称" : "名称"}</div>
                                <div className="col-span-2 text-right">{isStock ? "持股比例" : "权重"}</div>
                                {showRealtime && (
                                    <>
                                        <div className="col-span-2 text-right">现价</div>
                                        <div className="col-span-2 text-right">涨跌</div>
                                    </>
                                )}
                                {isStock && !showRealtime && (
                                    <div className="col-span-4 text-right">持股数</div>
                                )}
                            </div>

                            {/* Holdings List */}
                            {holdingsData?.holdings.map((rawHolding, index) => {
                                const holding = normalizeHolding(rawHolding)
                                return (
                                    <div
                                        key={holding.code || index}
                                        className="grid grid-cols-12 gap-2 text-sm py-2 hover:bg-muted/50 rounded"
                                    >
                                        <div className="col-span-1 text-muted-foreground">
                                            {index + 1}
                                        </div>
                                        <div className="col-span-5 truncate" title={holding.name}>
                                            <span className="font-medium">{holding.name}</span>
                                            {!isStock && (
                                                <span className="text-xs text-muted-foreground ml-2">
                                                    {holding.code}
                                                </span>
                                            )}
                                        </div>
                                        <div className="col-span-2 text-right font-mono">
                                            {holding.weight > 0 ? `${holding.weight.toFixed(2)}%` : '--'}
                                        </div>
                                        {showRealtime && (
                                            <>
                                                <div className="col-span-2 text-right font-mono">
                                                    {holding.price?.toFixed(2) || '--'}
                                                </div>
                                                <div className="col-span-2 text-right">
                                                    {renderChangeIndicator(holding.change, holding.change_pct)}
                                                </div>
                                            </>
                                        )}
                                        {isStock && !showRealtime && (
                                            <div className="col-span-4 text-right font-mono text-xs">
                                                {/* Access original shares from raw holding since normalized doesn't explicitly pass it well in typings yet */}
                                                {rawHolding.shares ? (rawHolding.shares / 1000000).toFixed(2) + 'M' : '--'}
                                            </div>
                                        )}
                                    </div>
                                )
                            })}

                            {(holdingsData?.total_count ?? holdingsData?.total_holdings ?? 0) > 10 && (
                                <p className="text-xs text-muted-foreground text-center pt-2">
                                    共 {holdingsData?.total_count || holdingsData?.total_holdings} 只持仓
                                </p>
                            )}
                        </div>
                    )}
                </CardContent>
            )}
        </Card>
    )
}
