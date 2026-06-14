<script setup lang="ts">
import Button from '@/components/ui/button/Button.vue'
import educationHero from '@/assets/education-hero.png'
</script>

<template>
  <section class="relative bg-hero-gradient pt-24 pb-16 md:pt-32 md:pb-24 overflow-hidden">
    <!-- Background Pattern -->
    <div class="absolute inset-0 opacity-10">
      <div class="absolute top-20 left-10 w-32 h-32 rounded-full bg-primary-foreground/20" />
      <div class="absolute bottom-20 right-20 w-48 h-48 rounded-full bg-primary-foreground/10" />
      <div class="absolute top-1/2 left-1/3 w-24 h-24 rounded-full bg-primary-foreground/15" />
    </div>

    <div class="container-section relative z-10">
      <div class="grid lg:grid-cols-2 gap-12 items-center">
        <!-- Content -->
        <div
          v-motion
          :initial="{ opacity: 0, x: -30 }"
          :enter="{ opacity: 1, x: 0, transition: { duration: 600 } }"
          class="text-center lg:text-left"
        >
          <p class="text-primary-foreground/80 text-sm font-semibold tracking-widest uppercase mb-4">
            Welcome to the Future of Learning
          </p>
          <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold text-primary-foreground leading-tight mb-6">
            Empowering Minds
            <span class="block">
              Shaping
              <span class="text-yellow">Tomorrow</span>
            </span>
          </h1>
          <p class="text-primary-foreground/80 text-lg mb-8 max-w-lg mx-auto lg:mx-0">
            Welcome to our innovative education portal. Manage your curriculum,
            track progress, and access resources through our seamless digital campus.
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
            <Button variant="accent" size="lg">
              Get Started Now
            </Button>
            <Button variant="heroOutline" size="lg">
              Learn More
            </Button>
          </div>
        </div>

        <!-- Hero Image -->
        <div
          v-motion
          :initial="{ opacity: 0, x: 30 }"
          :enter="{ opacity: 1, x: 0, transition: { duration: 600, delay: 200 } }"
          class="relative flex justify-center lg:justify-end"
        >
          <div class="relative">
            <img
              :src="educationHero"
              alt="Education illustration with books, graduation cap, and learning tools"
              class="w-full max-w-md lg:max-w-lg drop-shadow-2xl"
              v-motion
              :enter="{ y: [0, -10, 0], transition: { duration: 3000, repeat: Infinity, ease: 'easeInOut' } }"
            >
            <!-- Floating badge -->
            <div
              class="absolute -bottom-4 -right-4 bg-card px-4 py-2 rounded-lg shadow-lg"
              v-motion
              :initial="{ opacity: 0, scale: 0.8 }"
              :enter="{ opacity: 1, scale: 1, transition: { delay: 800 } }"
            >
              <p class="text-sm font-semibold text-foreground">
                🎓 Join 2000+ Students
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Wave divider -->
    <div class="absolute bottom-0 left-0 right-0">
      <svg
        viewBox="0 0 1440 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        class="w-full"
        preserveAspectRatio="none"
      >
        <path
          d="M0 120L60 110C120 100 240 80 360 70C480 60 600 60 720 65C840 70 960 80 1080 85C1200 90 1320 90 1380 90L1440 90V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0V120Z"
          fill="hsl(var(--background))"
        />
      </svg>
    </div>
  </section>
</template>
