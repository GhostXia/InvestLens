/**
 * API Configuration Utility
 * 
 * Provides centralized logic for determining the backend API URL.
 * Automatically adapts to the current environment (Localhost vs Network).
 */

export const getApiUrl = (path: string = "") => {
    // If we're on the client side, we can use window.location
    if (typeof window !== "undefined") {
        const hostname = window.location.hostname;
        // Assume backend is on port 8000 on the same host
        return `http://${hostname}:8000${path.startsWith("/") ? path : `/${path}`}`;
    }

    // Fallback for SSR
    return `http://localhost:8000${path.startsWith("/") ? path : `/${path}`}`;
};
