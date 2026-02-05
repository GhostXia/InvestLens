"use client"

import { Search, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { useState } from "react"
import { useRouter } from "next/navigation"

/**
 * AssetInput Component
 * 
 * The primary entry point for user interaction on the Home page.
 * Renders a large search bar designed to look like a modern search engine.
 * 
 * Behavior:
 * - Captures user input (Ticker or Asset Name).
 * - Redirects to `/analysis?ticker=XXX` on submission.
 * - Provides quick-access buttons for trending assets.
 * 
 * @returns {JSX.Element} The search input UI
 */
export function AssetInput() {
    const [query, setQuery] = useState("")
    const router = useRouter()

    /**
     * Handles form submission to navigate to analysis page.
     * Prevents default form submit and encodes the query parameter.
     */
    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault()
        if (query.trim()) {
            router.push(`/analysis?ticker=${encodeURIComponent(query)}`)
        }
    }

    return (
        <Card className="w-full max-w-2xl border-none shadow-none bg-transparent">
            <CardContent className="p-0">
                <form onSubmit={handleSearch} className="relative flex items-center w-full">
                    <Search className="absolute left-4 h-5 w-5 text-muted-foreground" />
                    <Input
                        className="h-14 w-full rounded-full border-2 border-muted bg-background pl-12 pr-12 text-lg shadow-sm transition-all focus-visible:border-primary focus-visible:ring-0 focus-visible:ring-offset-0"
                        placeholder="Enter Ticker (e.g., AAPL) or Asset Name..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                    />
                    <Button
                        type="submit"
                        size="icon"
                        className="absolute right-2 h-10 w-10 rounded-full"
                        disabled={!query.trim()}
                    >
                        <ArrowRight className="h-5 w-5" />
                        <span className="sr-only">Analyze</span>
                    </Button>
                </form>
                {/* Trending Suggestions used to guide new users */}
                <div className="mt-4 flex justify-center gap-2 text-sm text-muted-foreground">
                    <span>Trending:</span>
                    <button type="button" onClick={() => setQuery('NVDA')} className="hover:text-primary underline decoration-dotted">NVDA</button>
                    <button type="button" onClick={() => setQuery('BTC-USD')} className="hover:text-primary underline decoration-dotted">BTC</button>
                    <button type="button" onClick={() => setQuery('TSLA')} className="hover:text-primary underline decoration-dotted">TSLA</button>
                </div>
            </CardContent>
        </Card>
    )
}
