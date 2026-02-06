import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface SettingsState {
    apiKey: string
    baseUrl: string
    model: string
    quantModeEnabled: boolean
    ddgEnabled: boolean
    yahooEnabled: boolean
    akshareEnabled: boolean
    setApiKey: (key: string) => void
    setBaseUrl: (url: string) => void
    setModel: (model: string) => void
    setQuantModeEnabled: (enabled: boolean) => void
    setDdgEnabled: (enabled: boolean) => void
    setYahooEnabled: (enabled: boolean) => void
    setAkshareEnabled: (enabled: boolean) => void
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
            quantModeEnabled: false,
            ddgEnabled: false,
            yahooEnabled: true,
            akshareEnabled: true,
            setApiKey: (key) => set({ apiKey: key }),
            setBaseUrl: (url) => set({ baseUrl: url }),
            setModel: (model) => set({ model: model }),
            setQuantModeEnabled: (enabled) => set({ quantModeEnabled: enabled }),
            setDdgEnabled: (enabled) => set({ ddgEnabled: enabled }),
            setYahooEnabled: (enabled) => set({ yahooEnabled: enabled }),
            setAkshareEnabled: (enabled) => set({ akshareEnabled: enabled }),
            clearAll: () => set({
                apiKey: "",
                baseUrl: "https://api.openai.com/v1",
                model: "gpt-4",
                quantModeEnabled: false,
                ddgEnabled: false,
                yahooEnabled: true,
                akshareEnabled: true
            }),
        }),
        {
            name: 'investlens-settings',
        }
    )
)
