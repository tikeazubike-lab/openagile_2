# Deployment Instructions (Copy this to your Engineer)
**Subject:** Full Frontend Migration (Vue 3) - Action Required

The `edu_theme` frontend has been completely migrated to a new architecture using Vue 3, Tailwind, and VueUse Motion.

## Steps to Deploy:

1. **Pull the latest code.**
2. **Clean & Install:**
   ```bash
   cd apps/edu_theme/frontend
   rm -rf node_modules package-lock.json # Recommended
   npm install
   ```
3. **Build:**
   ```bash
   npm run build
   ```
4. **Clear Cache:**
   ```bash
   bench clear-cache
   ```

## Verification:

- [ ] Ensure the site loads at `/landing`.
- [ ] Clicking **Login** should take you to the Desk (`/app`).
- [ ] Animations and styles should match the new "Premium Polish" reference.

## 📂 New File Structure (Reference)

The components have been reorganized into a nested structure:

- **Layout:**
  - `src/components/layout/Footer.vue`
  - `src/components/layout/Header.vue`

- **Sections:**
  - `src/components/sections/HeroSection.vue`
  - `src/components/sections/ClassesSection.vue`
  - `src/components/sections/CoursesSection.vue`
  - `src/components/sections/AboutSection.vue`
  - `src/components/sections/StatsSection.vue`
  - `src/components/sections/TestimonialsSection.vue`
