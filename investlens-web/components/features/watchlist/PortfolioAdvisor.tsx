"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertTriangle, Flame, Skull, Sparkles, Lock } from "lucide-react"
import ReactMarkdown from 'react-markdown'
import { getApiUrl } from "@/lib/api-config"
import { useSettingsStore } from "@/lib/store/settings"

interface PortfolioAdvisorProps {
    symbols: string[]
}

export function PortfolioAdvisor({ symbols }: PortfolioAdvisorProps) {
    const [loading, setLoading] = useState(false)
    const [report, setReport] = useState<string | null>(null)
    const [isOpen, setIsOpen] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const { quantModeEnabled } = useSettingsStore()

    if (!quantModeEnabled) {
        return (
            <Button variant="outline" disabled className="gap-2 border-dashed">
                <Lock className="h-4 w-4" />
                <span className="hidden sm:inline">AI 毒舌评测 (需开启量化模式)</span>
                <span className="sm:hidden">已锁定</span>
            </Button>
        )
    }

    const handleAnalyze = async () => {
        if (symbols.length === 0) return

        setLoading(true)
        setError(null)
        setReport(null)

        try {
            const res = await fetch(getApiUrl('/analysis/portfolio'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symbols })
            })

            if (!res.ok) {
                throw new Error("Analysis failed")
            }

            const data = await res.json()
            setReport(data.report)
        } catch (err) {
            setError("AI 正在休息，或是被你的持仓吓到了。请稍后再试。")
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    return (
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>
                <Button
                    variant="destructive"
                    className="gap-2 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 border-0 shadow-lg"
                    disabled={symbols.length === 0}
                >
                    <Flame className="h-4 w-4 fill-yellow-300 text-yellow-300" />
                    AI 毒舌评测 (High Risk)
                </Button>
            </DialogTrigger>
            <DialogContent className="max-w-3xl h-[80vh] flex flex-col">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2 text-2xl font-black text-destructive">
                        <Skull className="h-6 w-6" />
                        Hedge Fund Manager's Roast
                    </DialogTitle>
                    <DialogDescription>
                        警告：此模式即为激进，包含可能会让你感到不适的真实评价。不构成任何财务建议。
                    </DialogDescription>
                </DialogHeader>

                <div className="flex-1 overflow-hidden mt-4">
                    {!report && !loading && !error && (
                        <div className="h-full flex flex-col items-center justify-center text-center p-8 space-y-4">
                            <Flame className="h-16 w-16 text-orange-500 animate-pulse" />
                            <h3 className="text-xl font-bold">准备好接受暴击了吗？</h3>
                            <p className="text-muted-foreground max-w-md">
                                AI 将模仿一位冷酷无情的对冲基金经理，无视常规风险提示，直接指出你持仓中的致命弱点。
                            </p>
                            <Button size="lg" onClick={handleAnalyze} className="mt-4">
                                开始评测
                            </Button>
                        </div>
                    )}

                    {loading && (
                        <div className="h-full flex flex-col items-center justify-center space-y-4">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                            <p className="text-lg font-medium animate-pulse">正在审视你的"资产" (如果可以称之为资产的话)...</p>
                        </div>
                    )}

                    {error && (
                        <Alert variant="destructive">
                            <AlertTriangle className="h-4 w-4" />
                            <AlertTitle>Error</AlertTitle>
                            <AlertDescription>{error}</AlertDescription>
                        </Alert>
                    )}

                    {report && (
                        <ScrollArea className="h-full pr-4">
                            <div className="prose dark:prose-invert max-w-none pb-8">
                                <ReactMarkdown
                                    components={{
                                        h1: ({ node, ...props }) => <h1 className="text-3xl font-black text-red-500 mt-8 mb-4 border-b border-red-500/30 pb-2" {...props} />,
                                        h2: ({ node, ...props }) => <h2 className="text-xl font-bold text-orange-400 mt-6 mb-3" {...props} />,
                                        li: ({ node, ...props }) => <li className="my-1" {...props} />,
                                        strong: ({ node, ...props }) => <strong className="text-yellow-400 font-bold" {...props} />,
                                    }}
                                >
                                    {report}
                                </ReactMarkdown>
                            </div>
                        </ScrollArea>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    )
}
