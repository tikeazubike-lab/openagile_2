<script setup>
import { onMounted, ref } from 'vue'
import Navbar from './components/Navbar.vue'
import Hero from './components/Hero.vue'
import FeaturedCourses from './components/FeaturedCourses.vue'
import Footer from './components/Footer.vue'

const landingData = ref({
  hero_title: 'Empowering Minds <br/> Shaping Tomorrow',
  hero_subtitle: 'Access world-class education portals, manage your curriculum, and track your progress through our unified digital campus.',
  cta_text: 'GET STARTED',
  cta_link: '#',
  featured_courses: []
})

const isLoading = ref(true)

onMounted(async () => {
  try {
    const response = await fetch('/api/method/edu_theme.api.get_landing_page_data')
    const result = await response.json()
    if (result.message) {
      landingData.value = result.message
    }
  } catch (error) {
    console.error('Failed to fetch landing page data:', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="min-h-screen flex flex-col font-sans text-slate-900 bg-slate-50">
    <Navbar />
    <main class="flex-grow">
      <Hero :data="landingData" />
      <FeaturedCourses :courses="landingData.featured_courses" />
    </main>
    <Footer />
  </div>
</template>