"use client"

import { useState } from "react"
import { useSettingsStore, ModelConfig } from "@/lib/store/settings"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Trash2, Plus, Save, Cpu, RefreshCw } from "lucide-react"

/**
 * ModelConfigEditor Component
 * 
 * Allows users to manage multiple LLM model configurations.
 * Each config has: Name, Base URL, API Key, Model ID, Enabled status.
 */
export function ModelConfigEditor() {
    const { modelConfigs, addModelConfig, removeModelConfig, updateModelConfig } = useSettingsStore()
    const [fetchingModels, setFetchingModels] = useState<Record<string, boolean>>({})
    const [availableModels, setAvailableModels] = useState<Record<string, Array<{ id: string, name: string }>>>({})
    const [saveStatus, setSaveStatus] = useState("")

    const handleAddConfig = () => {
        const newConfig: ModelConfig = {
            id: crypto.randomUUID(),
            name: "New Model",
            baseUrl: "",
            apiKey: "",
            model: "",
            enabled: true
        }
        addModelConfig(newConfig)
    }

    const handleRemoveConfig = (id: string) => {
        removeModelConfig(id)
    }

    const handleUpdate = (id: string, field: keyof ModelConfig, value: any) => {
        updateModelConfig(id, { [field]: value })
    }

    const fetchModelsForConfig = async (config: ModelConfig) => {
        if (!config.baseUrl) return

        setFetchingModels(prev => ({ ...prev, [config.id]: true }))
        try {
            const response = await fetch("http://localhost:8000/api/v1/models", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    base_url: config.baseUrl,
                    api_key: config.apiKey || "sk-placeholder"
                })
            })

            if (response.ok) {
                const data = await response.json()
                setAvailableModels(prev => ({ ...prev, [config.id]: data.models || [] }))
            }
        } catch (error) {
            console.error("Failed to fetch models:", error)
        } finally {
            setFetchingModels(prev => ({ ...prev, [config.id]: false }))
        }
    }

    const handleSave = () => {
        // Configs are already persisted via Zustand middleware
        setSaveStatus("✓ Configuration saved")
        setTimeout(() => setSaveStatus(""), 2000)
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Cpu className="h-5 w-5 text-purple-500" />
                    AI Model Providers
                </CardTitle>
                <CardDescription>
                    Configure multiple LLM providers for multi-model consensus analysis.
                    All API keys are stored locally in your browser.
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
                {modelConfigs.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                        <p>No model providers configured.</p>
                        <p className="text-sm">Click &quot;Add Provider&quot; to get started.</p>
                    </div>
                )}

                {modelConfigs.map((config) => (
                    <div key={config.id} className="grid gap-4 p-4 border rounded-lg relative bg-muted/20">
                        <Button
                            variant="ghost"
                            size="icon"
                            className="absolute top-2 right-2 text-destructive hover:bg-destructive/10"
                            onClick={() => handleRemoveConfig(config.id)}
                        >
                            <Trash2 className="h-4 w-4" />
                        </Button>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Provider Name</Label>
                                <Input
                                    value={config.name}
                                    onChange={(e) => handleUpdate(config.id, "name", e.target.value)}
                                    placeholder="e.g., My GPT-4"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Base URL</Label>
                                <Input
                                    value={config.baseUrl}
                                    onChange={(e) => handleUpdate(config.id, "baseUrl", e.target.value)}
                                    placeholder="https://api.openai.com/v1"
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>API Key</Label>
                                <Input
                                    type="password"
                                    value={config.apiKey}
                                    onChange={(e) => handleUpdate(config.id, "apiKey", e.target.value)}
                                    placeholder="sk-..."
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Model</Label>
                                <div className="flex gap-2">
                                    <select
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                        value={config.model}
                                        onChange={(e) => handleUpdate(config.id, "model", e.target.value)}
                                    >
                                        {/* Show fetched models */}
                                        {(availableModels[config.id] || []).map(m => (
                                            <option key={m.id} value={m.id}>{m.name}</option>
                                        ))}

                                        {/* Always show current model if not in list */}
                                        {config.model && !(availableModels[config.id] || []).some(m => m.id === config.model) && (
                                            <option value={config.model}>{config.model}</option>
                                        )}

                                        {/* Placeholder if no models */}
                                        {(availableModels[config.id] || []).length === 0 && !config.model && (
                                            <option value="" disabled>Click refresh to load</option>
                                        )}
                                    </select>
                                    <Button
                                        variant="outline"
                                        size="icon"
                                        onClick={() => fetchModelsForConfig(config)}
                                        disabled={fetchingModels[config.id]}
                                    >
                                        <RefreshCw className={`h-4 w-4 ${fetchingModels[config.id] ? 'animate-spin' : ''}`} />
                                    </Button>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center space-x-2 pt-2">
                            <Switch
                                checked={config.enabled}
                                onCheckedChange={(val) => handleUpdate(config.id, "enabled", val)}
                            />
                            <Label>Enable for Consensus Analysis</Label>
                        </div>
                    </div>
                ))}

                <div className="flex justify-between items-center pt-4 border-t">
                    <Button variant="outline" onClick={handleAddConfig}>
                        <Plus className="mr-2 h-4 w-4" /> Add Provider
                    </Button>

                    <div className="flex items-center gap-4">
                        {saveStatus && <span className="text-sm text-green-600">{saveStatus}</span>}
                        <Button onClick={handleSave}>
                            <Save className="mr-2 h-4 w-4" /> Save Changes
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}
