import { create } from 'zustand'
import { persist } from 'zustand/middleware'

/**
 * Represents a single LLM model configuration.
 */
export interface ModelConfig {
    id: string
    name: string
    baseUrl: string
    apiKey: string
    model: string
    enabled: boolean
}

interface SettingsState {
    // Legacy single-model config (kept for backward compatibility)
    apiKey: string
    baseUrl: string
    model: string

    // Multi-model configuration
    modelConfigs: ModelConfig[]

    quantModeEnabled: boolean
    ddgEnabled: boolean
    yahooEnabled: boolean
    akshareEnabled: boolean
    customEnabled: boolean

    setApiKey: (key: string) => void
    setBaseUrl: (url: string) => void
    setModel: (model: string) => void
    setModelConfigs: (configs: ModelConfig[]) => void
    addModelConfig: (config: ModelConfig) => void
    removeModelConfig: (id: string) => void
    updateModelConfig: (id: string, updates: Partial<ModelConfig>) => void
    setQuantModeEnabled: (enabled: boolean) => void
    setDdgEnabled: (enabled: boolean) => void
    setYahooEnabled: (enabled: boolean) => void
    setAkshareEnabled: (enabled: boolean) => void
    setCustomEnabled: (enabled: boolean) => void
    clearAll: () => void
}

/**
 * Settings Store
 * 
 * Manages global user preferences and sensitive credentials.
 * Uses 'persist' middleware to save state to localStorage.
 * 
 * Security Note: API Keys are stored in the browser's localStorage.
 * They are never sent to our backend database, only passed in headers
 * for on-the-fly requests.
 */
export const useSettingsStore = create<SettingsState>()(
    persist(
        (set) => ({
            apiKey: "",
            baseUrl: "https://api.openai.com/v1",
            model: "gpt-4",
            modelConfigs: [],
            quantModeEnabled: false,
            ddgEnabled: false,
            yahooEnabled: true,
            akshareEnabled: true,
            customEnabled: true,
            setApiKey: (key) => set({ apiKey: key }),
            setBaseUrl: (url) => set({ baseUrl: url }),
            setModel: (model) => set({ model: model }),
            setModelConfigs: (configs) => set({ modelConfigs: configs }),
            addModelConfig: (config) => set((state) => ({
                modelConfigs: [...state.modelConfigs, config]
            })),
            removeModelConfig: (id) => set((state) => ({
                modelConfigs: state.modelConfigs.filter(c => c.id !== id)
            })),
            updateModelConfig: (id, updates) => set((state) => ({
                modelConfigs: state.modelConfigs.map(c =>
                    c.id === id ? { ...c, ...updates } : c
                )
            })),
            setQuantModeEnabled: (enabled) => set({ quantModeEnabled: enabled }),
            setDdgEnabled: (enabled) => set({ ddgEnabled: enabled }),
            setYahooEnabled: (enabled) => set({ yahooEnabled: enabled }),
            setAkshareEnabled: (enabled) => set({ akshareEnabled: enabled }),
            setCustomEnabled: (enabled) => set({ customEnabled: enabled }),
            clearAll: () => set({
                apiKey: "",
                baseUrl: "https://api.openai.com/v1",
                model: "gpt-4",
                modelConfigs: [],
                quantModeEnabled: false,
                ddgEnabled: false,
                yahooEnabled: true,
                akshareEnabled: true,
                customEnabled: true
            }),
        }),
        {
            name: 'investlens-settings',
        }
    )
)

