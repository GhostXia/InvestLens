"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { Globe } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useTranslations } from "next-intl"
import { locales, localeNames, type Locale } from "@/i18n"

/**
 * LanguageToggle Component
 * 
 * A dropdown menu for switching between supported languages.
 * Updates the NEXT_LOCALE cookie and refreshes the page.
 * 
 * @returns {JSX.Element} The language toggle dropdown
 */
export function LanguageToggle() {
    const t = useTranslations("language")
    const router = useRouter()

    const switchLanguage = (locale: Locale) => {
        // Set cookie for language preference
        document.cookie = `NEXT_LOCALE=${locale};path=/;max-age=31536000`
        // Refresh the page to apply the new language
        router.refresh()
    }

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="outline" size="icon">
                    <Globe className="h-[1.2rem] w-[1.2rem]" />
                    <span className="sr-only">{t("switch")}</span>
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
                {locales.map((locale) => (
                    <DropdownMenuItem
                        key={locale}
                        onClick={() => switchLanguage(locale)}
                    >
                        {localeNames[locale]}
                    </DropdownMenuItem>
                ))}
            </DropdownMenuContent>
        </DropdownMenu>
    )
}
