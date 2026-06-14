export default function Home() {
    return (
        <div className="space-y-8">
            <section className="text-center space-y-4 py-12">
                <h1 className="text-4xl font-bold tracking-tight">
                    Welcome to Thrive Tech Hub Learning
                </h1>
                <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                    A production-grade React learning project that mirrors real-world architecture and best practices.
                </p>
            </section>

            <section className="grid md:grid-cols-3 gap-6">
                <div className="p-6 border rounded-lg space-y-2">
                    <h2 className="text-2xl font-semibold">React Router</h2>
                    <p className="text-muted-foreground">
                        Learn client-side routing with React Router v6, the industry standard for React navigation.
                    </p>
                </div>

                <div className="p-6 border rounded-lg space-y-2">
                    <h2 className="text-2xl font-semibold">TanStack Query</h2>
                    <p className="text-muted-foreground">
                        Master data fetching, caching, and synchronization with TanStack Query (formerly React Query).
                    </p>
                </div>

                <div className="p-6 border rounded-lg space-y-2">
                    <h2 className="text-2xl font-semibold">Tailwind CSS</h2>
                    <p className="text-muted-foreground">
                        Build modern interfaces with utility-first CSS and Shadcn UI components.
                    </p>
                </div>
            </section>

            <section className="bg-muted p-8 rounded-lg">
                <h2 className="text-2xl font-semibold mb-4">Learning Objectives</h2>
                <ul className="space-y-2 list-disc list-inside">
                    <li>Understand production React architecture patterns</li>
                    <li>Integrate with headless CMS (Ghost) via REST API</li>
                    <li>Write type-safe code with TypeScript</li>
                    <li>Build reusable component libraries</li>
                    <li>Implement testing with Vitest</li>
                    <li>Prepare for production deployment</li>
                </ul>
            </section>
        </div>
    )
}
