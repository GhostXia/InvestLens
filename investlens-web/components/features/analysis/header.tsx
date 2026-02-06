"use client"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { ArrowUp, ArrowDown, Database } from "lucide-react"

interface TickerHeaderProps {
    symbol: string
    price?: number
    change?: number
    changePercent?: number
    name?: string
    currency?: string
    isLoading: boolean
    dataSource?: string
    volume?: number
    marketCap?: number
    peRatio?: number
    turnoverRate?: number
}

/**
 * TickerHeader Component
 * 
 * Displays the high-level market context for the analyzed asset.
 * Featured prominently at the top of the dashboard.
 * 
 * Visuals:
 * - Large ticker symbol and current price.
 * - Color-coded change indicator (Green/Red).
 * - Data source badge (Yahoo Finance / AkShare).
 * - Key metrics bar (Volume, Market Cap, P/E).
 * - Skeleton loading state.
 * 
 * @param {TickerHeaderProps} props - Market data and loading state
 * @returns {JSX.Element} The header UI
 */
export function TickerHeader({
    symbol,
    price,
    change = 0,
    changePercent = 0,
    name,
    currency = "USD",
    isLoading,
    dataSource,
    volume,
    marketCap,
    peRatio,
    turnoverRate
}: TickerHeaderProps) {
    if (isLoading) {
        return (
            <div className="flex items-center gap-4 mb-6">
                <Skeleton className="h-16 w-16 rounded-lg" />
                <div className="space-y-2">
                    <Skeleton className="h-8 w-32" />
                    <Skeleton className="h-4 w-48" />
                </div>
            </div>
        )
    }

    // Auto-detect currency for Chinese stocks if not explicitly set to something else likely
    // Common patterns: 6 digits (A-share code usually), or suffixes .SS, .SZ
    const isChineseStock = /^\d{6}$|(\.SS|\.SZ)$/i.test(symbol)
    const effectiveCurrency = isChineseStock && (currency === "USD" || !currency) ? "CNY" : currency
    const currencySymbol = effectiveCurrency === "CNY" ? "¥" : effectiveCurrency === "USD" ? "$" : ""

    // Prioritize name for display
    const displayName = name || symbol
    // User requested full ticker (e.g. 603986.SS) as subtitle
    const displaySymbol = name ? symbol : ""
    const isPositive = change >= 0

    // Format large numbers
    const formatNumber = (num?: number) => {
        if (!num) return "N/A"
        if (num >= 1e12) return (num / 1e12).toFixed(2) + "T"
        if (num >= 1e9) return (num / 1e9).toFixed(2) + "B"
        if (num >= 1e6) return (num / 1e6).toFixed(2) + "M"
        if (num >= 1e3) return (num / 1e3).toFixed(2) + "K"
        return num.toFixed(2)
    }

    return (
        <div className="space-y-4 mb-6 animate-in fade-in slide-in-from-top-4 duration-500">
            {/* Main Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                    <div className="flex items-center justify-center h-16 w-16 rounded-lg bg-primary/10 text-primary font-bold text-xl border border-primary/20">
                        {symbol.slice(0, 2)}
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h1 className="text-3xl font-bold tracking-tight">{displayName}</h1>
                            {dataSource && (
                                <Badge variant="outline" className={`text-xs ${dataSource.includes("akshare")
                                    ? "border-red-500/50 text-red-600 dark:text-red-400"
                                    : "border-green-500/50 text-green-600 dark:text-green-400"
                                    }`}>
                                    <Database className="h-3 w-3 mr-1" />
                                    {dataSource === "akshare" ? "AkShare" :
                                        dataSource === "akshare_delayed" ? "AkShare (Delayed)" : "Yahoo Finance"}
                                </Badge>
                            )}
                        </div>
                        {displaySymbol && <p className="text-muted-foreground font-medium">{displaySymbol}</p>}
                    </div>
                </div>

                <div className="flex flex-col items-end">
                    <div className="flex items-baseline gap-2">
                        <span className="text-4xl font-extrabold tracking-tight">
                            {currencySymbol}{price?.toFixed(2)}
                        </span>
                        <span className="text-sm text-muted-foreground font-medium">{effectiveCurrency}</span>
                    </div>
                    <Badge
                        variant={isPositive ? "default" : "destructive"}
                        className={`gap-1 mt-1 ${isPositive ? "bg-green-600 hover:bg-green-700" : "bg-red-600 hover:bg-red-700"}`}
                    >
                        {isPositive ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
                        {Math.abs(change).toFixed(2)} ({Math.abs(changePercent).toFixed(2)}%)
                    </Badge>
                </div>
            </div>

            {/* Key Metrics Bar */}
            {(volume || marketCap || peRatio || turnoverRate) && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {volume && (
                        <div className="bg-muted/30 rounded-lg px-3 py-2">
                            <p className="text-xs text-muted-foreground">Volume</p>
                            <p className="font-mono font-medium">{formatNumber(volume)}</p>
                        </div>
                    )}
                    {marketCap && (
                        <div className="bg-muted/30 rounded-lg px-3 py-2">
                            <p className="text-xs text-muted-foreground">Market Cap</p>
                            <p className="font-mono font-medium">{currencySymbol}{formatNumber(marketCap)}</p>
                        </div>
                    )}
                    {peRatio && (
                        <div className="bg-muted/30 rounded-lg px-3 py-2">
                            <p className="text-xs text-muted-foreground">P/E Ratio</p>
                            <p className="font-mono font-medium">{peRatio.toFixed(2)}</p>
                        </div>
                    )}
                    {turnoverRate && (
                        <div className="bg-muted/30 rounded-lg px-3 py-2">
                            <p className="text-xs text-muted-foreground">Turnover</p>
                            <p className="font-mono font-medium">{turnoverRate.toFixed(2)}%</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
