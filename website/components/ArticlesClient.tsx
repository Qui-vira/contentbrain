"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { SectionWrapper } from "./SectionWrapper";
import { ArrowRight, FileText, Eye } from "lucide-react";

interface Article {
  slug: string;
  title: string;
  cta_keyword: string | null;
  video_title: string | null;
  views: number | null;
  created_at: string | null;
}

export function ArticlesClient({ articles }: { articles: Article[] }) {
  return (
    <main className="min-h-screen pt-32 pb-24">
      <div className="mx-auto max-w-[1200px] px-6">
        {/* Hero */}
        <SectionWrapper>
          <div className="mb-16 text-center">
            <motion.h1
              className="text-4xl font-bold tracking-tight text-text-primary sm:text-5xl"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              Articles
            </motion.h1>
            <motion.p
              className="mx-auto mt-4 max-w-xl text-lg text-text-secondary"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              Exclusive breakdowns, frameworks, and guides from @big_quiv.
            </motion.p>
          </div>
        </SectionWrapper>

        {/* Articles Grid */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {articles.map((article, i) => (
            <SectionWrapper key={article.slug} delay={i * 0.1}>
              <Link href={`/doc/${article.slug}`}>
                <div className="group relative overflow-hidden rounded-xl border border-border bg-bg-secondary p-6 transition-all duration-300 hover:border-border-hover hover:bg-bg-tertiary">
                  <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-accent/10">
                    <FileText className="h-5 w-5 text-accent" />
                  </div>

                  <h2 className="mb-2 text-lg font-semibold text-text-primary transition-colors group-hover:text-accent">
                    {article.title}
                  </h2>

                  {article.video_title && (
                    <p className="mb-3 text-sm text-text-muted">
                      From: {article.video_title}
                    </p>
                  )}

                  {article.cta_keyword && (
                    <span className="inline-block rounded-full bg-accent/10 px-3 py-1 text-xs font-medium text-accent">
                      {article.cta_keyword}
                    </span>
                  )}

                  <div className="mt-4 flex items-center justify-between">
                    <div className="flex items-center gap-1 text-xs text-text-muted">
                      {article.views != null && article.views > 0 && (
                        <>
                          <Eye className="h-3 w-3" />
                          <span>{article.views} views</span>
                        </>
                      )}
                    </div>
                    <ArrowRight className="h-4 w-4 text-text-muted transition-transform group-hover:translate-x-1 group-hover:text-accent" />
                  </div>
                </div>
              </Link>
            </SectionWrapper>
          ))}
        </div>

        {articles.length === 0 && (
          <SectionWrapper>
            <div className="rounded-xl border border-border bg-bg-secondary p-12 text-center">
              <p className="text-text-secondary">No articles yet. Check back soon.</p>
            </div>
          </SectionWrapper>
        )}
      </div>
    </main>
  );
}
