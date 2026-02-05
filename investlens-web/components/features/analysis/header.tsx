"use client"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { ArrowUp, ArrowDown } from "lucide-react"

interface TickerHeaderProps {
    symbol: string
    price?: number
    change?: number
    changePercent?: number
    name?: string
    currency?: string
    isLoading: boolean
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
    isLoading
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

    const isPositive = change >= 0

    return (
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 animate-in fade-in slide-in-from-top-4 duration-500">
            <div className="flex items-center gap-4">
                <div className="flex items-center justify-center h-16 w-16 rounded-lg bg-primary/10 text-primary font-bold text-xl border border-primary/20">
                    {symbol.slice(0, 2)}
                </div>
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">{symbol}</h1>
                    <p className="text-muted-foreground font-medium">{name}</p>
                </div>
            </div>

            <div className="flex flex-col items-end">
                <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-extrabold tracking-tight">
                        {currency === "USD" ? "$" : ""}{price?.toFixed(2)}
                    </span>
                    <span className="text-sm text-muted-foreground font-medium">{currency}</span>
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
    )
}
