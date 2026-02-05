"use client"

import { useEffect, useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Activity } from "lucide-react"
import { getApiUrl } from "@/lib/api-config"

/**
 * SystemStatus Component
 * 
 * Periodically checks the health of the backend "Quant Kernel".
 * Displays a non-intrusive floating badge indicating connection status.
 * 
 * States:
 * - Checking: Initial state, hidden.
 * - Online: Green indicator, pulsing.
 * - Offline: Red indicator, static.
 * 
 * @returns {JSX.Element | null} The status badge or null if initializing
 */
export function SystemStatus() {
    const [status, setStatus] = useState<"online" | "offline" | "checking">("checking")

    useEffect(() => {
        /**
         * Polling function to hit the backend health endpoint.
         * Expects a 200 OK from getApiUrl("/health").
         */
        const checkHealth = async () => {
            try {
                const res = await fetch(getApiUrl("/health"))
                if (res.ok) {
                    setStatus("online")
                } else {
                    setStatus("offline")
                }
            } catch (e) {
                setStatus("offline")
            }
        }

        // Initial check + 30s interval polling
        checkHealth()
        const interval = setInterval(checkHealth, 30000)
        return () => clearInterval(interval)
    }, [])

    if (status === "checking") return null

    return (
        <div className="fixed bottom-4 right-4 flex items-center gap-2 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <Badge variant={status === "online" ? "outline" : "destructive"} className="gap-1.5 bg-background shadow-sm">
                <span className={`h-2 w-2 rounded-full ${status === "online" ? "bg-green-500 animate-pulse" : "bg-red-500"}`} />
                {status === "online" ? "System Operations Normal" : "Quant Kernel Offline"}
                {status === "online" && <Activity className="h-3 w-3 text-muted-foreground ml-1" />}
            </Badge>
        </div>
    )
}
