import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Home from './pages/Home'
import Blog from './pages/Blog'
import About from './pages/About'
import Layout from './components/layout/Layout'

const queryClient = new QueryClient()

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <BrowserRouter>
                <Layout>
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/blog" element={<Blog />} />
                        <Route path="/about" element={<About />} />
                    </Routes>
                </Layout>
            </BrowserRouter>
        </QueryClientProvider>
    )
}

export default App
