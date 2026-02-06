import Link from "next/link"
import { BookOpen, Lightbulb, Shield, HelpCircle, ArrowRight } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { WIKI_ARTICLES } from "@/lib/wiki-data"

function getCategoryIcon(category: string) {
    switch (category) {
        case "Guide": return <BookOpen className="h-6 w-6 text-blue-500" />
        case "Concepts": return <Lightbulb className="h-6 w-6 text-yellow-500" />
        case "Features": return <ArrowRight className="h-6 w-6 text-green-500" /> // Features icon
        case "FAQ": return <HelpCircle className="h-6 w-6 text-purple-500" />
        default: return <Shield className="h-6 w-6 text-gray-500" />
    }
}

export default function WikiPage() {
    const categories = Array.from(new Set(WIKI_ARTICLES.map(a => a.category)))

    return (
        <div className="container mx-auto py-10 max-w-5xl">
            <div className="text-center mb-12 space-y-4">
                <h1 className="text-4xl font-extrabold tracking-tight">InvestLens Wiki</h1>
                <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                    探索 InvestLens 的核心概念、功能指南和常见问题解答。
                </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {WIKI_ARTICLES.map((article) => (
                    <Link key={article.slug} href={`/wiki/${article.slug}`} className="group">
                        <Card className="h-full transition-all hover:shadow-lg hover:border-primary/50">
                            <CardHeader>
                                <div className="flex items-center justify-between mb-2">
                                    <div className="p-2 bg-muted rounded-full group-hover:bg-primary/10 transition-colors">
                                        {getCategoryIcon(article.category)}
                                    </div>
                                    <Badge variant="secondary">{article.category}</Badge>
                                </div>
                                <CardTitle className="group-hover:text-primary transition-colors">
                                    {article.title}
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <CardDescription className="line-clamp-3">
                                    {article.description}
                                </CardDescription>
                            </CardContent>
                            <CardFooter>
                                <span className="text-sm font-medium text-muted-foreground group-hover:text-primary flex items-center gap-1 transition-colors">
                                    阅读全文 <ArrowRight className="h-4 w-4" />
                                </span>
                            </CardFooter>
                        </Card>
                    </Link>
                ))}
            </div>
        </div>
    )
}
