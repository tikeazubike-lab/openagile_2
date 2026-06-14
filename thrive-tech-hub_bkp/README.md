# Thrive Tech Hub - Learning Project

> 🎓 A production-grade React learning project that mirrors real-world architecture

## Overview

This project is designed to help you transition from basic React tutorials to production-ready development. It replicates the architecture, tech stack, and patterns used in the [`thrive-tech-hub`](../thrive-tech-hub) production project.

## Tech Stack

- **React 18** - Modern functional components with hooks
- **TypeScript** - Type-safe development
- **Vite** - Lightning-fast build tooling
- **React Router v6** - Client-side routing
- **TanStack Query** - Data fetching and caching
- **Tailwind CSS** - Utility-first styling
- **Shadcn UI** - Accessible component library
- **Vitest** - Testing framework

## Project Structure

```
thrive-tech-hub-learning/
├── src/
│   ├── components/
│   │   ├── ui/          # Shadcn UI components (to be added)
│   │   ├── layout/      # Layout components (Header, Footer, Layout)
│   │   └── features/    # Feature-specific components
│   ├── pages/           # Page components (Home, Blog, About)
│   ├── lib/             # Utilities and helpers
│   ├── hooks/           # Custom React hooks
│   ├── types/           # TypeScript type definitions
│   └── test/            # Test files
├── public/              # Static assets
└── [config files]       # Vite, TypeScript, Tailwind configs
```

## Getting Started

### 1. Install Dependencies

```bash
npm install
```

###2. Run Development Server

```bash
npm run dev
```

Visit `http://localhost:5173` to see your app!

### 3. Explore the Code

- **Routing**: Check `src/App.tsx` to see React Router setup
- **Layout**: Explore `src/components/layout/` for reusable layouts
- **Pages**: View `src/pages/` for page components
- **Styling**: See `src/index.css` for Tailwind configuration

## Learning Path

### Phase 1: Foundation (Current) ✅
- [x] React Router v6 routing
- [x] Tailwind CSS styling
- [x] Basic component structure
- [x] TypeScript configuration

### Phase 2: Data Fetching (Next)
- [ ] TanStack Query integration
- [ ] Ghost Content API setup
- [ ] Custom hooks for data fetching
- [ ] Loading and error states

### Phase 3: Advanced Components
- [ ] Shadcn UI components
- [ ] Reusable component patterns
- [ ] Performance optimization
- [ ] Accessibility implementation

### Phase 4: Testing
- [ ] Vitest configuration
- [ ] Component tests
- [ ] Hook tests
- [ ] Integration tests

### Phase 5: Production
- [ ] Docker configuration
- [ ] CI/CD pipeline
- [ ] Deployment setup

## Available Scripts

```bash
npm run dev        # Start development server
npm run build      # Build for production
npm run preview    # Preview production build
npm run lint       # Run ESLint
npm run test       # Run tests
npm run test:watch # Run tests in watch mode
```

## Learning Resources

- [React Documentation](https://react.dev/)
- [React Router Docs](https://reactrouter.com/)
- [TanStack Query Docs](https://tanstack.com/query/)
- [Tailwind CSS Docs](https://tailwindcss.com/)
- [Shadcn UI Docs](https://ui.shadcn.com/)
- [TypeScript Docs](https://www.typescriptlang.org/)

## Comparing to Production

This project mirrors [`thrive-tech-hub`](../thrive-tech-hub) but with:

✅ **Included**: Core architecture, routing, styling, TypeScript patterns  
🔜 **Coming Soon**: Ghost CMS integration, advanced components, Docker, CI/CD  
📚 **Learning Focus**: Understanding patterns before production complexity

## Next Steps

1. **Run the app** and explore the three pages
2. **Study the code** - read through components and understand the structure
3. **Make changes** - try modifying styles, adding content, creating new components
4. **Move to Phase 2** - integrate with Ghost CMS for dynamic data

---

**Ready to learn?** Start by running `npm install && npm run dev`!
