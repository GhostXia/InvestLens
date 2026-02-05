"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"

/**
 * ThemeProvider Component
 * 
 * Wraps the application with `next-themes` provider to enable light/dark mode switching.
 * This client-side component handles the `class` attribute manipulation on the HTML tag
 * to apply Tailwind's dark utility classes.
 * 
 * @param {React.ComponentProps<typeof NextThemesProvider>} props - Props passed down to next-themes provider
 * @returns {JSX.Element} The logic wrapper for theme context
 */
export function ThemeProvider({
    children,
    ...props
}: React.ComponentProps<typeof NextThemesProvider>) {
    return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
