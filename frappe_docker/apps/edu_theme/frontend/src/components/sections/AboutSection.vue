<script setup lang="ts">
import { Play } from 'lucide-vue-next'
import classroomImage from '@/assets/classroom.jpg'

const stats = [
  { value: '98%', label: 'Student Satisfaction' },
  { value: '120+', label: 'Expert Teachers' },
]
</script>

<template>
  <section id="about" class="py-16 md:py-24 bg-background">
    <div class="container-section">
      <div class="grid lg:grid-cols-2 gap-12 items-center">
        <!-- Image -->
        <div
          v-motion
          :initial="{ opacity: 0, x: -30 }"
          :visible="{ opacity: 1, x: 0, transition: { duration: 600 } }"
          class="relative"
        >
          <div class="relative overflow-hidden" :style="{ borderRadius: 0 }">
            <img
              :src="classroomImage"
              alt="Modern classroom with students learning"
              class="w-full h-auto object-cover"
            >
            <!-- Overlay gradient -->
            <div class="absolute inset-0 bg-gradient-to-t from-navy/20 to-transparent" />
          </div>
          <!-- Decorative element -->
          <div
            class="absolute -bottom-4 -right-4 w-24 h-24 bg-accent"
            :style="{ borderRadius: 0 }"
          />
          <div
            class="absolute -top-4 -left-4 w-16 h-16 bg-primary"
            :style="{ borderRadius: 0 }"
          />
        </div>

        <!-- Content -->
        <div
          v-motion
          :initial="{ opacity: 0, x: 30 }"
          :visible="{ opacity: 1, x: 0, transition: { duration: 600 } }"
        >
          <div class="flex items-center gap-3 mb-4">
            <div class="w-12 h-0.5 bg-accent" />
            <span class="section-label">Since 2010</span>
          </div>
          <h2 class="section-title mb-6">
            Welcome to Educlo
          </h2>
          <p class="text-muted-foreground mb-6 leading-relaxed">
            We are more than just a digital campus. We are a thriving community of
            innovators, thinkers, and leaders. Our curriculum is designed to challenge
            the status quo and prepare you for a rapidly evolving world.
          </p>

          <!-- Stats -->
          <div class="grid grid-cols-2 gap-6 mb-8">
            <div v-for="stat in stats" :key="stat.label">
              <p class="text-4xl md:text-5xl font-bold text-primary">
                {{ stat.value }}
              </p>
              <p class="text-sm text-muted-foreground mt-1">
                {{ stat.label }}
              </p>
            </div>
          </div>

          <!-- Video CTA -->
          <button class="flex items-center gap-3 group">
            <div class="w-12 h-12 bg-foreground text-background rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
              <Play :size="20" fill="currentColor" />
            </div>
            <span class="font-semibold text-foreground group-hover:text-primary transition-colors">
              Watch Our Story
            </span>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>
