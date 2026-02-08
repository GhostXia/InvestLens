import { getApiUrl } from "./api-config";

interface FetchOptions extends RequestInit {
    params?: Record<string, string | number | boolean>;
}

/**
 * Universal API Fetcher
 * ---------------------
 * Automatically handles:
 * 1. URL Resolution (via getApiUrl)
 * 2. Query Parameter Serialization
 * 3. Error Status Codes (throws Error with backend message)
 * 4. Response Unwrapping (extracts 'data' from APIResponse)
 */
export async function fetchAPI<T = any>(endpoint: string, options: FetchOptions = {}): Promise<T> {
    const { params, headers, ...fetchOptions } = options;

    // 1. Build URL
    let url = getApiUrl(endpoint);
    if (params) {
        const searchParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                searchParams.append(key, String(value));
            }
        });
        url += `?${searchParams.toString()}`;
    }

    // 2. Default Headers
    const defaultHeaders: HeadersInit = {
        "Content-Type": "application/json",
        // Add any auth headers here if needed in future
    };

    // 3. Make Request
    const response = await fetch(url, {
        headers: { ...defaultHeaders, ...(headers || {}) },
        ...fetchOptions
    });

    // 4. Handle HTTP Errors
    if (!response.ok) {
        let errorMessage = `API Error: ${response.status} ${response.statusText}`;
        try {
            const errorData = await response.json();
            // Backend ErrorResponse: { code, message, detail, trace_id }
            if (errorData.detail) errorMessage = errorData.detail;
            else if (errorData.message) errorMessage = errorData.message;
            else if (errorData.error) errorMessage = typeof errorData.error === 'string' ? errorData.error : JSON.stringify(errorData.error);
        } catch (e) {
            // Fallback to default message if JSON parse fails
        }
        throw new Error(errorMessage);
    }

    // 5. Parse & Unwrap Response
    // Some endpoints might return 204 No Content
    if (response.status === 204) {
        return {} as T;
    }

    let result;
    try {
        result = await response.json();
    } catch (e) {
        // If not JSON, return text or empty (unlikely for our API)
        return {} as T;
    }

    // AUTO-UNWRAP: Check if it matches our APIResponse wrapper
    // APIResponse<T> { code: int, message: string, data: T, trace_id: string }
    if (result && typeof result === 'object' && 'data' in result && 'code' in result) {
        return result.data as T;
    }

    // Return raw if no wrapper detected
    return result as T;
}
