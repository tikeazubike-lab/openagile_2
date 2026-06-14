<script setup lang="ts">
import { GraduationCap, BookOpen, Building2, Briefcase } from 'lucide-vue-next'

const classes = [
  {
    title: 'Primary',
    subtitle: 'Foundation Years',
    icon: BookOpen,
    bgColor: 'bg-primary',
    textColor: 'text-primary-foreground',
  },
  {
    title: 'Secondary',
    subtitle: 'Core Curriculum',
    icon: GraduationCap,
    bgColor: 'bg-yellow',
    textColor: 'text-foreground',
  },
  {
    title: 'Higher Ed',
    subtitle: 'University Prep',
    icon: Building2,
    bgColor: 'bg-coral',
    textColor: 'text-foreground',
  },
  {
    title: 'Professional',
    subtitle: 'Career Skills',
    icon: Briefcase,
    bgColor: 'bg-accent',
    textColor: 'text-accent-foreground',
  },
]
</script>

<template>
  <section class="py-16 md:py-24 bg-background">
    <div class="container-section">
      <!-- Section Header -->
      <div
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :visible="{ opacity: 1, y: 0, transition: { duration: 600 } }"
        class="text-center mb-12"
      >
        <h2 class="text-3xl md:text-4xl font-bold text-foreground">
          OUR CLASSES
        </h2>
      </div>

      <!-- Cards -->
      <div
        class="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6"
      >
        <div
          v-for="(classItem, index) in classes"
          :key="classItem.title"
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible="{ opacity: 1, y: 0, transition: { delay: index * 100 } }"
          class="p-6 md:p-8 shadow-card hover:shadow-card-hover transition-all duration-300 cursor-pointer group"
          :class="classItem.bgColor"
          :style="{ borderRadius: 0 }"
        >
          <div class="flex flex-col items-center text-center">
            <div
              class="mb-4 p-3 rounded-full bg-background/20"
              :class="classItem.textColor"
            >
              <component :is="classItem.icon" :size="28" />
            </div>
            <h3 class="text-xl md:text-2xl font-bold mb-1" :class="classItem.textColor">
              {{ classItem.title }}
            </h3>
            <p class="text-sm opacity-80" :class="classItem.textColor">
              {{ classItem.subtitle }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
