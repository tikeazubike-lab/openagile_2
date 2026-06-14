<script setup lang="ts">
import { ref } from 'vue'
import { ArrowRight, Clock } from 'lucide-vue-next'
import Button from '@/components/ui/button/Button.vue'

const categories = ['Computer Science', 'Mathematics', 'Digital Art']

const courses = {
  'Computer Science': [
    {
      title: 'Computer Science 101',
      description: 'Introduction to programming, data structures, and the foundations of computing.',
      level: 'Beginner',
      duration: '8 weeks',
    },
  ],
  'Mathematics': [
    {
      title: 'Advanced Mathematics',
      description: 'Deep dive into calculus, linear algebra, and applied mathematics.',
      level: 'Intermediate',
      duration: '10 weeks',
    },
  ],
  'Digital Art': [
    {
      title: 'Digital Art & Design',
      description: 'Explore the intersection of technology and creativity using modern tools.',
      level: 'Beginner',
      duration: '6 weeks',
    },
  ],
} satisfies Record<string, { title: string; description: string; level: string; duration: string }[]>

const activeCategory = ref('Computer Science')
</script>

<template>
  <section id="courses" class="py-16 md:py-24 bg-secondary/30">
    <div class="container-section">
      <!-- Header -->
      <div
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :visible="{ opacity: 1, y: 0, transition: { duration: 600 } }"
        class="text-center mb-12"
      >
        <p class="section-label mb-3">
          Unlock Your Potential
        </p>
        <h2 class="section-title">
          Explore Our <span class="text-gradient">Courses</span>
        </h2>
        <p class="text-muted-foreground mt-4 max-w-2xl mx-auto">
          Discover a wide range of courses designed to help you achieve your learning goals.
          From tech to arts, we have it all.
        </p>
      </div>

      <!-- Category Tabs -->
      <div class="flex flex-wrap justify-center gap-2 mb-10">
        <button
          v-for="category in categories"
          :key="category"
          @click="activeCategory = category"
          class="px-6 py-3 font-semibold transition-all duration-200"
          :class="activeCategory === category
            ? 'bg-primary text-primary-foreground shadow-md'
            : 'bg-card text-muted-foreground hover:bg-secondary hover:text-foreground'"
          :style="{ borderRadius: 0 }"
        >
          {{ category }}
        </button>
      </div>

      <!-- Course Cards -->
      <transition
        mode="out-in"
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-300 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-4"
      >
        <div
          :key="activeCategory"
          class="grid md:grid-cols-3 gap-6"
        >
          <div
            v-for="category in categories"
            :key="category"
            class="bg-card p-6 shadow-card transition-all duration-300 hover:-translate-y-1"
            :class="{ 'ring-2 ring-primary': category === activeCategory }"
            :style="{ borderRadius: 0 }"
          >
            <div class="flex items-center gap-2 mb-3">
              <span class="text-xs font-semibold text-accent uppercase tracking-wide">
                {{ courses[category as keyof typeof courses][0]!.level }}
              </span>
              <span class="text-muted-foreground">•</span>
              <span class="text-xs text-muted-foreground flex items-center gap-1">
                <Clock :size="12" />
                {{ courses[category as keyof typeof courses][0]!.duration }}
              </span>
            </div>
            <h3 class="text-xl font-bold text-foreground mb-2">
              {{ courses[category as keyof typeof courses][0]!.title }}
            </h3>
            <p class="text-muted-foreground text-sm mb-4">
              {{ courses[category as keyof typeof courses][0]!.description }}
            </p>
            <button class="flex items-center gap-2 text-primary font-semibold text-sm hover:gap-3 transition-all">
              View Details
              <ArrowRight :size="16" />
            </button>
          </div>
        </div>
      </transition>

      <!-- View All Button -->
      <div
        v-motion
        :initial="{ opacity: 0 }"
        :visible="{ opacity: 1, transition: { duration: 600 } }"
        class="text-center mt-10"
      >
        <Button variant="outline" size="lg" class="gap-2">
          View All Courses
          <ArrowRight :size="18" />
        </Button>
      </div>
    </div>
  </section>
</template>
