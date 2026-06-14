<script setup lang="ts">
const stats = [
  { value: '2295+', label: 'Active Students' },
  { value: '55', label: 'Expert Mentors' },
  { value: '20+', label: 'Countries' },
  { value: '43%', label: 'Course Completion' },
]
</script>

<template>
  <section class="py-12 md:py-16 bg-[#0e1829]">
    <div class="container-section">
      <div
        class="grid grid-cols-2 md:grid-cols-4 gap-8"
      >
        <div
          v-for="(stat, index) in stats"
          :key="stat.label"
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible="{ opacity: 1, y: 0, transition: { duration: 600, delay: index * 100 } }"
          class="text-center"
        >
          <p class="text-3xl md:text-4xl lg:text-5xl font-bold text-primary-foreground">
            {{ stat.value }}
          </p>
          <p class="text-sm text-primary-foreground/60 mt-2 uppercase tracking-wide">
            {{ stat.label }}
          </p>
        </div>
      </div>
    </div>
  </section>
</template>
