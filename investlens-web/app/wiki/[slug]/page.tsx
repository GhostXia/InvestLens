"use client"

import { notFound } from "next/navigation"
import Link from "next/link"
import ReactMarkdown from 'react-markdown'
import { ArrowLeft, Calendar, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { WIKI_ARTICLES } from "@/lib/wiki-data"

interface PageProps {
    params: {
        slug: string
    }
}

export default function WikiArticlePage({ params }: PageProps) {
    const article = WIKI_ARTICLES.find(a => a.slug === params.slug)

    if (!article) {
        notFound()
    }

    return (
        <div className="container mx-auto py-8 max-w-4xl h-full flex flex-col">
            <div className="mb-8">
                <Link href="/wiki">
                    <Button variant="ghost" className="gap-2 pl-0 hover:bg-transparent hover:text-primary">
                        <ArrowLeft className="h-4 w-4" />
                        返回 Wiki 知识库
                    </Button>
                </Link>
            </div>

            <ScrollArea className="flex-1 pr-4">
                <article className="pb-20">
                    <div className="mb-8 space-y-4 border-b pb-8">
                        <div className="flex items-center gap-2">
                            <Badge>{article.category}</Badge>
                            <span className="text-sm text-muted-foreground flex items-center gap-1">
                                <Calendar className="h-3 w-3" /> 最新更新: 2026-02-06
                            </span>
                        </div>
                        <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl">
                            {article.title}
                        </h1>
                        <p className="text-xl text-muted-foreground leading-relaxed">
                            {article.description}
                        </p>
                    </div>

                    <div className="prose dark:prose-invert max-w-none prose-lg prose-headings:font-bold prose-h1:text-3xl prose-h2:text-2xl prose-a:text-primary hover:prose-a:underline">
                        <ReactMarkdown>
                            {article.content}
                        </ReactMarkdown>
                    </div>
                </article>
            </ScrollArea>
        </div>
    )
}
