<script setup>
defineProps({
  course: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <div class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden hover:shadow-xl hover:shadow-blue-900/5 transition duration-300 group">
    <div class="h-48 bg-slate-50 flex items-center justify-center text-6xl group-hover:scale-110 transition duration-500">
      {{ course.image }}
    </div>
    <div class="p-6">
      <div class="flex items-center gap-2 mb-3">
        <span class="px-2 py-0.5 bg-blue-50 text-brand-blue text-[10px] font-bold uppercase tracking-wider rounded">
          {{ course.level }}
        </span>
      </div>
      <h3 class="text-xl font-bold text-slate-900 mb-2 group-hover:text-brand-blue transition">
        {{ course.title }}
      </h3>
      <p class="text-slate-500 text-sm mb-4 line-clamp-2">
        {{ course.description }}
      </p>
      <div class="flex items-center justify-between pt-4 border-t border-slate-50">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-xs">
            👤
          </div>
          <span class="text-xs font-medium text-slate-600">{{ course.instructor }}</span>
        </div>
        <button class="text-brand-blue font-bold text-sm hover:underline">
          View Details
        </button>
      </div>
    </div>
  </div>
</template>
