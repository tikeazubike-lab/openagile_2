<script setup lang="ts">
import Toaster from '@/components/ui/sonner/Sonner.vue'
import { TooltipProvider } from 'radix-vue'
</script>

<template>
  <TooltipProvider>
    <Toaster />
    <router-view />
  </TooltipProvider>
</template>
