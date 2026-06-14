<script setup lang="ts">
import Header from '@/components/Header.vue'
import HeroSection from '@/components/HeroSection.vue'
import { onMounted } from 'vue'

onMounted(() => {
  document.title = "EDUCLO - Empowering Minds, Shaping Tomorrow"
})
</script>

<template>
  <div class="min-h-screen">
    <Header />
    <main>
      <HeroSection />
      
      <!-- Placeholder for additional sections -->
      <section class="container mx-auto px-6 py-24">
        <div class="text-center">
          <h2 class="font-gemola text-4xl text-foreground md:text-5xl">
            Explore Our <span class="text-primary">Courses</span>
          </h2>
          <p class="mx-auto mt-4 max-w-2xl font-merriweather text-lg text-muted-foreground">
            Discover a wide range of courses designed to help you achieve your learning goals.
          </p>
        </div>
      </section>
    </main>
  </div>
</template>
