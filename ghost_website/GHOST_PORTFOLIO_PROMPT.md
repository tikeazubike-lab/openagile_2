# Ghost.js Portfolio Website Development Prompt

## Project Overview

Create a Ghost.js-based portfolio website for a freelance software developer, DevOps engineer, and tech admin support personnel. The site has a 70% focus on blogs about health and technology for the over-40s demographic, with the remaining content covering professional portfolio elements.

### Core Objectives
1. **Portfolio Site**: Showcase professional services, projects, skills, and testimonials
2. **Health & Tech Blog (70%)**: Content focused on health and technology insights for professionals over 40
3. **Content Pipeline**: Automated content ingestion from social media platforms → Gmail → vetting/correction → Ghost publication
4. **Development Approach**: MVP first on demo environment, then migrate to production

---

## Technical Requirements

### Hosting & Infrastructure
- **Platform**: Docker (self-hosted)
- **Database**: PostgreSQL (integrate with existing Docker stack PostgreSQL)
- **Ghost Version**: Use latest stable release (at the time of implementation)
- **Deployment Environment**: Two separate instances
  - Demo environment (for testing and initial development)
  - Production environment (final live site)
- **Domains**: Separate domains for demo and production
  - You have one domain registered; recommend approach for acquiring/setting up second domain

### Theme & Design
- **Theme Type**: Custom Ghost theme (built from scratch)
- **Design Style**: Modern minimalist
  - Clean, simple design with ample white space
  - High readability optimized for over-40 audience
  - Responsive across all devices
  - Accessible (WCAG AA compliance recommended)
- **Key Design Considerations**:
  - Clear typography hierarchy
  - Large, readable fonts for the target demographic
  - High contrast for readability
  - Intuitive navigation

### Technology Stack
- **Ghost.js**: Content management system
- **Docker**: Containerization
- **Python**: Custom automation scripts
- **PostgreSQL**: Database (existing in Docker stack)
- **Google Analytics**: Analytics integration
- **Third-party form service**: Contact form implementation (recommend service)
- **Existing Infrastructure**: You have Traefik, n8n, PostgreSQL, Gitea in your Docker stack (can leverage as needed)

---

## Content Requirements

### Blog Categories & Focus

**Primary Focus (70%)**
- Health and Technology for the Over-40s
  - Topics may include: maintaining health in tech careers, technology for healthy aging, ergonomics, wellness for developers, work-life balance, technology solutions for health challenges common in the 40+ demographic

**Secondary Categories (30%)**
- DevOps Tutorials: Technical guides, how-tos, best practices
- Tech Insights: Commentary on tech trends, industry developments, analysis
- Health Tips: Ergonomics, wellness, work-life balance for tech professionals
- Freelancing Tips: Advice for freelance tech workers, client management, pricing

### Content Publishing Workflow

**Social Media Integration**
- Platforms to integrate:
  - Twitter/X
  - Instagram
  - LinkedIn
  - Reddit

**Gmail Workflow (Semi-Automated)**
Content flows from social media platforms to Gmail inbox via:
1. API integration (preferred)
2. RSS to email conversion
3. Digest emails from platforms

**Content Approval Pipeline**
- Agent should recommend best practice workflow (examples to consider):
  - Email parsing creates Ghost draft → User reviews in Ghost admin → Preview → Publish
  - User reviews email content → Create Ghost draft → Preview → Publish
  - Email parsing creates draft → User edits → Preview → Publish
- All content requires vetting, correction, and approval before publishing
- User must review and approve every post before it goes live

**Publishing Frequency**
- Multiple posts per week (variable based on social media content volume)
- No strict schedule initially

---

## Portfolio Elements

### Pages & Sections Required

**1. Home Page**
- Introduction/hero section
- Featured blog posts (prioritize health & tech over-40s content)
- Brief overview of services
- Call-to-action for newsletter signup

**2. Projects/Gallery Page**
- Display completed projects with:
  - Project images/screenshots
  - Case study descriptions
  - Technology stack used for each project
  - Links to live demos (if available)

**3. Skills & Technologies Page**
- List and categorize technical skills
- Highlight expertise in:
  - Software Development
  - DevOps
  - Tech Administration/Support
  - Relevant tools and platforms

**4. Services Page**
- Present freelance services as packages:
  - Service descriptions
  - Pricing tiers/packages
  - Clear call-to-action (contact for booking/inquiries)
  - Service deliverables outlined

**5. Testimonials Page**
- Display client testimonials with:
  - Client name
  - Company name
  - Quote/testimonial text
  - Client photo (if available)
  - Optional: project or service worked on together

**6. About Page**
- Professional background
- Expertise areas
- Why health & tech for over-40s focus
- Personal approach to freelancing

**7. Contact Page**
- Contact form (third-party service integration)
- Social media links
- Email contact option
- Response time expectations

---

## Integration Requirements

### Social Media → Gmail → Ghost Pipeline
**Phase 1: MVP (Demo Environment)**
Implement a basic content ingestion workflow using Python scripts:
- Fetch content from social platforms (via APIs where possible, or RSS feeds)
- Convert to email format and send to Gmail
- Manual extraction/copy-paste for initial testing

**Phase 2: Enhanced (Post-MVP)**
Develop more sophisticated Python automation:
- Parse emails automatically
- Create Ghost draft posts programmatically
- Extract metadata (images, tags, categories)
- Assign appropriate tags/categories automatically
- Notify user of new drafts requiring review

### Third-Party Integrations
- **Contact Form**: Recommend and integrate reliable third-party form service (e.g., Formspree, Typeform, Netlify Forms)
- **Newsletter**: Agent should recommend best approach (Ghost native vs external service)
- **Google Analytics**: Full GA4 integration
- **Affiliate Links**: Agent should determine best placement strategy (in-content, sidebar, resources page)

### APIs & Webhooks (Where Applicable)
- Social media platform APIs (Twitter/X, Instagram, LinkedIn, Reddit)
- Ghost API for content management
- Gmail API for email parsing
- Third-party form service webhook

---

## SEO & Analytics

### SEO Requirements
- **Basic Setup** (Priority for MVP):
  - Meta titles and descriptions for all pages
  - XML sitemap
  - Robots.txt configuration
  - Structured data markup (schema.org)
  - Canonical URLs

- **Local Presence** (Priority for MVP):
  - Local SEO optimization for freelance services
  - Geographic targeting configuration

- **Keyword Ranking** (Priority for MVP):
  - Target keywords related to:
    - Health and technology for over-40s
    - DevOps services
    - Freelance software development
    - Tech administration/support
  - SEO-friendly URL structure
  - Image alt text optimization

### Analytics
- **Google Analytics (GA4)**: Full implementation with:
  - Page view tracking
  - Event tracking (form submissions, affiliate link clicks)
  - Custom dimensions for blog categories
  - Conversion tracking (newsletter signups, contact form submissions)

---

## Monetization Strategy

### 1. Freelance Services Promotion
- Promote services across site
- Clear pricing/packages on Services page
- Calls-to-action in blog posts when relevant

### 2. Newsletter
- Email list building for future opportunities
- Newsletter signup form on homepage and throughout site
- Regular newsletter with curated content

### 3. Affiliate Links
- Agent should determine optimal placement strategy
- Recommend products/services relevant to target audience
- Ensure compliance with disclosure requirements

---

## Development Phases

### Phase 1: MVP - Demo Environment
**Goal**: Basic functional site for testing

**Deliverables**:
1. Ghost instance running in Docker with PostgreSQL
2. Custom theme (basic modern minimalist design)
3. Essential pages created (Home, About, Contact, Services, Blog)
4. Basic social media → Gmail manual workflow
5. Third-party contact form integrated
6. Google Analytics basic setup
7. Basic SEO configuration
8. Portfolio pages with placeholder content
9. Newsletter signup functionality
10. Testing environment on demo domain

**Timeline**: 1-2 weeks (adjust based on complexity)

### Phase 2: Enhanced Features (Post-MVP)
**Goal**: Advanced features and automation

**Deliverables**:
1. Automated Python scripts for content pipeline:
   - Social media content fetching
   - Email parsing and Ghost draft creation
   - Metadata extraction and tagging
2. Enhanced portfolio pages with real content
3. Advanced SEO optimization
4. Additional integrations as needed
5. Performance optimization
6. Mobile responsiveness refinement

**Timeline**: Determine after MVP review

### Phase 3: Production Migration
**Goal**: Deploy to production environment

**Deliverables**:
1. Agent should recommend best migration approach:
   - Ghost export/import between instances
   - Database migration between containers
   - Fresh install with content migration
2. Content migration from demo to production
3. Domain configuration for production
4. SSL/TLS configuration
5. Final testing and verification

---

## Best Practices to Follow

### Code Quality
- Clean, well-commented code
- Follow language-specific conventions (Python PEP 8, etc.)
- Use environment variables for sensitive data
- Implement error handling and logging
- Version control with Git

### Security
- Secure API credentials management
- HTTPS/SSL for all environments
- Regular security updates
- Input validation and sanitization
- Rate limiting on API calls

### Performance
- Optimize images for web
- Lazy loading for images
- Minimize external dependencies
- Caching strategy
- Database query optimization

### Accessibility
- WCAG AA compliance
- Keyboard navigation
- Screen reader compatibility
- Alt text for all images
- Sufficient color contrast

---

## Deliverables

At each phase completion, provide:

1. **Documentation**:
   - Setup and configuration instructions
   - Deployment guide
   - Troubleshooting common issues
   - API usage documentation
   - Python script documentation

2. **Code Repository**:
   - Well-organized Git repository
   - Docker Compose configuration
   - Ghost theme source code
   - Python automation scripts
   - Configuration files (excluding secrets)

3. **Testing Verification**:
   - Test plan and results
   - Known issues or limitations
   - Performance benchmarks

4. **Migration Guide** (for production phase):
   - Step-by-step migration process
   - Rollback procedures
   - Post-migration checklist

---

## Important Notes

- **Docker Infrastructure**: You have an existing Docker Compose setup with Traefik, PostgreSQL, n8n, Gitea, Woodpecker CI/CD. Leverage these where appropriate.
- **Demo First**: Always develop and test on the demo environment first. Do not make changes to production until migration phase.
- **Content Approval**: Every blog post must be manually reviewed and approved before publishing. No automated publishing without human approval.
- **Target Audience**: Design for the over-40 demographic - prioritize readability, clarity, and accessibility.
- **Flexibility**: This is an MVP approach. Be prepared to iterate and refine based on testing and user feedback.
- **Agent Discretion**: Where the prompt says "Agent should recommend" or "Agent decides," use your best judgment based on industry best practices and the project goals.

---

## Getting Started

When you begin this project:
1. Confirm understanding of all requirements
2. Propose architecture and technical approach
3. Recommend any third-party services (contact form, newsletter, etc.)
4. Outline the development plan with timelines
5. Identify any dependencies or prerequisites
6. Ask clarifying questions if any requirements are unclear

This is a complex project with multiple components. Take a methodical approach, starting with the MVP demo environment and building incrementally. Quality and functionality are more important than speed at this stage.
