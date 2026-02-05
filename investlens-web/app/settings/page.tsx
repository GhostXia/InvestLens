"use client"

import { useState } from "react"
import { useSettingsStore } from "@/lib/store/settings"
import { AppShell } from "@/components/layout/app-shell"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { Brain, Lock, ShieldAlert } from "lucide-react"

/**
 * Settings Page
 * 
 * Allows users to configure:
 * 1. API Keys (Stored locally)
 * 2. Quant Mode (High-risk features)
 */
export default function SettingsPage() {
    const { apiKey, setApiKey, baseUrl, setBaseUrl, quantModeEnabled, setQuantModeEnabled } = useSettingsStore()
    const [showRiskDialog, setShowRiskDialog] = useState(false)

    const handleQuantToggle = (checked: boolean) => {
        if (checked) {
            // Require explicit confirmation
            setShowRiskDialog(true)
        } else {
            // Can always turn off safely
            setQuantModeEnabled(false)
        }
    }

    const confirmQuantMode = () => {
        setQuantModeEnabled(true)
        setShowRiskDialog(false)
    }

    return (
        <AppShell>
            <div className="max-w-4xl mx-auto space-y-8 p-6">
                <div className="space-y-2">
                    <h1 className="text-3xl font-bold">Settings</h1>
                    <p className="text-muted-foreground">Manage your preferences and local credentials.</p>
                </div>

                {/* API Key Section */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Lock className="h-5 w-5 text-blue-500" />
                            AI Provider Configuration
                        </CardTitle>
                        <CardDescription>
                            Configure your LLM connectivity. Keys are stored <strong>locally in your browser</strong> and never sent to our servers.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid w-full max-w-sm items-center gap-1.5">
                            <Label htmlFor="base-url">API Base URL</Label>
                            <Input
                                type="text"
                                id="base-url"
                                placeholder="https://api.openai.com/v1"
                                value={baseUrl}
                                onChange={(e) => setBaseUrl(e.target.value)}
                            />
                            <p className="text-xs text-muted-foreground">
                                Endpoint for OpenAI, DeepSeek, or local proxies (e.g., Ollama).
                            </p>
                        </div>
                        <div className="grid w-full max-w-sm items-center gap-1.5">
                            <Label htmlFor="api-key">API Key</Label>
                            <Input
                                type="password"
                                id="api-key"
                                placeholder="sk-..."
                                value={apiKey}
                                onChange={(e) => setApiKey(e.target.value)}
                            />
                            <p className="text-xs text-muted-foreground">
                                Your API key for authentication.
                            </p>
                        </div>
                    </CardContent>
                </Card>

                {/* Quant Mode Section */}
                <Card className={`border-l-4 ${quantModeEnabled ? 'border-l-red-500' : 'border-l-gray-300'}`}>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Brain className="h-5 w-5 text-purple-500" />
                            Quantitative Capabilities
                        </CardTitle>
                        <CardDescription>
                            Unlock advanced features like predictive K-lines and portfolio optimization.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="flex items-center justify-between">
                        <div className="space-y-1">
                            <Label className="text-base">Enable Quant Mode</Label>
                            <p className="text-sm text-muted-foreground">
                                {quantModeEnabled
                                    ? "Active. Features unlocked. Tread carefully."
                                    : "Disabled. System operating in strict Analysis Mode."}
                            </p>
                        </div>
                        <Switch
                            checked={quantModeEnabled}
                            onCheckedChange={handleQuantToggle}
                        />
                    </CardContent>
                </Card>

                {/* Risk Disclaimer Dialog */}
                <Dialog open={showRiskDialog} onOpenChange={setShowRiskDialog}>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle className="flex items-center gap-2 text-red-600">
                                <ShieldAlert className="h-6 w-6" />
                                Use with Excessive Caution
                            </DialogTitle>
                            <DialogDescription className="space-y-4 pt-4 text-foreground" asChild>
                                <div className="space-y-4">
                                    <p>
                                        By enabling <strong>Quant Mode</strong>, you gain access to predictive models and trade-like signals.
                                        Please confirm you understand the following:
                                    </p>
                                    <ul className="list-disc pl-5 space-y-2 text-sm text-muted-foreground">
                                        <li>
                                            <strong>Predictive K-Lines</strong> are AI hallucinations based on historical patterns and do not guarantee future performance.
                                        </li>
                                        <li>
                                            This software is for <strong>educational and analytical purposes only</strong>.
                                        </li>
                                        <li>
                                            The author (and the AI) assumes <strong>no responsibility</strong> for any financial losses incurred based on these outputs.
                                        </li>
                                    </ul>
                                </div>
                            </DialogDescription>
                        </DialogHeader>
                        <DialogFooter>
                            <Button variant="outline" onClick={() => setShowRiskDialog(false)}>
                                Cancel
                            </Button>
                            <Button variant="destructive" onClick={confirmQuantMode}>
                                I Understand the Risks
                            </Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>
        </AppShell>
    )
}
