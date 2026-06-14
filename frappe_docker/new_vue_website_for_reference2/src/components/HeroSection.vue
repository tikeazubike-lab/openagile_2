<script setup lang="ts">
import Button from "@/components/ui/Button.vue";
import educationIllustration from "@/assets/education-illustration.jpg";
</script>

<template>
  <section class="relative min-h-[calc(100vh-5rem)] overflow-hidden bg-hero">
    <!-- Background Pattern -->
    <div class="absolute inset-0 opacity-10">
      <div class="absolute -right-20 -top-20 h-96 w-96 rounded-full bg-vanilla-custard blur-3xl" />
      <div class="absolute -bottom-20 -left-20 h-80 w-80 rounded-full bg-light-cyan blur-3xl" />
    </div>

    <div class="container relative mx-auto flex min-h-[calc(100vh-5rem)] items-center px-6 py-16">
      <div class="grid gap-12 lg:grid-cols-2 lg:gap-8">
        <!-- Text Content -->
        <div class="flex flex-col justify-center space-y-8">
          <div class="space-y-6">
            <p class="font-raleway text-sm font-semibold uppercase tracking-[0.3em] text-vanilla-custard">
              Welcome to the Future of Learning
            </p>
            
            <h1 class="font-gemola text-5xl leading-tight text-hero-foreground md:text-6xl lg:text-7xl">
              Empowering Minds
              <span class="block">
                Shaping
                <span class="text-vanilla-custard">Tomorrow</span>
              </span>
            </h1>

            <p class="max-w-lg font-merriweather text-lg leading-relaxed text-hero-foreground/80">
              Welcome to the OpenAgile Education Portal. Manage your curriculum, 
              track progress, and access world-class resources through our unified 
              digital campus.
            </p>
          </div>

          <div class="flex flex-wrap gap-4">
            <Button variant="hero" size="lg">
              Get Started Now
            </Button>
            <Button variant="heroOutline" size="lg">
              Learn More
            </Button>
          </div>
        </div>

        <!-- Illustration -->
        <div class="relative flex items-center justify-center lg:justify-end">
          <div class="relative">
            <!-- Decorative frame -->
            <div class="absolute -inset-4 rounded-3xl bg-light-cyan/10 backdrop-blur-sm" />
            
            <!-- Main image container -->
            <div class="relative overflow-hidden rounded-2xl border-4 border-light-cyan/20 shadow-2xl">
              <img
                :src="educationIllustration"
                alt="Education illustration with school supplies and learning elements"
                class="h-auto max-h-[500px] w-full object-cover animate-float"
              />
            </div>

            <!-- Floating decorative elements -->
            <div class="absolute -bottom-6 -left-6 h-12 w-12 rounded-full bg-vanilla-custard animate-pulse-slow" />
            <div class="absolute -right-4 -top-4 h-8 w-8 rounded-full bg-hot-fuchsia animate-float-delayed" />
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom wave decoration -->
    <div class="absolute bottom-0 left-0 right-0">
      <svg
        viewBox="0 0 1440 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        class="w-full"
        preserveAspectRatio="none"
      >
        <path
          d="M0 120L60 105C120 90 240 60 360 45C480 30 600 30 720 37.5C840 45 960 60 1080 67.5C1200 75 1320 75 1380 75L1440 75V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z"
          class="fill-background"
        />
      </svg>
    </div>
  </section>
</template>
