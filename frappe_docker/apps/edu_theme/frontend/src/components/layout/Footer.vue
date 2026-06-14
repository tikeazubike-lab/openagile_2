<script setup lang="ts">
import Button from '@/components/ui/button/Button.vue'
import Input from '@/components/ui/input/Input.vue'
import { Facebook, Twitter, Instagram, Linkedin } from 'lucide-vue-next'

const footerLinks = {
  Learn: ['Courses', 'Mentors', 'Pricing', 'Certifications'],
  Company: ['About Us', 'Careers', 'Blog', 'Contact'],
}

const socialLinks = [
  { icon: Twitter, href: '#', label: 'Twitter' },
  { icon: Facebook, href: '#', label: 'Facebook' },
  { icon: Instagram, href: '#', label: 'Instagram' },
  { icon: Linkedin, href: '#', label: 'LinkedIn' },
]
</script>

<template>
  <footer id="contact" class="bg-[#0e1829] pt-16 pb-8">
    <div class="container-section">
      <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12">
        <!-- Brand & Newsletter -->
        <div class="lg:col-span-2">
          <h3 class="text-2xl font-bold text-primary-foreground mb-4">
            EDUCLO
          </h3>
          <p class="text-primary-foreground/60 mb-6 max-w-sm">
            Empowering the next generation of thinkers, creators, and innovators
            across the world. Join our community today.
          </p>
          <div class="space-y-3">
            <p class="text-sm font-semibold text-primary-foreground">
              Subscribe to our newsletter
            </p>
            <div class="flex gap-2">
              <Input
                type="email"
                placeholder="Enter your email"
                class="bg-[#192c4b] border-primary-foreground/20 text-primary-foreground placeholder:text-primary-foreground/40"
              />
              <Button variant="accent" size="default">
                Subscribe
              </Button>
            </div>
          </div>
        </div>

        <!-- Links -->
        <div v-for="(links, title) in footerLinks" :key="title">
          <h4 class="font-semibold text-primary-foreground mb-4 uppercase tracking-wide text-sm">
            {{ title }}
          </h4>
          <ul class="space-y-3">
            <li v-for="link in links" :key="link">
              <a
                href="#"
                class="text-primary-foreground/60 hover:text-primary-foreground transition-colors"
              >
                {{ link }}
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Divider -->
      <div class="border-t border-primary-foreground/10 pt-8">
        <div class="flex flex-col md:flex-row items-center justify-between gap-4">
          <p class="text-sm text-primary-foreground/40">
            © 2025 Educlo. All rights reserved.
          </p>
          <div class="flex items-center gap-4">
            <a
              v-for="social in socialLinks"
              :key="social.label"
              :href="social.href"
              class="w-10 h-10 rounded-full bg-primary-foreground/10 flex items-center justify-center text-primary-foreground/60 hover:bg-primary-foreground/20 hover:text-primary-foreground transition-colors"
              :aria-label="social.label"
            >
              <component :is="social.icon" :size="18" />
            </a>
          </div>
          <div class="flex gap-6 text-sm text-primary-foreground/40">
            <a href="#" class="hover:text-primary-foreground transition-colors">
              Terms
            </a>
            <a href="#" class="hover:text-primary-foreground transition-colors">
              Privacy
            </a>
            <a href="#" class="hover:text-primary-foreground transition-colors">
              Cookies
            </a>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>
