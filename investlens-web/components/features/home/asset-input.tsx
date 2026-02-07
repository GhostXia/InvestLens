"use client"

import { Search, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { useState, useRef, useEffect } from "react"
import { useRouter } from "next/navigation"
import { getApiUrl } from "@/lib/api-config"
import { useTranslations } from "next-intl"

import { useSettingsStore } from "@/lib/store/settings"

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
    const [results, setResults] = useState<any[]>([])
    const [showResults, setShowResults] = useState(false)
    const [loading, setLoading] = useState(false)
    const router = useRouter()
    const t = useTranslations("home")

    // Debounce timer ref
    const debounceRef = useRef<NodeJS.Timeout | null>(null)

    // Container ref for click outside detection
    const containerRef = useRef<HTMLFormElement>(null)

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
                setShowResults(false)
            }
        }
        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    const handleSearchChange = (value: string) => {
        setQuery(value)
        if (value.length >= 2 || results.length > 0) {
            setShowResults(true)
        }

        if (debounceRef.current) {
            clearTimeout(debounceRef.current)
        }

        if (value.length < 2) {
            setResults([])
            return
        }

        debounceRef.current = setTimeout(async () => {
            setLoading(true)
            try {
                // Get enabled search providers from store
                const { ddgEnabled, yahooEnabled, akshareEnabled, customEnabled } = useSettingsStore.getState()

                // Build list of fetch promises based on enabled providers
                const fetchPromises: Promise<Response>[] = [
                    // Always fetch asset search
                    fetch(getApiUrl(`/api/v1/search?q=${encodeURIComponent(value)}`))
                ]

                // Add enabled provider fetches
                if (ddgEnabled) {
                    fetchPromises.push(
                        fetch(getApiUrl(`/search/suggestions?query=${encodeURIComponent(value)}&provider=duckduckgo`))
                    )
                }
                if (yahooEnabled) {
                    fetchPromises.push(
                        fetch(getApiUrl(`/search/suggestions?query=${encodeURIComponent(value)}&provider=yahoo`))
                    )
                }
                if (akshareEnabled) {
                    fetchPromises.push(
                        fetch(getApiUrl(`/search/suggestions?query=${encodeURIComponent(value)}&provider=akshare`))
                    )
                }
                if (customEnabled) {
                    fetchPromises.push(
                        fetch(getApiUrl(`/search/suggestions?query=${encodeURIComponent(value)}&provider=custom`))
                    )
                }

                const responses = await Promise.all(fetchPromises)

                // Parse asset search results
                const assetData = responses[0].ok ? await responses[0].json() : { results: [] }
                const assetResults = assetData.results || []

                // Parse provider results (offset by 1 due to asset search being first)
                let allSuggestions: any[] = []
                let responseIndex = 1

                if (ddgEnabled && responses[responseIndex]) {
                    const ddgData = responses[responseIndex].ok ? await responses[responseIndex].json() : { suggestions: [] }
                    allSuggestions = [...allSuggestions, ...(ddgData.suggestions || [])]
                    responseIndex++
                }

                if (yahooEnabled && responses[responseIndex]) {
                    const yahooData = responses[responseIndex].ok ? await responses[responseIndex].json() : { suggestions: [] }
                    allSuggestions = [...allSuggestions, ...(yahooData.suggestions || [])]
                    responseIndex++
                }

                if (akshareEnabled && responses[responseIndex]) {
                    const akshareData = responses[responseIndex].ok ? await responses[responseIndex].json() : { suggestions: [] }
                    allSuggestions = [...allSuggestions, ...(akshareData.suggestions || [])]
                    responseIndex++
                }

                if (customEnabled && responses[responseIndex]) {
                    const customData = responses[responseIndex].ok ? await responses[responseIndex].json() : { suggestions: [] }
                    allSuggestions = [...allSuggestions, ...(customData.suggestions || [])]
                }

                // Combine: Asset search results first, then all provider suggestions
                setResults([...assetResults, ...allSuggestions].slice(0, 15))
            } catch (error) {
                console.error("Search failed:", error)
            } finally {
                setLoading(false)
            }
        }, 300)
    }

    const selectResult = (item: any) => {
        if (item.isDdg) {
            setQuery(item.ticker)
            handleSearchChange(item.ticker)
        } else if (item.isYahoo || item.isAkshare || item.isCustom) {
            setQuery(item.ticker)
            setShowResults(false)
            router.push(`/analysis?ticker=${encodeURIComponent(item.ticker)}`)
        } else {
            setQuery(item.ticker)
            setShowResults(false)
            router.push(`/analysis?ticker=${encodeURIComponent(item.ticker)}`)
        }
    }

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault()
        if (query.trim()) {
            router.push(`/analysis?ticker=${encodeURIComponent(query)}`)
            setShowResults(false)
        }
    }

    return (
        <Card className="w-full max-w-2xl border-none shadow-none bg-transparent relative z-50">
            <CardContent className="p-0 relative">
                {/* Search Tips */}
                <div className="text-center mb-3 text-sm text-muted-foreground">
                    <p className="mb-1">{t("searchTips.main")}</p>
                    <p className="text-xs opacity-75">
                        {t("searchTips.examples")}: <code className="bg-muted px-1 rounded">AAPL</code> · <code className="bg-muted px-1 rounded">0700.HK</code> · <code className="bg-muted px-1 rounded">平安银行</code> · <code className="bg-muted px-1 rounded">Tesla Inc</code>
                    </p>
                </div>

                <form
                    ref={containerRef}
                    onSubmit={handleSearch}
                    className="relative flex items-center w-full"
                >
                    <Search className="absolute left-4 h-5 w-5 text-muted-foreground" />
                    <Input
                        className="h-14 w-full rounded-full border-2 border-muted bg-background pl-12 pr-12 text-lg shadow-sm transition-all focus-visible:border-primary focus-visible:ring-0 focus-visible:ring-offset-0"
                        placeholder={t("searchPlaceholder")}
                        value={query}
                        onChange={(e) => handleSearchChange(e.target.value)}
                        onFocus={() => { if (results.length > 0) setShowResults(true) }}
                    />
                    <Button
                        type="submit"
                        size="icon"
                        className="absolute right-2 h-10 w-10 rounded-full"
                        disabled={!query.trim()}
                    >
                        <ArrowRight className="h-5 w-5" />
                        <span className="sr-only">{t("analyze")}</span>
                    </Button>

                    {/* Autocomplete Dropdown - inside form for proper positioning */}
                    {showResults && (results.length > 0 || loading) && (
                        <div className="absolute top-full left-0 right-0 mt-2 bg-background border rounded-lg shadow-lg overflow-hidden py-1 max-h-80 overflow-y-auto z-50 animate-in fade-in zoom-in-95 duration-100">
                            {loading && <div className="p-3 text-center text-sm text-muted-foreground">{t("searching")}</div>}

                            {!loading && results.map((item, index) => (
                                <div
                                    key={`${item.ticker}-${index}`}
                                    className="px-4 py-3 hover:bg-muted/50 cursor-pointer flex justify-between items-center transition-colors"
                                    onClick={(e) => {
                                        e.stopPropagation()
                                        selectResult(item)
                                    }}
                                >
                                    <div>
                                        <div className="font-semibold">{item.ticker}</div>
                                        <div className="text-xs text-muted-foreground truncate max-w-[300px]">{item.name}</div>
                                    </div>
                                    <div className="text-right">
                                        {item.isDdg ? (
                                            <div className="text-xs font-mono bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-1.5 py-0.5 rounded">DDG</div>
                                        ) : item.isYahoo ? (
                                            <>
                                                <div className="text-xs font-mono bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 px-1.5 py-0.5 rounded">Yahoo</div>
                                                <div className="text-[10px] text-muted-foreground mt-0.5">{item.exchange}</div>
                                            </>
                                        ) : item.isAkshare ? (
                                            <>
                                                <div className="text-xs font-mono bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 px-1.5 py-0.5 rounded">AkShare</div>
                                                <div className="text-[10px] text-muted-foreground mt-0.5">{item.exchange}</div>
                                            </>
                                        ) : item.isCustom ? (
                                            <>
                                                <div className="text-xs font-mono bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 px-1.5 py-0.5 rounded">{item.source || 'Custom'}</div>
                                                <div className="text-[10px] text-muted-foreground mt-0.5">{item.exchange}</div>
                                            </>
                                        ) : (
                                            <>
                                                <div className="text-xs font-mono bg-muted px-1.5 py-0.5 rounded">{item.asset_type || 'Asset'}</div>
                                                <div className="text-[10px] text-muted-foreground mt-0.5">{item.exchange}</div>
                                            </>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </form>

                {/* Trending Suggestions */}
                <div className="mt-4 flex justify-center gap-2 text-sm text-muted-foreground">
                    <span>{t("trending")}:</span>
                    <button type="button" onClick={() => handleSearchChange('NVDA')} className="hover:text-primary underline decoration-dotted">NVDA</button>
                    <button type="button" onClick={() => handleSearchChange('BTC-USD')} className="hover:text-primary underline decoration-dotted">BTC</button>
                    <button type="button" onClick={() => handleSearchChange('TSLA')} className="hover:text-primary underline decoration-dotted">TSLA</button>
                </div>
            </CardContent>
        </Card>
    )
}
