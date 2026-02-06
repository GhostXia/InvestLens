"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { MessageCircle, X, Send, Bot, User, Loader2 } from "lucide-react"
import ReactMarkdown from 'react-markdown'
import { useSettingsStore } from "@/lib/store/settings"
import { getApiUrl } from "@/lib/api-config"

interface Message {
    role: "user" | "assistant"
    content: string
}

interface ChatBubbleProps {
    ticker: string
    tickerName?: string
    price?: number
    change?: number
    changePercent?: number
    currency?: string
    dataSource?: string
}

/**
 * ChatBubble Component
 * 
 * A floating chat bubble in the bottom-right corner that expands
 * into a chat window for AI-powered analysis discussions.
 * 
 * Features:
 * - Context-aware: knows current ticker and market data
 * - Streaming responses for better UX
 * - Persistent conversation during session
 */
export function ChatBubble({
    ticker,
    tickerName,
    price,
    change,
    changePercent,
    currency = "USD",
    dataSource
}: ChatBubbleProps) {
    const [isOpen, setIsOpen] = useState(false)
    const [messages, setMessages] = useState<Message[]>([])
    const [input, setInput] = useState("")
    const [isLoading, setIsLoading] = useState(false)
    const scrollRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLInputElement>(null)

    const { apiKey, baseUrl, model } = useSettingsStore()

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight
        }
    }, [messages])

    // Focus input when chat opens
    useEffect(() => {
        if (isOpen && inputRef.current) {
            inputRef.current.focus()
        }
    }, [isOpen])

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return

        const userMessage = input.trim()
        setInput("")
        setMessages(prev => [...prev, { role: "user", content: userMessage }])
        setIsLoading(true)

        try {
            // Build context for the AI
            const context = {
                ticker,
                name: tickerName,
                price,
                change,
                changePercent,
                currency,
                dataSource
            }

            const response = await fetch(getApiUrl("/api/v1/chat"), {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    ...(apiKey && { "X-LLM-API-Key": apiKey }),
                    ...(baseUrl && { "X-LLM-Base-URL": baseUrl }),
                    ...(model && { "X-LLM-Model": model })
                },
                body: JSON.stringify({
                    message: userMessage,
                    context,
                    history: messages.slice(-6) // Last 6 messages for context
                })
            })

            if (!response.ok) {
                throw new Error("Chat request failed")
            }

            const data = await response.json()
            setMessages(prev => [...prev, { role: "assistant", content: data.response }])

        } catch (error) {
            setMessages(prev => [...prev, {
                role: "assistant",
                content: "Sorry, the request failed. Please check if your LLM settings are configured correctly."
            }])
        } finally {
            setIsLoading(false)
        }
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            sendMessage()
        }
    }

    return (
        <>
            {/* Floating Bubble Button */}
            {!isOpen && (
                <Button
                    onClick={() => setIsOpen(true)}
                    className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg z-50 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                    size="icon"
                >
                    <MessageCircle className="h-6 w-6" />
                </Button>
            )}

            {/* Chat Window */}
            {isOpen && (
                <Card className="fixed bottom-6 right-6 w-[380px] h-[500px] shadow-2xl z-50 flex flex-col animate-in slide-in-from-bottom-4 duration-300 border-2 border-primary/20">
                    {/* Header */}
                    <CardHeader className="flex flex-row items-center justify-between py-3 px-4 border-b bg-gradient-to-r from-purple-600/10 to-blue-600/10">
                        <CardTitle className="text-base flex items-center gap-2">
                            <Bot className="h-5 w-5 text-purple-500" />
                            <span>AI Analyst</span>
                            <span className="text-xs text-muted-foreground font-normal">
                                ({ticker})
                            </span>
                        </CardTitle>
                        <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => setIsOpen(false)}
                        >
                            <X className="h-4 w-4" />
                        </Button>
                    </CardHeader>

                    {/* Messages Area */}
                    <ScrollArea className="flex-1 p-4" ref={scrollRef}>
                        {messages.length === 0 ? (
                            <div className="text-center text-muted-foreground text-sm py-8">
                                <Bot className="h-12 w-12 mx-auto mb-4 text-purple-400 opacity-50" />
                                <p>Hi! I'm your AI Analyst.</p>
                                <p className="mt-1">What would you like to know about <strong>{ticker}</strong>?</p>
                                <div className="mt-4 space-y-2">
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="w-full text-xs"
                                        onClick={() => setInput("What's the technical analysis for this stock?")}
                                    >
                                        What's the technical analysis?
                                    </Button>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="w-full text-xs"
                                        onClick={() => setInput("Is this a good price to buy?")}
                                    >
                                        Is this a good price to buy?
                                    </Button>
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {messages.map((msg, idx) => (
                                    <div
                                        key={idx}
                                        className={`flex gap-2 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                                    >
                                        {msg.role === "assistant" && (
                                            <div className="h-7 w-7 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center flex-shrink-0">
                                                <Bot className="h-4 w-4 text-purple-600" />
                                            </div>
                                        )}
                                        <div
                                            className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${msg.role === "user"
                                                ? "bg-primary text-primary-foreground"
                                                : "bg-muted prose dark:prose-invert prose-sm max-w-none"
                                                }`}
                                        >
                                            {msg.role === "assistant" ? (
                                                <ReactMarkdown>{msg.content}</ReactMarkdown>
                                            ) : (
                                                msg.content
                                            )}
                                        </div>
                                        {msg.role === "user" && (
                                            <div className="h-7 w-7 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                                                <User className="h-4 w-4 text-primary" />
                                            </div>
                                        )}
                                    </div>
                                ))}
                                {isLoading && (
                                    <div className="flex gap-2 justify-start">
                                        <div className="h-7 w-7 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                                            <Bot className="h-4 w-4 text-purple-600" />
                                        </div>
                                        <div className="bg-muted rounded-lg px-3 py-2">
                                            <Loader2 className="h-4 w-4 animate-spin" />
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </ScrollArea>

                    {/* Input Area */}
                    <CardContent className="p-3 border-t">
                        <div className="flex gap-2">
                            <Input
                                ref={inputRef}
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Ask a question..."
                                disabled={isLoading}
                                className="flex-1"
                            />
                            <Button
                                onClick={sendMessage}
                                disabled={!input.trim() || isLoading}
                                size="icon"
                                className="bg-gradient-to-r from-purple-600 to-blue-600"
                            >
                                <Send className="h-4 w-4" />
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            )}
        </>
    )
}
