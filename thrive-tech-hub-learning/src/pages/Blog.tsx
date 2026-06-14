export default function Blog() {
    return (
        <div className="space-y-8">
            <h1 className="text-4xl font-bold">Blog</h1>
            <p className="text-lg text-muted-foreground">
                Coming soon: Integration with Ghost CMS to display blog posts dynamically.
            </p>

            <div className="grid gap-6">
                {/* Placeholder for blog posts */}
                <article className="p-6 border rounded-lg space-y-3">
                    <h2 className="text-2xl font-semibold">Sample Blog Post</h2>
                    <p className="text-muted-foreground text-sm">Published on January 31, 2026</p>
                    <p>
                        This is a placeholder for blog content. In Phase 2, we'll integrate with the Ghost Content API
                        to fetch and display real blog posts.
                    </p>
                </article>
            </div>
        </div>
    )
}
