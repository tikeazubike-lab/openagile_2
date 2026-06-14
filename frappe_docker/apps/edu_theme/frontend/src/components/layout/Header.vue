<script setup lang="ts">
import { ref } from 'vue'
import Button from '@/components/ui/button/Button.vue'
import { Menu, X } from 'lucide-vue-next'


const navLinks = [
  { href: '#', label: 'Home' },
  { href: '#courses', label: 'Courses' },
  { href: '#about', label: 'Why Choose Us' },
  { href: '#news', label: 'News' },
  { href: '#contact', label: 'Contact' },
]

const mobileMenuOpen = ref(false)
</script>

<template>
  <header class="fixed top-0 left-0 right-0 z-50 bg-hero-gradient">
    <div class="container-section">
      <nav class="flex items-center justify-between h-16 md:h-20">
        <!-- Logo -->
        <a href="#" class="flex items-center gap-2">
          <span class="text-2xl font-bold text-primary-foreground tracking-tight">
            EDUCLO
          </span>
        </a>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center gap-1">
          <a
            v-for="link in navLinks"
            :key="link.label"
            :href="link.href"
            class="px-4 py-2 text-primary-foreground/90 hover:text-primary-foreground font-medium transition-colors"
          >
            {{ link.label }}
          </a>
        </div>

        <!-- Desktop CTAs -->
        <div class="hidden md:flex items-center gap-3">
          <Button variant="nav" size="sm" as="a" href="/app">
            Login
          </Button>
          <Button variant="heroOutline" size="sm">
            Apply
          </Button>
        </div>

        <!-- Mobile Menu Toggle -->
        <button
          class="md:hidden p-2 text-primary-foreground"
          @click="mobileMenuOpen = !mobileMenuOpen"
          aria-label="Toggle menu"
        >
          <X v-if="mobileMenuOpen" :size="24" />
          <Menu v-else :size="24" />
        </button>
      </nav>
    </div>

    <!-- Mobile Menu -->
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2 scale-95"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 -translate-y-2 scale-95"
    >
      <div
        v-if="mobileMenuOpen"
        class="md:hidden bg-primary-dark overflow-hidden"
      >
        <div class="container-section py-4 flex flex-col gap-2">
          <a
            v-for="link in navLinks"
            :key="link.label"
            :href="link.href"
            class="px-4 py-3 text-primary-foreground/90 hover:text-primary-foreground hover:bg-primary-foreground/10 rounded-lg font-medium transition-colors"
            @click="mobileMenuOpen = false"
          >
            {{ link.label }}
          </a>
          <div class="flex gap-3 mt-4 pt-4 border-t border-primary-foreground/20">
            <Button variant="nav" size="sm" class="flex-1" as="a" href="/app">
              Login
            </Button>
            <Button variant="heroOutline" size="sm" class="flex-1">
              Apply
            </Button>
          </div>
        </div>
      </div>
    </transition>
  </header>
</template>
