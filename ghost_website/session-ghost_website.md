# Ghost.js portfolio with blog automation for health/tech over-40s, prompt for AI agents

**Session ID:** ses_441bc1f7bffe6basKhnAS83ZBP
**Created:** 1/14/2026, 9:47:58 PM
**Updated:** 1/14/2026, 10:06:32 PM

---

## User

Create a prompt that is AI agent agnostic. I need to create a Ghost. js-based website.  This is a portfolio site, but it has a 70% focus on blogs about health and technology for the over 40s. I am a software developer, DevOps, and tech admin support personnel. Currently freelancing. Most of the posts for the blogs will be coming automatically from social media and will be sent to me gmail account for vetting, correction and posting before publishing to my website. I will be using a demo website to test run this before moving it to the intended website. Ask all the question like you are the BA elucidating and getting all the clarifying information before creating the prompt. The output of this session should be a prompt that I can use for as many agents as I will be using to create this website. I was having a discussion based on this first prompt before my laptop lost power, now i can't see any of the conversation

---

## Assistant (Build · glm-4.7 · 21.1s)

_Thinking:_

The user wants me to act as a Business Analyst (BA) to gather requirements for creating a Ghost.js-based portfolio website. The website will have:
- 70% focus on blogs about health and technology for the over 40s
- User is a software developer, DevOps, and tech admin support personnel
- Currently freelancing
- Blog posts will come from social media → Gmail account → vetting/correction → publishing
- Will use a demo website first before moving to production
- Output should be an AI agent-agnostic prompt that can be used with different AI agents

I need to ask clarifying questions to understand all the requirements before creating the final prompt. Let me think about what information I need:

1. **Technical Setup**
   - Hosting environment? (Docker, direct hosting, Ghost Cloud?)
   - Domain names (demo vs production)
   - Theme preferences
   - Integrations needed (Gmail, social media, etc.)

2. **Content Strategy**
   - What social media platforms will posts come from?
   - How should the Gmail workflow be automated/integrated?
   - Content approval workflow details
   - Blog categories/topics
   - Frequency of posts

3. **Portfolio Elements**
   - What to showcase (projects, skills, services)?
   - Resume/CV section?
   - Testimonials?
   - Contact form?

4. **Design & UX**
   - Branding elements (colors, logo, style)
   - Target audience (over 40s - what does this mean for design?)
   - Mobile responsiveness requirements
   - Accessibility needs

5. **Monetization** (if any)
   - Ads?
   - Services offered?
   - Newsletter?

6. **Integration & Automation**
   - Gmail integration specifics
   - Social media integration
   - Analytics?
   - SEO requirements

7. **Demo to Production Strategy**
   - How will migration work?
   - Backup strategy
   - Testing requirements
   
I'll start gathering the initial requirements to build a comprehensive understanding of the project's scope and vision.

I'll help you create a comprehensive, agent-agnostic prompt for your Ghost.js portfolio website. Let me gather all the requirements first.

```
Tool: question

**Input:**
```json
{
  "questions": [
    {
      "question": "What hosting environment do you plan to use for Ghost?",
      "header": "Hosting",
      "options": [
        {
          "label": "Docker (self-hosted)",
          "description": "Run Ghost in Docker containers, full control over infrastructure"
        },
        {
          "label": "Ghost Cloud",
          "description": "Managed Ghost hosting, monthly fee"
        },
        {
          "label": "VPS/Direct hosting",
          "description": "Install Ghost directly on a virtual private server"
        },
        {
          "label": "Not decided yet",
          "description": "Open to recommendations based on requirements"
        }
      ]
    },
    {
      "question": "Which social media platforms will your blog posts be coming from?",
      "header": "Social Sources",
      "options": [
        {
          "label": "Twitter/X",
          "description": "Posts from Twitter/X will be imported"
        },
        {
          "label": "LinkedIn",
          "description": "LinkedIn articles/posts will be imported"
        },
        {
          "label": "Multiple platforms",
          "description": "Posts from various social media platforms"
        },
        {
          "label": "Not sure yet",
          "description": "Will determine based on ease of integration"
        }
      ]
    },
    {
      "question": "What should the Gmail integration workflow look like?",
      "header": "Gmail Workflow",
      "options": [
        {
          "label": "Manual extraction",
          "description": "Email arrives, you manually copy/paste content to Ghost"
        },
        {
          "label": "Semi-automated",
          "description": "Email parsing tool extracts content, you review and publish"
        },
        {
          "label": "Fully automated",
          "description": "Automatically creates draft posts from emails"
        },
        {
          "label": "Need guidance",
          "description": "Open to recommendations on best approach"
        }
      ]
    },
    {
      "question": "What portfolio elements do you want to showcase?",
      "header": "Portfolio",
      "multiple": true,
      "options": [
        {
          "label": "Projects/Gallery",
          "description": "Showcase completed projects with descriptions"
        },
        {
          "label": "Skills & Technologies",
          "description": "List of technical skills and tools you know"
        },
        {
          "label": "Services Offered",
          "description": "Freelance services you provide (DevOps, dev, support)"
        },
        {
          "label": "Resume/CV",
          "description": "Professional experience and background"
        },
        {
          "label": "Testimonials",
          "description": "Client feedback and reviews"
        },
        {
          "label": "Contact Form",
          "description": "Way for potential clients to reach you"
        }
      ]
    },
    {
      "question": "Do you have branding/design preferences?",
      "header": "Branding",
      "options": [
        {
          "label": "Modern minimalist",
          "description": "Clean, simple design with plenty of white space"
        },
        {
          "label": "Professional corporate",
          "description": "Traditional business-oriented design"
        },
        {
          "label": "Tech-focused dark theme",
          "description": "Dark mode aesthetic popular with developers"
        },
        {
          "label": "Accessible/readability focused",
          "description": "Optimized for over-40 audience with large fonts, high contrast"
        }
      ]
    },
    {
      "question": "What domain setup do you have in mind?",
      "header": "Domains",
      "options": [
        {
          "label": "Single domain (demo then prod)",
          "description": "Use one domain, switch content when ready"
        },
        {
          "label": "Separate domains",
          "description": "demo.yourdomain.com and www.yourdomain.com"
        },
        {
          "label": "Subdomains",
          "description": "blog.yourdomain.com for demo, yourdomain.com for production"
        },
        {
          "label": "Not decided yet",
          "description": "Open to suggestions on best approach"
        }
      ]
    },
    {
      "question": "What monetization strategy, if any, do you want to incorporate?",
      "header": "Monetization",
      "multiple": true,
      "options": [
        {
          "label": "Freelance services",
          "description": "Promote your consulting/freelance services"
        },
        {
          "label": "Newsletter signup",
          "description": "Build email list for future opportunities"
        },
        {
          "label": "Affiliate links",
          "description": "Recommend products/services with affiliate links"
        },
        {
          "label": "Sponsorships/ads",
          "description": "Display ads or sponsored content"
        },
        {
          "label": "None for now",
          "description": "Focus on building audience first"
        }
      ]
    },
    {
      "question": "What blog categories/topics do you want to cover beyond health & tech for over-40s?",
      "header": "Categories",
      "multiple": true,
      "options": [
        {
          "label": "DevOps tutorials",
          "description": "Technical guides and how-tos"
        },
        {
          "label": "Tech industry insights",
          "description": "Commentary on tech trends and developments"
        },
        {
          "label": "Health tips for developers",
          "description": "Ergonomics, wellness, work-life balance"
        },
        {
          "label": "Career advice for tech",
          "description": "Guidance for developers and tech professionals"
        },
        {
          "label": "Freelancing tips",
          "description": "Advice for freelance tech workers"
        }
      ]
    },
    {
      "question": "What automation/integration tools do you prefer?",
      "header": "Automation",
      "options": [
        {
          "label": "n8n",
          "description": "Open source automation platform (you have it in your stack)"
        },
        {
          "label": "Zapier/Make",
          "description": "Commercial automation platforms"
        },
        {
          "label": "Custom scripts",
          "description": "Write your own automation scripts"
        },
        {
          "label": "Need recommendations",
          "description": "Open to suggestions based on requirements"
        }
      ]
    },
    {
      "question": "What's your timeline for this project?",
      "header": "Timeline",
      "options": [
        {
          "label": "Quick prototype (1-2 weeks)",
          "description": "Get basic version up and running fast"
        },
        {
          "label": "Full production ready (1-2 months)",
          "description": "Comprehensive setup with all features"
        },
        {
          "label": "MVP first (demo), iterate later",
          "description": "Minimum viable product for demo, expand later"
        },
        {
          "label": "Flexible",
          "description": "No strict deadline, quality over speed"
        }
      ]
    }
  ]
}
```
**Error:**
```
Error: The question tool was called with invalid arguments: [
  {
    "origin": "string",
    "code": "too_big",
    "maximum": 12,
    "inclusive": true,
    "path": [
      "questions",
      1,
      "header"
    ],
    "message": "Too big: expected string to have <=12 characters"
  },
  {
    "origin": "string",
    "code": "too_big",
    "maximum": 12,
    "inclusive": true,
    "path": [
      "questions",
      2,
      "header"
    ],
    "message": "Too big: expected string to have <=12 characters"
  }
].
Please rewrite the input so it satisfies the expected schema.
```
```

---

## Assistant (Build · glm-4.7 · 267.9s)

_Thinking:_

I need to fix the headers - they must be <= 12 characters. Let me fix those:
- "Social Sources" -> "Social Srcs" (11 chars)
- "Gmail Workflow" -> "Gmail Flow" (10 chars)

Let me ask the questions again with corrected headers.

```
Tool: question

**Input:**
```json
{
  "questions": [
    {
      "header": "Hosting",
      "options": [
        {
          "description": "Run Ghost in Docker containers, full control over infrastructure",
          "label": "Docker (self-hosted)"
        },
        {
          "description": "Managed Ghost hosting, monthly fee",
          "label": "Ghost Cloud"
        },
        {
          "description": "Install Ghost directly on a virtual private server",
          "label": "VPS/Direct hosting"
        },
        {
          "description": "Open to recommendations based on requirements",
          "label": "Not decided yet"
        }
      ],
      "question": "What hosting environment do you plan to use for Ghost?"
    },
    {
      "header": "Social Srcs",
      "options": [
        {
          "description": "Posts from Twitter/X will be imported",
          "label": "Twitter/X"
        },
        {
          "description": "LinkedIn articles/posts will be imported",
          "label": "LinkedIn"
        },
        {
          "description": "Posts from various social media platforms",
          "label": "Multiple platforms"
        },
        {
          "description": "Will determine based on ease of integration",
          "label": "Not sure yet"
        }
      ],
      "question": "Which social media platforms will your blog posts be coming from?"
    },
    {
      "header": "Gmail Flow",
      "options": [
        {
          "description": "Email arrives, you manually copy/paste content to Ghost",
          "label": "Manual extraction"
        },
        {
          "description": "Email parsing tool extracts content, you review and publish",
          "label": "Semi-automated"
        },
        {
          "description": "Automatically creates draft posts from emails",
          "label": "Fully automated"
        },
        {
          "description": "Open to recommendations on best approach",
          "label": "Need guidance"
        }
      ],
      "question": "What should the Gmail integration workflow look like?"
    },
    {
      "header": "Portfolio",
      "multiple": true,
      "options": [
        {
          "description": "Showcase completed projects with descriptions",
          "label": "Projects/Gallery"
        },
        {
          "description": "List of technical skills and tools you know",
          "label": "Skills & Tech"
        },
        {
          "description": "Freelance services you provide (DevOps, dev, support)",
          "label": "Services"
        },
        {
          "description": "Professional experience and background",
          "label": "Resume/CV"
        },
        {
          "description": "Client feedback and reviews",
          "label": "Testimonials"
        },
        {
          "description": "Way for potential clients to reach you",
          "label": "Contact Form"
        }
      ],
      "question": "What portfolio elements do you want to showcase?"
    },
    {
      "header": "Branding",
      "options": [
        {
          "description": "Clean, simple design with plenty of white space",
          "label": "Modern minimal"
        },
        {
          "description": "Traditional business-oriented design",
          "label": "Professional"
        },
        {
          "description": "Dark mode aesthetic popular with developers",
          "label": "Tech dark theme"
        },
        {
          "description": "Optimized for over-40 audience with large fonts, high contrast",
          "label": "Accessible"
        }
      ],
      "question": "Do you have branding/design preferences?"
    },
    {
      "header": "Domains",
      "options": [
        {
          "description": "Use one domain, switch content when ready",
          "label": "Single domain"
        },
        {
          "description": "demo.yourdomain.com and www.yourdomain.com",
          "label": "Separate domains"
        },
        {
          "description": "blog.yourdomain.com for demo, yourdomain.com for production",
          "label": "Subdomains"
        },
        {
          "description": "Open to suggestions on best approach",
          "label": "Not decided yet"
        }
      ],
      "question": "What domain setup do you have in mind?"
    },
    {
      "header": "Monetization",
      "multiple": true,
      "options": [
        {
          "description": "Promote your consulting/freelance services",
          "label": "Freelance services"
        },
        {
          "description": "Build email list for future opportunities",
          "label": "Newsletter"
        },
        {
          "description": "Recommend products/services with affiliate links",
          "label": "Affiliate links"
        },
        {
          "description": "Display ads or sponsored content",
          "label": "Sponsorships"
        },
        {
          "description": "Focus on building audience first",
          "label": "None for now"
        }
      ],
      "question": "What monetization strategy, if any, do you want to incorporate?"
    },
    {
      "header": "Categories",
      "multiple": true,
      "options": [
        {
          "description": "Technical guides and how-tos",
          "label": "DevOps tutorials"
        },
        {
          "description": "Commentary on tech trends and developments",
          "label": "Tech insights"
        },
        {
          "description": "Ergonomics, wellness, work-life balance",
          "label": "Health tips"
        },
        {
          "description": "Guidance for developers and tech professionals",
          "label": "Career advice"
        },
        {
          "description": "Advice for freelance tech workers",
          "label": "Freelancing tips"
        }
      ],
      "question": "What blog categories/topics do you want to cover beyond health & tech for over-40s?"
    },
    {
      "header": "Automation",
      "options": [
        {
          "description": "Open source automation platform (you have it in your stack)",
          "label": "n8n"
        },
        {
          "description": "Commercial automation platforms",
          "label": "Zapier/Make"
        },
        {
          "description": "Write your own automation scripts",
          "label": "Custom scripts"
        },
        {
          "description": "Open to suggestions based on requirements",
          "label": "Need recommendations"
        }
      ],
      "question": "What automation/integration tools do you prefer?"
    },
    {
      "header": "Timeline",
      "options": [
        {
          "description": "Get basic version up and running fast",
          "label": "Quick prototype"
        },
        {
          "description": "Comprehensive setup with all features",
          "label": "Full production"
        },
        {
          "description": "Minimum viable product for demo, expand later",
          "label": "MVP then iterate"
        },
        {
          "description": "No strict deadline, quality over speed",
          "label": "Flexible"
        }
      ],
      "question": "What's your timeline for this project?"
    }
  ]
}
```
**Output:**
```
User has answered your questions: "What hosting environment do you plan to use for Ghost?"="Docker (self-hosted)", "Which social media platforms will your blog posts be coming from?"="Multiple platforms", "What should the Gmail integration workflow look like?"="Semi-automated", "What portfolio elements do you want to showcase?"="Projects/Gallery, Skills & Tech, Services, Testimonials, Contact Form", "Do you have branding/design preferences?"="Modern minimal", "What domain setup do you have in mind?"="Separate domains", "What monetization strategy, if any, do you want to incorporate?"="Freelance services, Newsletter, Affiliate links", "What blog categories/topics do you want to cover beyond health & tech for over-40s?"="DevOps tutorials, Tech insights, Health tips, Freelancing tips", "What automation/integration tools do you prefer?"="Custom scripts", "What's your timeline for this project?"="MVP then iterate". You can now continue with the user's answers in mind.
```
```

---

## Assistant (Build · glm-4.7 · 53.2s)

_Thinking:_

Great! I have the initial answers. Now I need to ask some follow-up questions to get more specific details before creating the comprehensive prompt. Let me think about what else I need to know:

1. More details on the Gmail workflow - how do they want to receive emails from social media?
2. What specific custom scripts are they thinking about?
3. Any existing domains or tools in their current stack?
4. Content publishing frequency
5. SEO requirements
6. Analytics needs
7. Backup strategy
8. Demo to production migration plan

Let me ask another batch of questions.

```
Tool: question

**Input:**
```json
{
  "questions": [
    {
      "header": "Gmail Details",
      "multiple": true,
      "options": [
        {
          "description": "Set up email forwarding from social platforms",
          "label": "Email forwarding"
        },
        {
          "description": "Social platforms send emails with post content",
          "label": "Digest emails"
        },
        {
          "description": "Use RSS feeds converted to emails",
          "label": "RSS to email"
        },
        {
          "description": "Custom API integration to send to Gmail",
          "label": "API integration"
        }
      ],
      "question": "How will social media posts get to your Gmail?"
    },
    {
      "header": "Scripting",
      "options": [
        {
          "description": "Node.js for automation",
          "label": "Node.js"
        },
        {
          "description": "Python for automation",
          "label": "Python"
        },
        {
          "description": "Bash scripts for automation",
          "label": "Bash scripts"
        },
        {
          "description": "Open to agent recommendations",
          "label": "Agent decides"
        }
      ],
      "question": "What scripting languages/tools for your custom automation?"
    },
    {
      "header": "Domains Owned",
      "options": [
        {
          "description": "I have demo and production domains ready",
          "label": "Yes, both"
        },
        {
          "description": "I have one domain, will register another",
          "label": "One domain"
        },
        {
          "description": "Need to register both domains",
          "label": "None yet"
        },
        {
          "description": "Will use local demo only for now",
          "label": "Local only"
        }
      ],
      "question": "Do you already have demo and production domains registered?"
    },
    {
      "header": "Publish Freq",
      "options": [
        {
          "description": "1-2 posts per week",
          "label": "Weekly"
        },
        {
          "description": "3-5 posts per week",
          "label": "Multiple/week"
        },
        {
          "description": "Depends on social media volume",
          "label": "Variable"
        },
        {
          "description": "Whatever works best for MVP",
          "label": "Flexible"
        }
      ],
      "question": "How frequently do you plan to publish blog posts?"
    },
    {
      "header": "Ghost Theme",
      "options": [
        {
          "description": "Use an existing Ghost theme as starting point",
          "label": "Existing theme"
        },
        {
          "description": "Custom-built theme from scratch",
          "label": "Custom theme"
        },
        {
          "description": "Existing theme with modifications",
          "label": "Theme + mods"
        },
        {
          "description": "Open to agent recommendations",
          "label": "Agent decides"
        }
      ],
      "question": "Do you want to use an existing Ghost theme or create a custom one?"
    },
    {
      "header": "Analytics",
      "options": [
        {
          "description": "Google Analytics integration",
          "label": "Google Analytics"
        },
        {
          "description": "Plausible or privacy-focused analytics",
          "label": "Privacy-focused"
        },
        {
          "description": "Ghost built-in analytics only",
          "label": "Ghost native"
        },
        {
          "description": "None for MVP initially",
          "label": "None yet"
        }
      ],
      "question": "What analytics do you want to integrate?"
    },
    {
      "header": "SEO Goals",
      "multiple": true,
      "options": [
        {
          "description": "Rank for tech/health keywords",
          "label": "Keyword ranking"
        },
        {
          "description": "Local SEO for freelance clients",
          "label": "Local presence"
        },
        {
          "description": "Build domain authority",
          "label": "Authority building"
        },
        {
          "description": "Basic SEO configuration for MVP",
          "label": "Basic setup"
        }
      ],
      "question": "What are your SEO priorities?"
    },
    {
      "header": "Backup",
      "options": [
        {
          "description": "Automated daily backups to cloud storage",
          "label": "Auto daily"
        },
        {
          "description": "Weekly backups, manual when needed",
          "label": "Weekly"
        },
        {
          "description": "Backup before major changes only",
          "label": "On-demand"
        },
        {
          "description": "Will determine after MVP",
          "label": "Later phase"
        }
      ],
      "question": "What backup strategy do you want for Ghost data?"
    },
    {
      "header": "Migration",
      "options": [
        {
          "description": "Export/import Ghost data between instances",
          "label": "Ghost export"
        },
        {
          "description": "Database migration between containers",
          "label": "DB migration"
        },
        {
          "description": "Fresh install and content migration",
          "label": "Fresh install"
        },
        {
          "description": "Need guidance on best approach",
          "label": "Agent advises"
        }
      ],
      "question": "How do you plan to migrate from demo to production?"
    }
  ]
}
```
**Error:**
```
Error: The question tool was called with invalid arguments: [
  {
    "origin": "string",
    "code": "too_big",
    "maximum": 12,
    "inclusive": true,
    "path": [
      "questions",
      0,
      "header"
    ],
    "message": "Too big: expected string to have <=12 characters"
  },
  {
    "origin": "string",
    "code": "too_big",
    "maximum": 12,
    "inclusive": true,
    "path": [
      "questions",
      2,
      "header"
    ],
    "message": "Too big: expected string to have <=12 characters"
  }
].
Please rewrite the input so it satisfies the expected schema.
```
```

---

## Assistant (Build · glm-4.7 · 401.0s)

_Thinking:_

Need to fix the headers again:
- "Gmail Details" -> "Gmail Det" (9 chars)
- "Domains Owned" -> "Domains" (7 chars)

```
Tool: question

**Input:**
```json
{
  "questions": [
    {
      "header": "Gmail Det",
      "multiple": true,
      "options": [
        {
          "description": "Set up email forwarding from social platforms",
          "label": "Email forwarding"
        },
        {
          "description": "Social platforms send emails with post content",
          "label": "Digest emails"
        },
        {
          "description": "Use RSS feeds converted to emails",
          "label": "RSS to email"
        },
        {
          "description": "Custom API integration to send to Gmail",
          "label": "API integration"
        }
      ],
      "question": "How will social media posts get to your Gmail?"
    },
    {
      "header": "Scripting",
      "options": [
        {
          "description": "Node.js for automation",
          "label": "Node.js"
        },
        {
          "description": "Python for automation",
          "label": "Python"
        },
        {
          "description": "Bash scripts for automation",
          "label": "Bash scripts"
        },
        {
          "description": "Open to agent recommendations",
          "label": "Agent decides"
        }
      ],
      "question": "What scripting languages/tools for your custom automation?"
    },
    {
      "header": "Domains",
      "options": [
        {
          "description": "I have demo and production domains ready",
          "label": "Yes, both"
        },
        {
          "description": "I have one domain, will register another",
          "label": "One domain"
        },
        {
          "description": "Need to register both domains",
          "label": "None yet"
        },
        {
          "description": "Will use local demo only for now",
          "label": "Local only"
        }
      ],
      "question": "Do you already have demo and production domains registered?"
    },
    {
      "header": "Publish Freq",
      "options": [
        {
          "description": "1-2 posts per week",
          "label": "Weekly"
        },
        {
          "description": "3-5 posts per week",
          "label": "Multiple/week"
        },
        {
          "description": "Depends on social media volume",
          "label": "Variable"
        },
        {
          "description": "Whatever works best for MVP",
          "label": "Flexible"
        }
      ],
      "question": "How frequently do you plan to publish blog posts?"
    },
    {
      "header": "Ghost Theme",
      "options": [
        {
          "description": "Use an existing Ghost theme as starting point",
          "label": "Existing theme"
        },
        {
          "description": "Custom-built theme from scratch",
          "label": "Custom theme"
        },
        {
          "description": "Existing theme with modifications",
          "label": "Theme + mods"
        },
        {
          "description": "Open to agent recommendations",
          "label": "Agent decides"
        }
      ],
      "question": "Do you want to use an existing Ghost theme or create a custom one?"
    },
    {
      "header": "Analytics",
      "options": [
        {
          "description": "Google Analytics integration",
          "label": "Google Analytics"
        },
        {
          "description": "Plausible or privacy-focused analytics",
          "label": "Privacy-focused"
        },
        {
          "description": "Ghost built-in analytics only",
          "label": "Ghost native"
        },
        {
          "description": "None for MVP initially",
          "label": "None yet"
        }
      ],
      "question": "What analytics do you want to integrate?"
    },
    {
      "header": "SEO Goals",
      "multiple": true,
      "options": [
        {
          "description": "Rank for tech/health keywords",
          "label": "Keyword ranking"
        },
        {
          "description": "Local SEO for freelance clients",
          "label": "Local presence"
        },
        {
          "description": "Build domain authority",
          "label": "Authority building"
        },
        {
          "description": "Basic SEO configuration for MVP",
          "label": "Basic setup"
        }
      ],
      "question": "What are your SEO priorities?"
    },
    {
      "header": "Backup",
      "options": [
        {
          "description": "Automated daily backups to cloud storage",
          "label": "Auto daily"
        },
        {
          "description": "Weekly backups, manual when needed",
          "label": "Weekly"
        },
        {
          "description": "Backup before major changes only",
          "label": "On-demand"
        },
        {
          "description": "Will determine after MVP",
          "label": "Later phase"
        }
      ],
      "question": "What backup strategy do you want for Ghost data?"
    },
    {
      "header": "Migration",
      "options": [
        {
          "description": "Export/import Ghost data between instances",
          "label": "Ghost export"
        },
        {
          "description": "Database migration between containers",
          "label": "DB migration"
        },
        {
          "description": "Fresh install and content migration",
          "label": "Fresh install"
        },
        {
          "description": "Need guidance on best approach",
          "label": "Agent advises"
        }
      ],
      "question": "How do you plan to migrate from demo to production?"
    }
  ]
}
```
**Output:**
```
User has answered your questions: "How will social media posts get to your Gmail?"="API integration, RSS to email, Digest emails", "What scripting languages/tools for your custom automation?"="Python", "Do you already have demo and production domains registered?"="One domain", "How frequently do you plan to publish blog posts?"="Multiple/week", "Do you want to use an existing Ghost theme or create a custom one?"="Custom theme", "What analytics do you want to integrate?"="Google Analytics", "What are your SEO priorities?"="Basic setup, Local presence, Keyword ranking", "What backup strategy do you want for Ghost data?"="Later phase", "How do you plan to migrate from demo to production?"="Agent advises". You can now continue with the user's answers in mind.
```
```

---

## Assistant (Build · glm-4.7 · 55.0s)

_Thinking:_

Good, now I have more details. Let me ask a few more questions about technical specifics and additional features:

1. Ghost version preferences
2. Database preferences (SQLite for demo vs MySQL/PostgreSQL for prod)
3. Content approval workflow specifics
4. Contact form integration
5. Newsletter service integration
6. Any specific social platforms they want to integrate
7. Portfolio display preferences (images, links, etc.)
8. Testimonials display
9. Services pricing/display

Let me ask one more batch of questions.

```
Tool: question

**Input:**
```json
{
  "questions": [
    {
      "header": "Ghost Ver",
      "options": [
        {
          "description": "Use latest stable Ghost release",
          "label": "Latest stable"
        },
        {
          "description": "Specific Ghost version in mind",
          "label": "Specific version"
        },
        {
          "description": "Let agent decide based on features",
          "label": "Agent decides"
        }
      ],
      "question": "Which Ghost version should be used?"
    },
    {
      "header": "Database",
      "options": [
        {
          "description": "Use existing PostgreSQL from your Docker stack",
          "label": "PostgreSQL"
        },
        {
          "description": "Use existing MySQL/MariaDB if available",
          "label": "MySQL"
        },
        {
          "description": "Use SQLite for demo, switch to MySQL/PostgreSQL for production",
          "label": "SQLite then prod DB"
        },
        {
          "description": "Let agent decide based on setup",
          "label": "Agent decides"
        }
      ],
      "question": "What database should Ghost use?"
    },
    {
      "header": "Approval Flow",
      "options": [
        {
          "description": "Review email content, create Ghost draft, preview, then publish",
          "label": "Email→Draft→Preview→Pub"
        },
        {
          "description": "Email parsing creates draft, edit in Ghost, preview, then publish",
          "label": "Auto draft→Edit→Pub"
        },
        {
          "description": "Review in email, approve via reply, auto-publish to Ghost",
          "label": "Email reply approve"
        },
        {
          "description": "Let agent suggest best workflow",
          "label": "Agent advises"
        }
      ],
      "question": "What is your content approval workflow?"
    },
    {
      "header": "Contact Form",
      "options": [
        {
          "description": "Use Ghost built-in forms feature",
          "label": "Ghost native"
        },
        {
          "description": "Custom form with email notifications",
          "label": "Custom form"
        },
        {
          "description": "Third-party form service (Formspree, etc.)",
          "label": "3rd party"
        },
        {
          "description": "Let agent decide based on needs",
          "label": "Agent decides"
        }
      ],
      "question": "How should the contact form be implemented?"
    },
    {
      "header": "Newsletter",
      "options": [
        {
          "description": "Use Ghost built-in newsletter functionality",
          "label": "Ghost native"
        },
        {
          "description": "Integrate with external email service",
          "label": "External service"
        },
        {
          "description": "Gmail for newsletter sending",
          "label": "Gmail"
        },
        {
          "description": "Let agent decide",
          "label": "Agent decides"
        }
      ],
      "question": "How should newsletter signup/management work?"
    },
    {
      "header": "Social Platforms",
      "multiple": true,
      "options": [
        {
          "description": "Twitter/X integration",
          "label": "Twitter/X"
        },
        {
          "description": "LinkedIn integration",
          "label": "LinkedIn"
        },
        {
          "description": "Facebook integration",
          "label": "Facebook"
        },
        {
          "description": "Instagram integration",
          "label": "Instagram"
        },
        {
          "description": "Will determine based on API access",
          "label": "Not sure yet"
        }
      ],
      "question": "Which specific social platforms do you want to integrate?"
    },
    {
      "header": "Portfolio",
      "multiple": true,
      "options": [
        {
          "description": "Project images/screenshots",
          "label": "Images"
        },
        {
          "description": "Live demo links",
          "label": "Live demos"
        },
        {
          "description": "GitHub repository links",
          "label": "GitHub links"
        },
        {
          "description": "Case study descriptions",
          "label": "Case studies"
        },
        {
          "description": "Tech stack details",
          "label": "Tech stacks"
        }
      ],
      "question": "What should be displayed for each portfolio project?"
    },
    {
      "header": "Testimonials",
      "options": [
        {
          "description": "Client name, company, quote, photo if available",
          "label": "Full details"
        },
        {
          "description": "Anonymous testimonials with company names",
          "label": "Anonymous"
        },
        {
          "description": "Text quotes only, no images",
          "label": "Text only"
        },
        {
          "description": "Let agent decide design",
          "label": "Agent decides"
        }
      ],
      "question": "How should testimonials be displayed?"
    },
    {
      "header": "Services",
      "options": [
        {
          "description": "Service description, pricing tiers, contact CTA",
          "label": "Packages"
        },
        {
          "description": "Service descriptions only, pricing by request",
          "label": "No pricing"
        },
        {
          "description": "Hourly rates and service offerings",
          "label": "Hourly rates"
        },
        {
          "description": "Let agent design layout",
          "label": "Agent decides"
        }
      ],
      "question": "How should freelance services be presented?"
    },
    {
      "header": "Affiliate Links",
      "options": [
        {
          "description": "Text links within relevant blog posts",
          "label": "In-content links"
        },
        {
          "description": "Sidebar or footer banner links",
          "label": "Banner ads"
        },
        {
          "description": "Dedicated resources/recommendations page",
          "label": "Resources page"
        },
        {
          "description": "Let agent decide placement",
          "label": "Agent decides"
        }
      ],
      "question": "How should affiliate links be integrated?"
    }
  ]
}
```
**Error:**
```
Error: The question tool was called with invalid arguments: [
  {
    "origin": "string",
    "code": "too_big",
    "maximum": 12,
    "inclusive": true,
    "path": [
      "questions",
      2,
      "header"
    ],
    "message": "Too big: expected string to have <=12 characters"
  },
  {
    "origin": "string",
    "code": "too_big",
    "maximum": 12,
    "inclusive": true,
    "path": [
      "questions",
      5,
      "header"
    ],
    "message": "Too big: expected string to have <=12 characters"
  },
  {
    "origin": "string",
    "code": "too_big",
    "maximum": 12,
    "inclusive": true,
    "path": [
      "questions",
      9,
      "header"
    ],
    "message": "Too big: expected string to have <=12 characters"
  }
].
Please rewrite the input so it satisfies the expected schema.
```
```

---

## Assistant (Build · glm-4.7 · 234.9s)

_Thinking:_

Need to fix these headers:- "Approval Flow" -> "Approval" (8 chars)
- "Social Platforms" -> "Social P" (8 chars)
- "Affiliate Links" -> "Affiliate" (8 chars)

```
Tool: question

**Input:**
```json
{
  "questions": [
    {
      "header": "Ghost Ver",
      "options": [
        {
          "description": "Use latest stable Ghost release",
          "label": "Latest stable"
        },
        {
          "description": "Specific Ghost version in mind",
          "label": "Specific version"
        },
        {
          "description": "Let agent decide based on features",
          "label": "Agent decides"
        }
      ],
      "question": "Which Ghost version should be used?"
    },
    {
      "header": "Database",
      "options": [
        {
          "description": "Use existing PostgreSQL from your Docker stack",
          "label": "PostgreSQL"
        },
        {
          "description": "Use existing MySQL/MariaDB if available",
          "label": "MySQL"
        },
        {
          "description": "Use SQLite for demo, switch to MySQL/PostgreSQL for production",
          "label": "SQLite then prod DB"
        },
        {
          "description": "Let agent decide based on setup",
          "label": "Agent decides"
        }
      ],
      "question": "What database should Ghost use?"
    },
    {
      "header": "Approval",
      "options": [
        {
          "description": "Review email content, create Ghost draft, preview, then publish",
          "label": "Email→Draft→Preview→Pub"
        },
        {
          "description": "Email parsing creates draft, edit in Ghost, preview, then publish",
          "label": "Auto draft→Edit→Pub"
        },
        {
          "description": "Review in email, approve via reply, auto-publish to Ghost",
          "label": "Email reply approve"
        },
        {
          "description": "Let agent suggest best workflow",
          "label": "Agent advises"
        }
      ],
      "question": "What is your content approval workflow?"
    },
    {
      "header": "Contact Form",
      "options": [
        {
          "description": "Use Ghost built-in forms feature",
          "label": "Ghost native"
        },
        {
          "description": "Custom form with email notifications",
          "label": "Custom form"
        },
        {
          "description": "Third-party form service (Formspree, etc.)",
          "label": "3rd party"
        },
        {
          "description": "Let agent decide based on needs",
          "label": "Agent decides"
        }
      ],
      "question": "How should the contact form be implemented?"
    },
    {
      "header": "Newsletter",
      "options": [
        {
          "description": "Use Ghost built-in newsletter functionality",
          "label": "Ghost native"
        },
        {
          "description": "Integrate with external email service",
          "label": "External service"
        },
        {
          "description": "Gmail for newsletter sending",
          "label": "Gmail"
        },
        {
          "description": "Let agent decide",
          "label": "Agent decides"
        }
      ],
      "question": "How should newsletter signup/management work?"
    },
    {
      "header": "Social P",
      "multiple": true,
      "options": [
        {
          "description": "Twitter/X integration",
          "label": "Twitter/X"
        },
        {
          "description": "LinkedIn integration",
          "label": "LinkedIn"
        },
        {
          "description": "Facebook integration",
          "label": "Facebook"
        },
        {
          "description": "Instagram integration",
          "label": "Instagram"
        },
        {
          "description": "Will determine based on API access",
          "label": "Not sure yet"
        }
      ],
      "question": "Which specific social platforms do you want to integrate?"
    },
    {
      "header": "Portfolio",
      "multiple": true,
      "options": [
        {
          "description": "Project images/screenshots",
          "label": "Images"
        },
        {
          "description": "Live demo links",
          "label": "Live demos"
        },
        {
          "description": "GitHub repository links",
          "label": "GitHub links"
        },
        {
          "description": "Case study descriptions",
          "label": "Case studies"
        },
        {
          "description": "Tech stack details",
          "label": "Tech stacks"
        }
      ],
      "question": "What should be displayed for each portfolio project?"
    },
    {
      "header": "Testimonials",
      "options": [
        {
          "description": "Client name, company, quote, photo if available",
          "label": "Full details"
        },
        {
          "description": "Anonymous testimonials with company names",
          "label": "Anonymous"
        },
        {
          "description": "Text quotes only, no images",
          "label": "Text only"
        },
        {
          "description": "Let agent decide design",
          "label": "Agent decides"
        }
      ],
      "question": "How should testimonials be displayed?"
    },
    {
      "header": "Services",
      "options": [
        {
          "description": "Service description, pricing tiers, contact CTA",
          "label": "Packages"
        },
        {
          "description": "Service descriptions only, pricing by request",
          "label": "No pricing"
        },
        {
          "description": "Hourly rates and service offerings",
          "label": "Hourly rates"
        },
        {
          "description": "Let agent design layout",
          "label": "Agent decides"
        }
      ],
      "question": "How should freelance services be presented?"
    },
    {
      "header": "Affiliate",
      "options": [
        {
          "description": "Text links within relevant blog posts",
          "label": "In-content links"
        },
        {
          "description": "Sidebar or footer banner links",
          "label": "Banner ads"
        },
        {
          "description": "Dedicated resources/recommendations page",
          "label": "Resources page"
        },
        {
          "description": "Let agent decide placement",
          "label": "Agent decides"
        }
      ],
      "question": "How should affiliate links be integrated?"
    }
  ]
}
```
**Output:**
```
User has answered your questions: "Which Ghost version should be used?"="Agent decides", "What database should Ghost use?"="PostgreSQL", "What is your content approval workflow?"="Agent advises", "How should the contact form be implemented?"="3rd party", "How should newsletter signup/management work?"="Agent decides", "Which specific social platforms do you want to integrate?"="Twitter/X, Instagram, LinkedIn, instagram, reddit", "What should be displayed for each portfolio project?"="Images, Case studies, Tech stacks", "How should testimonials be displayed?"="Full details", "How should freelance services be presented?"="Packages", "How should affiliate links be integrated?"="Agent decides". You can now continue with the user's answers in mind.
```
```

---

## Assistant (Build · glm-4.7 · 69.8s)

_Thinking:_

Great! Now I have all the information I need. Let me create a comprehensive, agent-agnostic prompt that the user can use with any AI agent to create their Ghost.js portfolio website.

Let me compile all the requirements:

**Core Requirements:**
- Ghost.js-based portfolio website
- 70% focus on blogs about health and technology for the over 40s
- User is a software developer, DevOps, and tech admin support personnel
- Currently freelancing
- Blog posts coming from social media → Gmail → vetting/correction → Ghost publishing
- Demo website first, then production

**Technical Requirements:**
- Hosting: Docker (self-hosted)
- Database: PostgreSQL (use existing from Docker stack)
- Ghost Version: Agent decides (latest stable recommended)
- Theme: Custom theme
- Design: Modern minimalist
- Scripting: Python for custom automation
- Automation tools: Custom scripts (Python)
- Analytics: Google Analytics
- Contact Form: Third-party service
- Newsletter: Agent decides
- Monetization: Freelance services, Newsletter, Affiliate links

**Content Requirements:**
- Social Platforms: Twitter/X, Instagram, LinkedIn, Reddit
- Gmail workflow: Semi-automated (API integration, RSS to email, Digest emails)
- Content approval workflow: Agent advises
- Blog categories:
  - Health and technology for the over 40s (70% focus)
  - DevOps tutorials
  - Tech insights
  - Health tips
  - Freelancing tips
- Publishing frequency: Multiple posts per week (variable based on volume)

**Portfolio Elements:**
- Projects/Gallery (Images, Case studies, Tech stacks)
- Skills & Technologies
- Services (Packages with pricing tiers)
- Testimonials (Full details: client name, company, quote, photo)
- Contact Form (Third-party service)

**Domains:**


I'll leverage my existing domain strategy for seamless development and production deployment. With one domain already secured, I'll set up distinct demo and production environments to ensure a smooth transition from testing to live site.

**SEO Strategy:**
I'll implement a targeted SEO approach focusing on basic setup, local presence optimization, and strategic keyword ranking to improve visibility and reach for the target audience.

**Project Phases:**
Starting with a Minimum Viable Product (MVP) approach, I'll prioritize a quick prototype. This allows for iterative development, ensuring continuous improvement and adaptation based on initial performance and feedback.

**Migration Plan:**
The demo-to-production migration will follow an agent-recommended strategy, with backup considerations to be addressed in later project phases for robust data protection and site reliability.

**Additional Considerations:**
The integration will leverage my existing Docker infrastructure stack, utilizing n8n for potential workflow automation and ensuring comprehensive API integration across platforms.

Now I'll create a comprehensive, agent-agnostic prompt based on all the requirements gathered.

```
Tool: write

**Input:**
```json
{
  "content": "# Ghost.js Portfolio Website Development Prompt\n\n## Project Overview\n\nCreate a Ghost.js-based portfolio website for a freelance software developer, DevOps engineer, and tech admin support personnel. The site has a 70% focus on blogs about health and technology for the over-40s demographic, with the remaining content covering professional portfolio elements.\n\n### Core Objectives\n1. **Portfolio Site**: Showcase professional services, projects, skills, and testimonials\n2. **Health & Tech Blog (70%)**: Content focused on health and technology insights for professionals over 40\n3. **Content Pipeline**: Automated content ingestion from social media platforms → Gmail → vetting/correction → Ghost publication\n4. **Development Approach**: MVP first on demo environment, then migrate to production\n\n---\n\n## Technical Requirements\n\n### Hosting & Infrastructure\n- **Platform**: Docker (self-hosted)\n- **Database**: PostgreSQL (integrate with existing Docker stack PostgreSQL)\n- **Ghost Version**: Use latest stable release (at the time of implementation)\n- **Deployment Environment**: Two separate instances\n  - Demo environment (for testing and initial development)\n  - Production environment (final live site)\n- **Domains**: Separate domains for demo and production\n  - You have one domain registered; recommend approach for acquiring/setting up second domain\n\n### Theme & Design\n- **Theme Type**: Custom Ghost theme (built from scratch)\n- **Design Style**: Modern minimalist\n  - Clean, simple design with ample white space\n  - High readability optimized for over-40 audience\n  - Responsive across all devices\n  - Accessible (WCAG AA compliance recommended)\n- **Key Design Considerations**:\n  - Clear typography hierarchy\n  - Large, readable fonts for the target demographic\n  - High contrast for readability\n  - Intuitive navigation\n\n### Technology Stack\n- **Ghost.js**: Content management system\n- **Docker**: Containerization\n- **Python**: Custom automation scripts\n- **PostgreSQL**: Database (existing in Docker stack)\n- **Google Analytics**: Analytics integration\n- **Third-party form service**: Contact form implementation (recommend service)\n- **Existing Infrastructure**: You have Traefik, n8n, PostgreSQL, Gitea in your Docker stack (can leverage as needed)\n\n---\n\n## Content Requirements\n\n### Blog Categories & Focus\n\n**Primary Focus (70%)**\n- Health and Technology for the Over-40s\n  - Topics may include: maintaining health in tech careers, technology for healthy aging, ergonomics, wellness for developers, work-life balance, technology solutions for health challenges common in the 40+ demographic\n\n**Secondary Categories (30%)**\n- DevOps Tutorials: Technical guides, how-tos, best practices\n- Tech Insights: Commentary on tech trends, industry developments, analysis\n- Health Tips: Ergonomics, wellness, work-life balance for tech professionals\n- Freelancing Tips: Advice for freelance tech workers, client management, pricing\n\n### Content Publishing Workflow\n\n**Social Media Integration**\n- Platforms to integrate:\n  - Twitter/X\n  - Instagram\n  - LinkedIn\n  - Reddit\n\n**Gmail Workflow (Semi-Automated)**\nContent flows from social media platforms to Gmail inbox via:\n1. API integration (preferred)\n2. RSS to email conversion\n3. Digest emails from platforms\n\n**Content Approval Pipeline**\n- Agent should recommend best practice workflow (examples to consider):\n  - Email parsing creates Ghost draft → User reviews in Ghost admin → Preview → Publish\n  - User reviews email content → Create Ghost draft → Preview → Publish\n  - Email parsing creates draft → User edits → Preview → Publish\n- All content requires vetting, correction, and approval before publishing\n- User must review and approve every post before it goes live\n\n**Publishing Frequency**\n- Multiple posts per week (variable based on social media content volume)\n- No strict schedule initially\n\n---\n\n## Portfolio Elements\n\n### Pages & Sections Required\n\n**1. Home Page**\n- Introduction/hero section\n- Featured blog posts (prioritize health & tech over-40s content)\n- Brief overview of services\n- Call-to-action for newsletter signup\n\n**2. Projects/Gallery Page**\n- Display completed projects with:\n  - Project images/screenshots\n  - Case study descriptions\n  - Technology stack used for each project\n  - Links to live demos (if available)\n\n**3. Skills & Technologies Page**\n- List and categorize technical skills\n- Highlight expertise in:\n  - Software Development\n  - DevOps\n  - Tech Administration/Support\n  - Relevant tools and platforms\n\n**4. Services Page**\n- Present freelance services as packages:\n  - Service descriptions\n  - Pricing tiers/packages\n  - Clear call-to-action (contact for booking/inquiries)\n  - Service deliverables outlined\n\n**5. Testimonials Page**\n- Display client testimonials with:\n  - Client name\n  - Company name\n  - Quote/testimonial text\n  - Client photo (if available)\n  - Optional: project or service worked on together\n\n**6. About Page**\n- Professional background\n- Expertise areas\n- Why health & tech for over-40s focus\n- Personal approach to freelancing\n\n**7. Contact Page**\n- Contact form (third-party service integration)\n- Social media links\n- Email contact option\n- Response time expectations\n\n---\n\n## Integration Requirements\n\n### Social Media → Gmail → Ghost Pipeline\n**Phase 1: MVP (Demo Environment)**\nImplement a basic content ingestion workflow using Python scripts:\n- Fetch content from social platforms (via APIs where possible, or RSS feeds)\n- Convert to email format and send to Gmail\n- Manual extraction/copy-paste for initial testing\n\n**Phase 2: Enhanced (Post-MVP)**\nDevelop more sophisticated Python automation:\n- Parse emails automatically\n- Create Ghost draft posts programmatically\n- Extract metadata (images, tags, categories)\n- Assign appropriate tags/categories automatically\n- Notify user of new drafts requiring review\n\n### Third-Party Integrations\n- **Contact Form**: Recommend and integrate reliable third-party form service (e.g., Formspree, Typeform, Netlify Forms)\n- **Newsletter**: Agent should recommend best approach (Ghost native vs external service)\n- **Google Analytics**: Full GA4 integration\n- **Affiliate Links**: Agent should determine best placement strategy (in-content, sidebar, resources page)\n\n### APIs & Webhooks (Where Applicable)\n- Social media platform APIs (Twitter/X, Instagram, LinkedIn, Reddit)\n- Ghost API for content management\n- Gmail API for email parsing\n- Third-party form service webhook\n\n---\n\n## SEO & Analytics\n\n### SEO Requirements\n- **Basic Setup** (Priority for MVP):\n  - Meta titles and descriptions for all pages\n  - XML sitemap\n  - Robots.txt configuration\n  - Structured data markup (schema.org)\n  - Canonical URLs\n\n- **Local Presence** (Priority for MVP):\n  - Local SEO optimization for freelance services\n  - Geographic targeting configuration\n\n- **Keyword Ranking** (Priority for MVP):\n  - Target keywords related to:\n    - Health and technology for over-40s\n    - DevOps services\n    - Freelance software development\n    - Tech administration/support\n  - SEO-friendly URL structure\n  - Image alt text optimization\n\n### Analytics\n- **Google Analytics (GA4)**: Full implementation with:\n  - Page view tracking\n  - Event tracking (form submissions, affiliate link clicks)\n  - Custom dimensions for blog categories\n  - Conversion tracking (newsletter signups, contact form submissions)\n\n---\n\n## Monetization Strategy\n\n### 1. Freelance Services Promotion\n- Promote services across site\n- Clear pricing/packages on Services page\n- Calls-to-action in blog posts when relevant\n\n### 2. Newsletter\n- Email list building for future opportunities\n- Newsletter signup form on homepage and throughout site\n- Regular newsletter with curated content\n\n### 3. Affiliate Links\n- Agent should determine optimal placement strategy\n- Recommend products/services relevant to target audience\n- Ensure compliance with disclosure requirements\n\n---\n\n## Development Phases\n\n### Phase 1: MVP - Demo Environment\n**Goal**: Basic functional site for testing\n\n**Deliverables**:\n1. Ghost instance running in Docker with PostgreSQL\n2. Custom theme (basic modern minimalist design)\n3. Essential pages created (Home, About, Contact, Services, Blog)\n4. Basic social media → Gmail manual workflow\n5. Third-party contact form integrated\n6. Google Analytics basic setup\n7. Basic SEO configuration\n8. Portfolio pages with placeholder content\n9. Newsletter signup functionality\n10. Testing environment on demo domain\n\n**Timeline**: 1-2 weeks (adjust based on complexity)\n\n### Phase 2: Enhanced Features (Post-MVP)\n**Goal**: Advanced features and automation\n\n**Deliverables**:\n1. Automated Python scripts for content pipeline:\n   - Social media content fetching\n   - Email parsing and Ghost draft creation\n   - Metadata extraction and tagging\n2. Enhanced portfolio pages with real content\n3. Advanced SEO optimization\n4. Additional integrations as needed\n5. Performance optimization\n6. Mobile responsiveness refinement\n\n**Timeline**: Determine after MVP review\n\n### Phase 3: Production Migration\n**Goal**: Deploy to production environment\n\n**Deliverables**:\n1. Agent should recommend best migration approach:\n   - Ghost export/import between instances\n   - Database migration between containers\n   - Fresh install with content migration\n2. Content migration from demo to production\n3. Domain configuration for production\n4. SSL/TLS configuration\n5. Final testing and verification\n\n---\n\n## Best Practices to Follow\n\n### Code Quality\n- Clean, well-commented code\n- Follow language-specific conventions (Python PEP 8, etc.)\n- Use environment variables for sensitive data\n- Implement error handling and logging\n- Version control with Git\n\n### Security\n- Secure API credentials management\n- HTTPS/SSL for all environments\n- Regular security updates\n- Input validation and sanitization\n- Rate limiting on API calls\n\n### Performance\n- Optimize images for web\n- Lazy loading for images\n- Minimize external dependencies\n- Caching strategy\n- Database query optimization\n\n### Accessibility\n- WCAG AA compliance\n- Keyboard navigation\n- Screen reader compatibility\n- Alt text for all images\n- Sufficient color contrast\n\n---\n\n## Deliverables\n\nAt each phase completion, provide:\n\n1. **Documentation**:\n   - Setup and configuration instructions\n   - Deployment guide\n   - Troubleshooting common issues\n   - API usage documentation\n   - Python script documentation\n\n2. **Code Repository**:\n   - Well-organized Git repository\n   - Docker Compose configuration\n   - Ghost theme source code\n   - Python automation scripts\n   - Configuration files (excluding secrets)\n\n3. **Testing Verification**:\n   - Test plan and results\n   - Known issues or limitations\n   - Performance benchmarks\n\n4. **Migration Guide** (for production phase):\n   - Step-by-step migration process\n   - Rollback procedures\n   - Post-migration checklist\n\n---\n\n## Important Notes\n\n- **Docker Infrastructure**: You have an existing Docker Compose setup with Traefik, PostgreSQL, n8n, Gitea, Woodpecker CI/CD. Leverage these where appropriate.\n- **Demo First**: Always develop and test on the demo environment first. Do not make changes to production until migration phase.\n- **Content Approval**: Every blog post must be manually reviewed and approved before publishing. No automated publishing without human approval.\n- **Target Audience**: Design for the over-40 demographic - prioritize readability, clarity, and accessibility.\n- **Flexibility**: This is an MVP approach. Be prepared to iterate and refine based on testing and user feedback.\n- **Agent Discretion**: Where the prompt says \"Agent should recommend\" or \"Agent decides,\" use your best judgment based on industry best practices and the project goals.\n\n---\n\n## Getting Started\n\nWhen you begin this project:\n1. Confirm understanding of all requirements\n2. Propose architecture and technical approach\n3. Recommend any third-party services (contact form, newsletter, etc.)\n4. Outline the development plan with timelines\n5. Identify any dependencies or prerequisites\n6. Ask clarifying questions if any requirements are unclear\n\nThis is a complex project with multiple components. Take a methodical approach, starting with the MVP demo environment and building incrementally. Quality and functionality are more important than speed at this stage.\n",
  "filePath": "/home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/ghost_website/GHOST_PORTFOLIO_PROMPT.md"
}
```
**Output:**
```
Wrote file successfully.
```
```

---

## Assistant (Build · glm-4.7 · 11.5s)

_Thinking:_

Perfect! I've created a comprehensive, agent-agnostic prompt. Now let me provide a brief summary to the user.

Created comprehensive prompt at `GHOST_PORTFOLIO_PROMPT.md`. This agent-agnostic prompt includes:

**Coverage:**
- Technical requirements (Docker, PostgreSQL, Ghost.js, Python automation)
- Custom theme (modern minimalist, over-40 optimized)
- Content pipeline (social media → Gmail → Ghost with approval)
- Portfolio elements (projects, skills, services, testimonials, contact)
- Blog categories (70% health/tech over-40s, plus DevOps, tech insights)
- SEO & Analytics (Google GA4, keyword ranking, local presence)
- Monetization (freelance services, newsletter, affiliate links)
- Three-phase development (MVP demo → enhanced → production)

**Features:**
- Integration with Twitter/X, Instagram, LinkedIn, Reddit
- Semi-automated Gmail workflow for vetting/correction
- Separate demo & production domains
- Third-party contact form integration
- Full documentation deliverables

The prompt is structured so any AI agent can understand requirements, make informed decisions where needed, and follow best practices throughout development.

---

