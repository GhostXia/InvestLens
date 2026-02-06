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
import { Brain, Lock, ShieldAlert, Database, Trash2, Search } from "lucide-react"
import { DataSourceEditor } from "@/components/settings/DataSourceEditor"

/**
 * Settings Page
 * 
 * Allows users to configure:
 * 1. API Keys (Stored locally)
 * 2. Quant Mode (High-risk features)
 */
export default function SettingsPage() {
    const { apiKey, setApiKey, baseUrl, setBaseUrl, model, setModel, quantModeEnabled, setQuantModeEnabled, ddgEnabled, setDdgEnabled, yahooEnabled, setYahooEnabled, akshareEnabled, setAkshareEnabled, clearAll } = useSettingsStore()
    const [showRiskDialog, setShowRiskDialog] = useState(false)
    const [showClearDialog, setShowClearDialog] = useState(false)
    const [clearing, setClearing] = useState(false)

    // Local state for unsaved changes
    const [tempApiKey, setTempApiKey] = useState(apiKey)
    const [tempBaseUrl, setTempBaseUrl] = useState(baseUrl)
    const [tempModel, setTempModel] = useState(model)
    const [saveSuccess, setSaveSuccess] = useState(false)

    // Model fetching state
    const [availableModels, setAvailableModels] = useState<Array<{ id: string, name: string }>>([])
    const [fetchingModels, setFetchingModels] = useState(false)
    const [modelsFetched, setModelsFetched] = useState(false)

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

    const fetchAvailableModels = async () => {
        if (!tempBaseUrl) return

        setFetchingModels(true)
        try {
            const response = await fetch("http://localhost:8000/api/v1/models", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    base_url: tempBaseUrl,
                    api_key: tempApiKey || "sk-placeholder"
                })
            })

            if (response.ok) {
                const data = await response.json()
                setAvailableModels(data.models || [])
                setModelsFetched(true)
            }
        } catch (error) {
            console.error("Failed to fetch models:", error)
            // Set default models on error
            setAvailableModels([
                { id: "gpt-4", name: "GPT-4" },
                { id: "gpt-3.5-turbo", name: "GPT-3.5 Turbo" },
                { id: "deepseek-chat", name: "DeepSeek Chat" },
            ])
        } finally {
            setFetchingModels(false)
        }
    }

    const handleSaveApiSettings = () => {
        setApiKey(tempApiKey)
        setBaseUrl(tempBaseUrl)
        setModel(tempModel)
        setSaveSuccess(true)
        setTimeout(() => setSaveSuccess(false), 2000)
    }

    const handleClearAllData = async () => {
        setClearing(true)
        try {
            // Clear frontend data
            clearAll()
            setTempApiKey("")
            setTempBaseUrl("https://api.openai.com/v1")
            setTempModel("gpt-4")

            // Clear backend data
            const response = await fetch("http://localhost:8000/privacy/clear-all", {
                method: "POST"
            })

            if (response.ok) {
                console.log("Backend privacy data cleared successfully")
            } else {
                console.error("Failed to clear backend data")
            }
        } catch (error) {
            console.error("Error clearing privacy data:", error)
        } finally {
            setClearing(false)
            setShowClearDialog(false)
        }
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
                                value={tempBaseUrl}
                                onChange={(e) => setTempBaseUrl(e.target.value)}
                            />
                            <p className="text-xs text-muted-foreground">
                                Endpoint for OpenAI, DeepSeek, or local proxies (e.g., Ollama).
                            </p>
                            <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={fetchAvailableModels}
                                disabled={!tempBaseUrl || fetchingModels}
                                className="mt-2"
                            >
                                {fetchingModels ? "Fetching..." : "Fetch Available Models"}
                            </Button>
                        </div>
                        <div className="grid w-full max-w-sm items-center gap-1.5">
                            <Label htmlFor="model">Model</Label>
                            {modelsFetched && availableModels.length > 0 ? (
                                <select
                                    id="model"
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    value={tempModel}
                                    onChange={(e) => setTempModel(e.target.value)}
                                >
                                    {availableModels.map(m => (
                                        <option key={m.id} value={m.id}>{m.name}</option>
                                    ))}
                                    <option value="custom">Custom (Enter Below)</option>
                                </select>
                            ) : (
                                <select
                                    id="model"
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    value={tempModel}
                                    onChange={(e) => setTempModel(e.target.value)}
                                >
                                    <optgroup label="OpenAI">
                                        <option value="gpt-4">GPT-4</option>
                                        <option value="gpt-4-turbo">GPT-4 Turbo</option>
                                        <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                                    </optgroup>
                                    <optgroup label="DeepSeek">
                                        <option value="deepseek-chat">DeepSeek Chat</option>
                                        <option value="deepseek-reasoner">DeepSeek Reasoner</option>
                                    </optgroup>
                                    <optgroup label="Local Models">
                                        <option value="qwen2.5">Qwen 2.5</option>
                                        <option value="llama3.1">Llama 3.1</option>
                                        <option value="mistral">Mistral</option>
                                        <option value="gemma2">Gemma 2</option>
                                    </optgroup>
                                    <option value="custom">Custom (Enter Below)</option>
                                </select>
                            )}
                            {tempModel === 'custom' && (
                                <Input
                                    type="text"
                                    placeholder="Enter custom model name"
                                    className="mt-2"
                                    onChange={(e) => setTempModel(e.target.value)}
                                />
                            )}
                            <p className="text-xs text-muted-foreground">
                                {modelsFetched
                                    ? "Select from available models or choose Custom."
                                    : "Click 'Fetch Available Models' to load models from your endpoint."}
                            </p>
                        </div>
                        <div className="grid w-full max-w-sm items-center gap-1.5">
                            <Label htmlFor="api-key">API Key</Label>
                            <Input
                                type="password"
                                id="api-key"
                                placeholder="sk-..."
                                value={tempApiKey}
                                onChange={(e) => setTempApiKey(e.target.value)}
                            />
                            <p className="text-xs text-muted-foreground">
                                Your API key for authentication.
                            </p>
                        </div>
                        <div className="flex items-center gap-3">
                            <Button onClick={handleSaveApiSettings}>
                                Save Configuration
                            </Button>
                            {saveSuccess && (
                                <span className="text-sm text-green-600 dark:text-green-400 animate-in fade-in">
                                    ✓ Saved successfully
                                </span>
                            )}
                        </div>
                    </CardContent>
                </Card>

                {/* Search Provider Section */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Search className="h-5 w-5 text-green-500" />
                            Search Configuration
                        </CardTitle>
                        <CardDescription>
                            Enable multiple search providers for parallel autocomplete suggestions.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex items-center justify-between py-2">
                            <div className="space-y-0.5">
                                <Label className="text-base">DuckDuckGo</Label>
                                <p className="text-sm text-muted-foreground">
                                    General web search suggestions
                                </p>
                            </div>
                            <Switch
                                checked={ddgEnabled}
                                onCheckedChange={setDdgEnabled}
                            />
                        </div>
                        <div className="flex items-center justify-between py-2">
                            <div className="space-y-0.5">
                                <Label className="text-base">Yahoo Finance</Label>
                                <p className="text-sm text-muted-foreground">
                                    Precise financial tickers with market info
                                </p>
                            </div>
                            <Switch
                                checked={yahooEnabled}
                                onCheckedChange={setYahooEnabled}
                            />
                        </div>
                        <div className="flex items-center justify-between py-2">
                            <div className="space-y-0.5">
                                <Label className="text-base">AkShare (China)</Label>
                                <p className="text-sm text-muted-foreground">
                                    A股、基金，支持中文搜索
                                </p>
                            </div>
                            <Switch
                                checked={akshareEnabled}
                                onCheckedChange={setAkshareEnabled}
                            />
                        </div>
                        <p className="text-xs text-muted-foreground pt-2 border-t">
                            Results from each provider will be labeled (DDG / Yahoo / AkShare).
                        </p>
                    </CardContent>
                </Card>

                {/* Data Sources Section */}
                <DataSourceEditor />

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
                </Card >

                {/* Danger Zone - Privacy Data Cleanup */}
                <Card className="border-l-4 border-l-red-600 bg-red-50 dark:bg-red-950/20">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-red-600 dark:text-red-400">
                            <Trash2 className="h-5 w-5" />
                            Danger Zone
                        </CardTitle>
                        <CardDescription className="text-red-700 dark:text-red-300">
                            Permanently delete all privacy-sensitive data. This action cannot be undone.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="rounded-lg border border-red-300 dark:border-red-700 p-4 bg-white dark:bg-red-950/30">
                            <h4 className="font-semibold text-sm mb-2">Clear All Privacy Data</h4>
                            <p className="text-sm text-muted-foreground mb-4">
                                This will permanently delete:
                            </p>
                            <ul className="text-sm text-muted-foreground list-disc pl-5 space-y-1 mb-4">
                                <li>API Keys and endpoints (frontend)</li>
                                <li>Model preferences (frontend)</li>
                                <li>Data source configurations (backend)</li>
                                <li>Quant Mode settings</li>
                            </ul>
                            <Button
                                variant="destructive"
                                onClick={() => setShowClearDialog(true)}
                                disabled={clearing}
                            >
                                <Trash2 className="mr-2 h-4 w-4" />
                                {clearing ? "Clearing..." : "Clear All Privacy Data"}
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                {/* Risk Disclaimer Dialog */}
                < Dialog open={showRiskDialog} onOpenChange={setShowRiskDialog} >
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
                </Dialog >

                {/* Clear Privacy Data Confirmation Dialog */}
                <Dialog open={showClearDialog} onOpenChange={setShowClearDialog}>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle className="flex items-center gap-2 text-red-600">
                                <Trash2 className="h-6 w-6" />
                                Confirm Privacy Data Deletion
                            </DialogTitle>
                            <DialogDescription className="space-y-4 pt-4 text-foreground" asChild>
                                <div className="space-y-4">
                                    <p className="font-semibold">
                                        Are you absolutely sure you want to delete ALL privacy data?
                                    </p>
                                    <p className="text-sm">
                                        This action will <strong>permanently delete</strong>:
                                    </p>
                                    <ul className="list-disc pl-5 space-y-2 text-sm text-muted-foreground">
                                        <li>
                                            <strong>Frontend:</strong> API keys, base URLs, model preferences, Quant Mode settings
                                        </li>
                                        <li>
                                            <strong>Backend:</strong> Data source configurations and API endpoint settings
                                        </li>
                                    </ul>
                                    <p className="text-sm font-semibold text-red-600">
                                        This action cannot be undone. You will need to reconfigure everything from scratch.
                                    </p>
                                </div>
                            </DialogDescription>
                        </DialogHeader>
                        <DialogFooter>
                            <Button variant="outline" onClick={() => setShowClearDialog(false)}>
                                Cancel
                            </Button>
                            <Button variant="destructive" onClick={handleClearAllData} disabled={clearing}>
                                {clearing ? "Clearing..." : "Yes, Delete Everything"}
                            </Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div >
        </AppShell >
    )
}
