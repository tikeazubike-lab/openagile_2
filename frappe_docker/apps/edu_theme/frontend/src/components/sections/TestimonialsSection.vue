<script setup lang="ts">
import { ref, computed } from 'vue'
import { ChevronLeft, ChevronRight, Quote } from 'lucide-vue-next'
import studentImage from '@/assets/student-testimonial.jpg'

const testimonials = [
  {
    quote: 'The depth of the curriculum at Educlo challenged me to think differently. It wasn\'t just about learning code; it was about solving real-world problems.',
    name: 'Sarah Jenkins',
    role: 'Web Development Graduate',
    image: studentImage,
  },
  {
    quote: 'Educlo\'s supportive community and expert mentors helped me transition into a completely new career. The hands-on projects were invaluable.',
    name: 'Michael Chen',
    role: 'Data Science Student',
    image: studentImage,
  },
  {
    quote: 'The flexibility of the courses allowed me to balance learning with my full-time job. I couldn\'t have done it without Educlo\'s approach.',
    name: 'Emily Rodriguez',
    role: 'UX Design Graduate',
    image: studentImage,
  },
]

const currentIndex = ref(0)

const next = () => {
  currentIndex.value = (currentIndex.value + 1) % testimonials.length
}

const prev = () => {
  currentIndex.value = (currentIndex.value - 1 + testimonials.length) % testimonials.length
}

const current = computed(() => testimonials[currentIndex.value]!)
</script>

<template>
  <section class="py-16 md:py-24 bg-secondary/30">
    <div class="container-section">
      <!-- Header -->
      <div
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :visible="{ opacity: 1, y: 0, transition: { duration: 600 } }"
        class="flex items-center justify-between mb-12"
      >
        <div>
          <p class="section-label mb-2">
            Voices
          </p>
          <h2 class="section-title">
            Student Stories
          </h2>
        </div>
        <div class="flex gap-2">
          <button
            class="w-10 h-10 border border-border rounded-full flex items-center justify-center hover:bg-secondary transition-colors"
            @click="prev"
            aria-label="Previous testimonial"
          >
            <ChevronLeft :size="20" />
          </button>
          <button
            class="w-10 h-10 bg-foreground text-background rounded-full flex items-center justify-center hover:bg-foreground/80 transition-colors"
            @click="next"
            aria-label="Next testimonial"
          >
            <ChevronRight :size="20" />
          </button>
        </div>
      </div>

      <!-- Testimonial Card -->
      <transition
        mode="out-in"
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="opacity-0 translate-x-12"
        enter-to-class="opacity-100 translate-x-0"
        leave-active-class="transition duration-300 ease-in"
        leave-from-class="opacity-100 translate-x-0"
        leave-to-class="opacity-0 -translate-x-12"
      >
        <div
          :key="currentIndex"
          class="grid md:grid-cols-2 gap-8 items-center"
        >
          <!-- Image -->
          <div class="relative">
            <div
              class="overflow-hidden aspect-[4/5]"
              :style="{ borderRadius: 0 }"
            >
              <img
                :src="current.image"
                :alt="current.name"
                class="w-full h-full object-cover"
              >
            </div>
          </div>

          <!-- Quote -->
          <div class="flex flex-col justify-center">
            <Quote class="text-accent mb-6" :size="48" />
            <blockquote class="text-xl md:text-2xl font-medium text-foreground leading-relaxed mb-8">
              "{{ current.quote }}"
            </blockquote>
            <div>
              <p class="text-lg font-bold text-foreground">
                {{ current.name }}
              </p>
              <p class="text-muted-foreground">
                {{ current.role }}
              </p>
            </div>
          </div>
        </div>
      </transition>

      <!-- Dots indicator -->
      <div class="flex justify-center gap-2 mt-8">
        <button
          v-for="(_, index) in testimonials"
          :key="index"
          @click="currentIndex = index"
          class="w-2 h-2 rounded-full transition-all"
          :class="index === currentIndex
            ? 'w-8 bg-primary'
            : 'bg-border hover:bg-muted-foreground'"
          :aria-label="`Go to testimonial ${index + 1}`"
        />
      </div>
    </div>
  </section>
</template>
