"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, Scale, Loader2, CheckCircle2 } from "lucide-react"
import ReactMarkdown from "react-markdown"

interface DebateEvent {
    stage: "context" | "bull" | "bear" | "judge" | "done"
    status: "thinking" | "fetching" | "complete"
    model?: string
    content?: string
    message?: string
    result?: any
}

interface DebateViewerProps {
    ticker: string
    headers: Record<string, string>
    onComplete?: (result: any) => void
}

/**
 * DebateViewer Component
 * 
 * Real-time visualization of the LLM debate process using SSE.
 * Shows Bull, Bear, and Judge stages with live updates.
 */
export function DebateViewer({ ticker, headers, onComplete }: DebateViewerProps) {
    const [activeTab, setActiveTab] = useState("bull")
    const [bullContent, setBullContent] = useState<string[]>([])
    const [bearContent, setBearContent] = useState<string[]>([])
    const [judgeContent, setJudgeContent] = useState("")
    const [stages, setStages] = useState<Record<string, "pending" | "thinking" | "complete">>({
        context: "pending",
        bull: "pending",
        bear: "pending",
        judge: "pending"
    })
    const [isConnected, setIsConnected] = useState(false)
    const eventSourceRef = useRef<EventSource | null>(null)

    useEffect(() => {
        // Use fetch with POST for SSE (EventSource doesn't support POST)
        const startStream = async () => {
            setIsConnected(true)

            try {
                const response = await fetch("http://localhost:8000/api/v1/analyze/stream", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        ...headers
                    },
                    body: JSON.stringify({
                        ticker: ticker,
                        focus_areas: ["Technical", "Fundamental", "Market Sentiment"]
                    })
                })

                if (!response.ok) throw new Error("Stream failed")

                const reader = response.body?.getReader()
                const decoder = new TextDecoder()

                while (reader) {
                    const { done, value } = await reader.read()
                    if (done) break

                    const chunk = decoder.decode(value)
                    const lines = chunk.split("\n")

                    for (const line of lines) {
                        if (line.startsWith("data: ")) {
                            try {
                                const event: DebateEvent = JSON.parse(line.slice(6))
                                handleEvent(event)
                            } catch (e) {
                                console.error("Failed to parse SSE event:", e)
                            }
                        }
                    }
                }
            } catch (error) {
                console.error("Stream error:", error)
            } finally {
                setIsConnected(false)
            }
        }

        startStream()

        return () => {
            if (eventSourceRef.current) {
                eventSourceRef.current.close()
            }
        }
    }, [ticker, headers])

    const handleEvent = (event: DebateEvent) => {
        // Update stage status
        if (event.status === "thinking" || event.status === "fetching") {
            setStages(prev => ({ ...prev, [event.stage]: "thinking" }))
            // Switch to active tab
            if (event.stage !== "context" && event.stage !== "done") {
                setActiveTab(event.stage)
            }
        } else if (event.status === "complete") {
            setStages(prev => ({ ...prev, [event.stage]: "complete" }))
        }

        // Update content
        if (event.stage === "bull" && event.status === "complete" && event.content) {
            setBullContent(prev => [...prev, `### ${event.model}\n${event.content}`])
        } else if (event.stage === "bear" && event.status === "complete" && event.content) {
            setBearContent(prev => [...prev, `### ${event.model}\n${event.content}`])
        } else if (event.stage === "judge" && event.status === "complete" && event.content) {
            setJudgeContent(event.content)
            setActiveTab("judge")
        } else if (event.stage === "done" && event.result) {
            onComplete?.(event.result)
        }
    }

    const getStatusIcon = (stage: string) => {
        const status = stages[stage]
        if (status === "thinking") return <Loader2 className="h-4 w-4 animate-spin text-yellow-500" />
        if (status === "complete") return <CheckCircle2 className="h-4 w-4 text-green-500" />
        return null
    }

    return (
        <Card className="mt-6">
            <CardHeader className="pb-3">
                <CardTitle className="flex items-center justify-between">
                    <span className="flex items-center gap-2">
                        <Scale className="h-5 w-5 text-purple-500" />
                        LLM Debate Process
                    </span>
                    {isConnected && (
                        <Badge variant="outline" className="animate-pulse">
                            <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                            Live
                        </Badge>
                    )}
                </CardTitle>
            </CardHeader>
            <CardContent>
                <Tabs value={activeTab} onValueChange={setActiveTab}>
                    <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="bull" className="flex items-center gap-2">
                            <TrendingUp className="h-4 w-4 text-green-500" />
                            Bull
                            {getStatusIcon("bull")}
                        </TabsTrigger>
                        <TabsTrigger value="bear" className="flex items-center gap-2">
                            <TrendingDown className="h-4 w-4 text-red-500" />
                            Bear
                            {getStatusIcon("bear")}
                        </TabsTrigger>
                        <TabsTrigger value="judge" className="flex items-center gap-2">
                            <Scale className="h-4 w-4 text-purple-500" />
                            Judge
                            {getStatusIcon("judge")}
                        </TabsTrigger>
                    </TabsList>

                    <TabsContent value="bull" className="mt-4 max-h-[400px] overflow-y-auto">
                        {bullContent.length === 0 && stages.bull === "pending" && (
                            <div className="text-center py-8 text-muted-foreground">
                                Waiting for Bull analysis...
                            </div>
                        )}
                        {stages.bull === "thinking" && bullContent.length === 0 && (
                            <div className="flex items-center justify-center py-8 gap-2">
                                <Loader2 className="h-5 w-5 animate-spin text-green-500" />
                                <span className="text-green-600">Bull is thinking...</span>
                            </div>
                        )}
                        <div className="prose prose-sm dark:prose-invert max-w-none space-y-4">
                            {bullContent.map((content, i) => (
                                <div key={i} className="p-3 bg-green-50 dark:bg-green-950/20 rounded-lg border border-green-200 dark:border-green-900">
                                    <ReactMarkdown>{content}</ReactMarkdown>
                                </div>
                            ))}
                        </div>
                    </TabsContent>

                    <TabsContent value="bear" className="mt-4 max-h-[400px] overflow-y-auto">
                        {bearContent.length === 0 && stages.bear === "pending" && (
                            <div className="text-center py-8 text-muted-foreground">
                                Waiting for Bear analysis...
                            </div>
                        )}
                        {stages.bear === "thinking" && bearContent.length === 0 && (
                            <div className="flex items-center justify-center py-8 gap-2">
                                <Loader2 className="h-5 w-5 animate-spin text-red-500" />
                                <span className="text-red-600">Bear is thinking...</span>
                            </div>
                        )}
                        <div className="prose prose-sm dark:prose-invert max-w-none space-y-4">
                            {bearContent.map((content, i) => (
                                <div key={i} className="p-3 bg-red-50 dark:bg-red-950/20 rounded-lg border border-red-200 dark:border-red-900">
                                    <ReactMarkdown>{content}</ReactMarkdown>
                                </div>
                            ))}
                        </div>
                    </TabsContent>

                    <TabsContent value="judge" className="mt-4 max-h-[400px] overflow-y-auto">
                        {!judgeContent && stages.judge === "pending" && (
                            <div className="text-center py-8 text-muted-foreground">
                                Waiting for Judge verdict...
                            </div>
                        )}
                        {stages.judge === "thinking" && !judgeContent && (
                            <div className="flex items-center justify-center py-8 gap-2">
                                <Loader2 className="h-5 w-5 animate-spin text-purple-500" />
                                <span className="text-purple-600">Judge is deliberating...</span>
                            </div>
                        )}
                        {judgeContent && (
                            <div className="prose prose-sm dark:prose-invert max-w-none p-3 bg-purple-50 dark:bg-purple-950/20 rounded-lg border border-purple-200 dark:border-purple-900">
                                <ReactMarkdown>{judgeContent}</ReactMarkdown>
                            </div>
                        )}
                    </TabsContent>
                </Tabs>
            </CardContent>
        </Card>
    )
}
