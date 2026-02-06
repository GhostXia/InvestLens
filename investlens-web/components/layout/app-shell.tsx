"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { LayoutDashboard, Settings, BookOpen, LineChart, PanelLeft, Github, Star } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { ThemeProvider } from "@/components/theme-provider"
import { ModeToggle } from "@/components/mode-toggle"

/**
 * Props for the AppShell wrapper
 */
interface AppShellProps {
    children: React.ReactNode
}

/**
 * AppShell Component
 * 
 * The main layout wrapper for the authenticated application.
 * Implements a responsive "Sidebar + Header" layout strategy:
 * - **Desktop**: Persistent vertical sidebar on the left.
 * - **Mobile**: Hamburger menu triggering a slide-out Sheet (sidebar).
 * 
 * Features:
 * - Automatic active route highlighting.
 * - Integrated Dark Mode toggle.
 * - Responsive design handling (hidden/flex utility classes).
 * 
 * @param {AppShellProps} props - Contain the main page content
 * @returns {JSX.Element} The scaffolded application layout
 */
export function AppShell({ children }: AppShellProps) {
    const pathname = usePathname()

    // Navigation configuration
    const routes = [
        {
            href: "/",
            label: "Dashboard",
            icon: LayoutDashboard,
            active: pathname === "/",
        },
        {
            href: "/analysis",
            label: "Analysis",
            icon: LineChart,
            active: pathname.startsWith("/analysis"),
        },
        {
            href: "/wiki",
            label: "Wiki",
            icon: BookOpen,
            active: pathname.startsWith("/wiki"),
        },
        {
            href: "/watchlist",
            label: "Watchlist",
            icon: Star,
            active: pathname.startsWith("/watchlist"),
        },
        {
            href: "/settings",
            label: "Settings",
            icon: Settings,
            active: pathname.startsWith("/settings"),
        },
    ]

    return (
        <div className="flex min-h-screen w-full flex-col bg-muted/20">
            {/* Mobile Header & Trigger */}
            <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:static sm:h-auto sm:border-0 sm:bg-transparent sm:px-6">
                <Sheet>
                    <SheetTrigger asChild>
                        <Button size="icon" variant="outline" className="sm:hidden">
                            <PanelLeft className="h-5 w-5" />
                            <span className="sr-only">Toggle Menu</span>
                        </Button>
                    </SheetTrigger>
                    <SheetContent side="left" className="sm:max-w-xs">
                        <nav className="grid gap-6 text-lg font-medium">
                            <Link
                                href="#"
                                className="group flex h-10 w-10 items-center justify-center rounded-full bg-primary text-lg font-semibold text-primary-foreground md:text-base"
                            >
                                <LineChart className="h-5 w-5 transition-all group-hover:scale-110" />
                                <span className="sr-only">InvestLens</span>
                            </Link>
                            {routes.map((route) => (
                                <Link
                                    key={route.href}
                                    href={route.href}
                                    className={cn(
                                        "flex items-center gap-4 px-2.5 text-muted-foreground hover:text-foreground",
                                        route.active && "text-foreground"
                                    )}
                                >
                                    <route.icon className="h-5 w-5" />
                                    {route.label}
                                </Link>
                            ))}
                        </nav>
                    </SheetContent>
                </Sheet>
                <div className="flex items-center gap-2 md:hidden">
                    <span className="font-bold text-lg">InvestLens</span>
                </div>
                <div className="ml-auto flex items-center gap-2">
                    <ModeToggle />
                </div>
            </header>

            {/* Main Content Area */}
            <div className="flex flex-1 overflow-hidden">
                {/* Desktop Sidebar */}
                <aside className="fixed inset-y-0 left-0 z-10 hidden w-14 flex-col border-r bg-background sm:flex">
                    <nav className="flex flex-col items-center gap-4 px-2 py-4">
                        <Link
                            href="/"
                            className="group flex h-9 w-9 items-center justify-center rounded-full bg-primary text-lg font-semibold text-primary-foreground md:h-8 md:w-8 md:text-base"
                        >
                            <LineChart className="h-4 w-4 transition-all group-hover:scale-110" />
                            <span className="sr-only">InvestLens</span>
                        </Link>
                        {routes.map((route) => (
                            // Simple sidebar implementation for collapsed state, can be expanded later
                            <Link
                                key={route.href}
                                href={route.href}
                                className={cn(
                                    "flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:text-foreground md:h-8 md:w-8",
                                    route.active && "bg-accent text-accent-foreground"
                                )}
                            >
                                <route.icon className="h-5 w-5" />
                                <span className="sr-only">{route.label}</span>
                            </Link>
                        ))}
                    </nav>
                    <nav className="mt-auto flex flex-col items-center gap-4 px-2 py-4">
                        <Link
                            href="/settings"
                            className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:text-foreground md:h-8 md:w-8"
                        >
                            <Settings className="h-5 w-5" />
                            <span className="sr-only">Settings</span>
                        </Link>
                    </nav>
                </aside>

                {/* Page Content Injection */}
                <main className="flex-1 overflow-y-auto p-4 sm:ml-14 sm:p-6 lg:p-8">
                    {children}
                </main>
            </div>

            {/* Footer */}
            <footer className="border-t bg-background py-4 px-6 sm:ml-14">
                <div className="flex items-center justify-center gap-4 text-sm text-muted-foreground">
                    <span>© 2026 InvestLens</span>
                    <span>•</span>
                    <a
                        href="https://github.com/GhostXia/InvestLens"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1.5 hover:text-foreground transition-colors"
                    >
                        <Github className="h-4 w-4" />
                        GitHub
                    </a>
                    <span>•</span>
                    <span>MIT License</span>
                </div>
            </footer>
        </div>
    )
}
