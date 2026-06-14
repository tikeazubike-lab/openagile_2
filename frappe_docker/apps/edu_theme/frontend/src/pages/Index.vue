<script setup lang="ts">
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import HeroSection from '@/components/sections/HeroSection.vue'
import ClassesSection from '@/components/sections/ClassesSection.vue'
import CoursesSection from '@/components/sections/CoursesSection.vue'
import AboutSection from '@/components/sections/AboutSection.vue'
import TestimonialsSection from '@/components/sections/TestimonialsSection.vue'
import StatsSection from '@/components/sections/StatsSection.vue'
</script>

<template>
  <main class="min-h-screen">
    <Header />
    <HeroSection />
    <ClassesSection />
    <CoursesSection />
    <AboutSection />
    <TestimonialsSection />
    <StatsSection />
    <Footer />
  </main>
</template>
