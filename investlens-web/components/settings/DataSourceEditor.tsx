"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Trash2, Plus, Save } from "lucide-react"

interface DataSource {
    name: string
    provider_type: string
    api_key: string
    endpoint_override: string
    enabled: boolean
}

const API_BASE_URL = "http://localhost:8000" // Should be env var in production

export function DataSourceEditor() {
    const [sources, setSources] = useState<DataSource[]>([])
    const [loading, setLoading] = useState(false)
    const [status, setStatus] = useState<string>("")

    useEffect(() => {
        fetchSources()
    }, [])

    const fetchSources = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/config/sources`)
            if (res.ok) {
                const data = await res.json()
                setSources(data)
            }
        } catch (err) {
            console.error("Failed to load sources", err)
        }
    }

    const saveSources = async () => {
        setLoading(true)
        setStatus("")
        try {
            const res = await fetch(`${API_BASE_URL}/config/sources`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ sources }),
            })

            if (res.ok) {
                setStatus("Configuration saved and reloaded.")
            } else {
                setStatus("Failed to save.")
            }
        } catch (err) {
            setStatus("Error saving configuration.")
        } finally {
            setLoading(false)
        }
    }

    const addSource = () => {
        setSources([
            ...sources,
            {
                name: "New Alpha Vantage",
                provider_type: "alpha_vantage",
                api_key: "",
                endpoint_override: "",
                enabled: true,
            },
        ])
    }

    const removeSource = (index: number) => {
        const newSources = [...sources]
        newSources.splice(index, 1)
        setSources(newSources)
    }

    const updateSource = (index: number, field: keyof DataSource, value: any) => {
        const newSources = [...sources]
        // @ts-ignore
        newSources[index][field] = value
        setSources(newSources)
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>Data Sources</CardTitle>
                <CardDescription>
                    Configure external data providers. Changes apply immediately upon save.
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
                {sources.map((source, index) => (
                    <div key={index} className="grid gap-4 p-4 border rounded-lg relative">
                        <Button
                            variant="ghost"
                            size="icon"
                            className="absolute top-2 right-2 text-destructive hover:bg-destructive/10"
                            onClick={() => removeSource(index)}
                        >
                            <Trash2 className="h-4 w-4" />
                        </Button>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Name</Label>
                                <Input
                                    value={source.name}
                                    onChange={(e) => updateSource(index, "name", e.target.value)}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Provider Type</Label>
                                <Select
                                    value={source.provider_type}
                                    onValueChange={(val) => updateSource(index, "provider_type", val)}
                                >
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="alpha_vantage">Alpha Vantage</SelectItem>
                                        <SelectItem value="yfinance">YFinance (Internal)</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label>API Key</Label>
                            <Input
                                type="password"
                                value={source.api_key}
                                onChange={(e) => updateSource(index, "api_key", e.target.value)}
                                placeholder="Required for Alpha Vantage"
                            />
                        </div>

                        <div className="flex items-center space-x-2">
                            <Switch
                                checked={source.enabled}
                                onCheckedChange={(val: boolean) => updateSource(index, "enabled", val)}
                            />
                            <Label>Enabled</Label>
                        </div>
                    </div>
                ))}

                <div className="flex justify-between items-center pt-4">
                    <Button variant="outline" onClick={addSource}>
                        <Plus className="mr-2 h-4 w-4" /> Add Source
                    </Button>

                    <div className="flex items-center gap-4">
                        {status && <span className="text-sm text-green-600">{status}</span>}
                        <Button onClick={saveSources} disabled={loading}>
                            <Save className="mr-2 h-4 w-4" /> {loading ? "Saving..." : "Save Changes"}
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}
