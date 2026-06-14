<script setup lang="ts">
import Button from '@/components/ui/Button.vue'

const navLinks = [
  { name: "Home", href: "#" },
  { name: "Courses", href: "#courses" },
  { name: "Admissions", href: "#admissions" },
  { name: "News", href: "#news" },
  { name: "Contact", href: "#contact" },
]
</script>

<template>
  <header class="sticky top-0 z-50 w-full bg-hero/95 backdrop-blur-sm">
      <div class="container mx-auto flex h-20 items-center justify-between px-6">
        <!-- Logo -->
        <div class="flex items-center gap-2">
          <span class="rounded-lg bg-vanilla-custard px-3 py-1.5 font-gemola text-xl font-bold text-ink-black">
            EDUCLO
          </span>
        </div>

        <!-- Navigation -->
        <nav class="hidden items-center gap-8 md:flex">
          <a
            v-for="link in navLinks"
            :key="link.name"
            :href="link.href"
            class="font-raleway text-sm font-medium uppercase tracking-wider text-hero-foreground/80 transition-colors hover:text-hero-foreground"
          >
            {{ link.name }}
          </a>
        </nav>

        <!-- Auth Buttons -->
        <div class="flex items-center gap-4">
          <Button variant="ghost" class="text-hero-foreground hover:bg-hero-foreground/10">
            Login
          </Button>
          <Button variant="hero" size="default">
            Desk
          </Button>
        </div>
      </div>
    </header>
</template>
