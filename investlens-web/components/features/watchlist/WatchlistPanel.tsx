"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useWatchlistStore } from "@/lib/store/watchlist"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Trash2, TrendingUp, TrendingDown, ExternalLink, RefreshCw } from "lucide-react"
import { PortfolioAdvisor } from "./PortfolioAdvisor"

export function WatchlistPanel() {
    const router = useRouter()
    const { items, loading, fetchWatchlist, removeFromWatchlist } = useWatchlistStore()

    useEffect(() => {
        fetchWatchlist()
    }, [])

    const handleRemove = (e: React.MouseEvent, symbol: string) => {
        e.stopPropagation()
        removeFromWatchlist(symbol)
    }

    const handleNavigate = (symbol: string) => {
        router.push(`/analysis?ticker=${symbol}`)
    }

    return (
        <Card className="h-full">
            <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">我的自选</CardTitle>
                    <div className="flex items-center gap-2">
                        <PortfolioAdvisor symbols={items.map(i => i.symbol)} />
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => fetchWatchlist()}
                            disabled={loading}
                        >
                            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                        </Button>
                    </div>
                </div>
                <CardDescription>
                    关注的资产列表 ({items.length})
                </CardDescription>
            </CardHeader>
            <CardContent className="h-[calc(100%-80px)] overflow-auto pr-2 custom-scrollbar">
                {items.length === 0 && !loading ? (
                    <div className="text-center py-8 text-muted-foreground text-sm">
                        暂无自选资产<br />
                        点击右上角星标添加
                    </div>
                ) : (
                    <div className="space-y-2">
                        {loading && items.length === 0 ? (
                            Array(3).fill(0).map((_, i) => (
                                <div key={i} className="flex items-center justify-between p-3 border rounded-lg">
                                    <div className="space-y-2">
                                        <Skeleton className="h-4 w-16" />
                                        <Skeleton className="h-3 w-24" />
                                    </div>
                                    <Skeleton className="h-8 w-8 rounded-full" />
                                </div>
                            ))
                        ) : (
                            items.map((item) => (
                                <div
                                    key={item.symbol}
                                    className="group flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                                    onClick={() => handleNavigate(item.symbol)}
                                >
                                    <div className="flex flex-col min-w-0">
                                        <div className="flex items-center gap-2">
                                            <span className="font-bold font-mono">{item.symbol}</span>
                                            {item.asset_type && (
                                                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-secondary text-secondary-foreground">
                                                    {item.asset_type === 'china_fund' ? '基金' :
                                                        item.asset_type === 'us_stock' ? '美股' : '股票'}
                                                </span>
                                            )}
                                        </div>
                                        <span className="text-xs text-muted-foreground truncate max-w-[160px]">
                                            {item.name || item.symbol}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="h-8 w-8 text-muted-foreground hover:text-destructive"
                                            onClick={(e) => handleRemove(e, item.symbol)}
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                )}
            </CardContent>
        </Card>
    )
}
