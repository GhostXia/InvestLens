import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface SettingsState {
    apiKey: string
    quantModeEnabled: boolean
    setApiKey: (key: string) => void
    setQuantModeEnabled: (enabled: boolean) => void
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
            quantModeEnabled: false,
            setApiKey: (key) => set({ apiKey: key }),
            setQuantModeEnabled: (enabled) => set({ quantModeEnabled: enabled }),
        }),
        {
            name: 'investlens-settings', // name of the item in the storage (must be unique)
        }
    )
)
