import { WatchlistPanel } from "@/components/features/watchlist/WatchlistPanel"

export default function WatchlistPage() {
    return (
        <div className="container mx-auto py-6 max-w-4xl h-[calc(100vh-80px)]">
            <h1 className="text-2xl font-bold mb-6">自选管理</h1>
            <div className="h-[600px]">
                <WatchlistPanel />
            </div>
        </div>
    )
}
