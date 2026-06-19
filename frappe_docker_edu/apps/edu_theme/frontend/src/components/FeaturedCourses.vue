<script setup>
import CourseCard from './CourseCard.vue'

defineProps({
  courses: {
    type: Array,
    default: () => []
  }
})
</script>

<template>
  <section class="py-24 bg-white" id="courses">
    <div class="container mx-auto px-6">
      <div class="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-6">
        <div class="max-w-xl">
          <span class="text-brand-blue font-bold tracking-[0.2em] uppercase text-xs mb-4 block">Our Curriculum</span>
          <h2 class="text-4xl font-extrabold text-slate-900 leading-tight">
            Explore our <span class="text-brand-blue">Featured</span> Courses
          </h2>
        </div>
        <div>
          <button class="text-slate-500 font-bold hover:text-brand-blue transition flex items-center gap-2 group">
            Browse All Courses 
            <span class="group-hover:translate-x-1 transition">→</span>
          </button>
        </div>
      </div>

      <div class="grid md:grid-cols-3 gap-8">
        <CourseCard 
          v-for="(course, index) in courses" 
          :key="index" 
          :course="course" 
        />
      </div>
    </div>
  </section>
</template>
