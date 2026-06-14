import { Link } from 'react-router-dom'

export default function Header() {
    return (
        <header className="border-b">
            <div className="container mx-auto px-4 py-4">
                <nav className="flex items-center justify-between">
                    <Link to="/" className="text-2xl font-bold">
                        Thrive Tech Hub
                    </Link>
                    <ul className="flex gap-6">
                        <li>
                            <Link to="/" className="hover:text-primary transition-colors">
                                Home
                            </Link>
                        </li>
                        <li>
                            <Link to="/blog" className="hover:text-primary transition-colors">
                                Blog
                            </Link>
                        </li>
                        <li>
                            <Link to="/about" className="hover:text-primary transition-colors">
                                About
                            </Link>
                        </li>
                    </ul>
                </nav>
            </div>
        </header>
    )
}
