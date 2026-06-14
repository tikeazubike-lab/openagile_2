<script setup lang="ts">
import Button from '@/components/ui/button/Button.vue'

// In Vue Router we don't have exact same location object structure as React Router, 
// strictly speaking purely for 404 display it might not be needed, but let's just make a simple 404.
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900">
    <div class="text-center">
      <h1 class="text-4xl font-bold mb-4">404</h1>
      <p class="text-xl text-gray-600 dark:text-gray-400 mb-4">
        Oops! Page not found
      </p>
      <router-link to="/">
        <Button>Return to Home</Button>
      </router-link>
    </div>
  </div>
</template>
