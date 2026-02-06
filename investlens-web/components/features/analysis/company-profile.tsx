"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Building2, Users, Globe, Briefcase } from "lucide-react"

interface CompanyProfileProps {
    description?: string
    sector?: string
    industry?: string
    employees?: string | number
    website?: string
    city?: string
    country?: string
    exchange?: string
    currency?: string
    isLoading?: boolean
}

export function CompanyProfile({
    description,
    sector,
    industry,
    employees,
    website,
    isLoading
}: CompanyProfileProps) {

    if (isLoading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                        <Building2 className="h-5 w-5" />
                        Company Profile
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 animate-pulse">
                    <div className="h-4 bg-muted rounded w-3/4"></div>
                    <div className="h-4 bg-muted rounded w-full"></div>
                    <div className="h-4 bg-muted rounded w-5/6"></div>
                    <div className="flex gap-2 pt-2">
                        <div className="h-6 w-20 bg-muted rounded"></div>
                        <div className="h-6 w-24 bg-muted rounded"></div>
                    </div>
                </CardContent>
            </Card>
        )
    }

    if (!description && !sector) {
        return null;
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                    <Building2 className="h-5 w-5" />
                    Company Profile
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Badges / Meta Info */}
                <div className="flex flex-wrap gap-2">
                    {sector && sector !== "N/A" && (
                        <Badge variant="secondary" className="flex items-center gap-1">
                            <Briefcase className="h-3 w-3" />
                            {sector}
                        </Badge>
                    )}
                    {industry && industry !== "N/A" && (
                        <Badge variant="outline" className="flex items-center gap-1">
                            <Building2 className="h-3 w-3" />
                            {industry}
                        </Badge>
                    )}
                    {employees && employees !== "N/A" && (
                        <Badge variant="outline" className="flex items-center gap-1">
                            <Users className="h-3 w-3" />
                            {parseInt(String(employees)).toLocaleString()} Employees
                        </Badge>
                    )}
                </div>

                {/* Description */}
                <div className="text-sm text-foreground/80 leading-relaxed max-h-[200px] overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-muted">
                    {description === "No description available." ? (
                        <span className="text-muted-foreground italic">No description available for this asset.</span>
                    ) : (
                        description
                    )}
                </div>

                {/* Additional Links */}
                {website && website !== "N/A" && (
                    <div className="pt-2 border-t text-sm">
                        <a
                            href={website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-primary hover:underline w-fit"
                        >
                            <Globe className="h-3 w-3" />
                            Official Website
                        </a>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}
