import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface SettingsState {
    apiKey: string
    baseUrl: string
    model: string
    quantModeEnabled: boolean
    setApiKey: (key: string) => void
    setBaseUrl: (url: string) => void
    setModel: (model: string) => void
    setQuantModeEnabled: (enabled: boolean) => void
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
            setApiKey: (key) => set({ apiKey: key }),
            setBaseUrl: (url) => set({ baseUrl: url }),
            setModel: (model) => set({ model: model }),
            setQuantModeEnabled: (enabled) => set({ quantModeEnabled: enabled }),
            clearAll: () => set({
                apiKey: "",
                baseUrl: "https://api.openai.com/v1",
                model: "gpt-4",
                quantModeEnabled: false
            }),
        }),
        {
            name: 'investlens-settings', // name of the item in the storage (must be unique)
        }
    )
)
