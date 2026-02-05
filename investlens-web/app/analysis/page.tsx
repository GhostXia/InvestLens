"use client"

import { useSearchParams } from "next/navigation"
import { AppShell } from "@/components/layout/app-shell"
import { AnalysisDashboard } from "@/components/features/analysis/dashboard"

/**
 * Analysis Page
 * 
 * The main container for the asset analysis view.
 * Responsible for extracting the `ticker` from URL search params
 * and passing it to the `AnalysisDashboard` feature component.
 * 
 * @returns {JSX.Element} The analysis page layout
 */
export default function AnalysisPage() {
    const searchParams = useSearchParams()
    const ticker = searchParams.get("ticker")

    return (
        <AppShell>
            {ticker ? (
                <AnalysisDashboard ticker={ticker} />
            ) : (
                <div className="flex h-full items-center justify-center text-muted-foreground">
                    No ticker specified. Please return home and search again.
                </div>
            )}
        </AppShell>
    )
}
