export default function About() {
    return (
        <div className="max-w-3xl space-y-6">
            <h1 className="text-4xl font-bold">About This Project</h1>

            <section className="space-y-4">
                <h2 className="text-2xl font-semibold">Project Overview</h2>
                <p>
                    This is a bridge learning project designed to help you transition from basic React tutorials
                    to production-grade development. It mirrors the architecture of the{' '}
                    <code className="bg-muted px-2 py-1 rounded text-sm">thrive-tech-hub</code> production project.
                </p>
            </section>

            <section className="space-y-4">
                <h2 className="text-2xl font-semibold">Tech Stack</h2>
                <ul className="space-y-2">
                    <li><strong>React 18:</strong> Modern React with hooks and functional components</li>
                    <li><strong>TypeScript:</strong> Type-safe development</li>
                    <li><strong>Vite:</strong> Lightning-fast build tooling</li>
                    <li><strong>React Router:</strong> Client-side routing</li>
                    <li><strong>TanStack Query:</strong> Data fetching and caching</li>
                    <li><strong>Tailwind CSS:</strong> Utility-first styling</li>
                    <li><strong>Shadcn UI:</strong> Accessible component library</li>
                    <li><strong>Vitest:</strong> Testing framework</li>
                </ul>
            </section>

            <section className="space-y-4">
                <h2 className="text-2xl font-semibold">Learning Philosophy</h2>
                <p>
                    Instead of following generic tutorials, you're building a real-world project using the same
                    patterns and tools used in professional React development. This hands-on approach will prepare
                    you for peer-reviewing and contributing to production codebases.
                </p>
            </section>
        </div>
    )
}
