import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { getApiUrl } from '@/lib/api-config'

interface WatchlistItem {
    symbol: string
    name?: string
    asset_type?: string
    notes?: string
    added_at?: string
}

interface WatchlistState {
    items: WatchlistItem[]
    loading: boolean
    lastSynced: string | null

    // Actions
    fetchWatchlist: () => Promise<void>
    addToWatchlist: (symbol: string, name?: string, assetType?: string) => Promise<void>
    removeFromWatchlist: (symbol: string) => Promise<void>
    isInWatchlist: (symbol: string) => boolean
    clearWatchlist: () => Promise<void>
}

export const useWatchlistStore = create<WatchlistState>()(
    persist(
        (set, get) => ({
            items: [],
            loading: false,
            lastSynced: null,

            fetchWatchlist: async () => {
                set({ loading: true })
                try {
                    const res = await fetch(getApiUrl('/watchlist'))
                    if (res.ok) {
                        const data = await res.json()
                        set({
                            items: data.items || [],
                            lastSynced: new Date().toISOString()
                        })
                    }
                } catch (error) {
                    console.error('Failed to fetch watchlist:', error)
                } finally {
                    set({ loading: false })
                }
            },

            addToWatchlist: async (symbol: string, name?: string, assetType?: string) => {
                try {
                    const res = await fetch(getApiUrl('/watchlist'), {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ symbol, name, asset_type: assetType })
                    })
                    if (res.ok) {
                        const data = await res.json()
                        set({ items: data.items || [] })
                    }
                } catch (error) {
                    console.error('Failed to add to watchlist:', error)
                }
            },

            removeFromWatchlist: async (symbol: string) => {
                try {
                    const res = await fetch(getApiUrl(`/watchlist/${symbol}`), {
                        method: 'DELETE'
                    })
                    if (res.ok) {
                        const data = await res.json()
                        set({ items: data.items || [] })
                    }
                } catch (error) {
                    console.error('Failed to remove from watchlist:', error)
                }
            },

            isInWatchlist: (symbol: string) => {
                const { items } = get()
                return items.some(item =>
                    item.symbol.toUpperCase() === symbol.toUpperCase()
                )
            },

            clearWatchlist: async () => {
                try {
                    const res = await fetch(getApiUrl('/watchlist'), {
                        method: 'DELETE'
                    })
                    if (res.ok) {
                        set({ items: [] })
                    }
                } catch (error) {
                    console.error('Failed to clear watchlist:', error)
                }
            }
        }),
        {
            name: 'investlens-watchlist',
            storage: createJSONStorage(() => localStorage),
            partialize: (state) => ({ items: state.items, lastSynced: state.lastSynced })
        }
    )
)
