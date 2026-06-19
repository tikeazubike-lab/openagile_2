<script setup>
defineProps({
  data: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <section class="bg-brand-blue text-white py-24 relative overflow-hidden">
    <!-- Decorative background elements -->
    <div class="absolute top-0 right-0 w-1/3 h-full bg-blue-800/20 -skew-x-12 transform translate-x-1/2"></div>
    
    <div class="container mx-auto px-6 flex flex-col md:flex-row items-center">
      <div class="md:w-3/5 z-10">
        <span class="text-brand-yellow font-bold tracking-[0.2em] uppercase text-xs mb-4 block">Welcome to the future of learning</span>
        <h1 class="text-5xl md:text-7xl font-extrabold leading-[1.1] mb-8" v-html="data.hero_title">
        </h1>
        <p class="text-blue-100 text-lg mb-10 max-w-lg leading-relaxed">
          {{ data.hero_subtitle }}
        </p>
        <div class="flex gap-4">
          <a :href="data.cta_link" class="bg-brand-yellow text-brand-blue font-bold py-4 px-10 rounded shadow-xl hover:scale-105 transition active:scale-95 inline-block text-center">
            {{ data.cta_text }}
          </a>
          <button class="border-2 border-white/30 hover:border-white text-white font-bold py-4 px-10 rounded transition">
            LEARN MORE
          </button>
        </div>
      </div>
      
      <div class="md:w-2/5 mt-16 md:mt-0 relative">
        <div class="bg-white/5 p-4 rounded-3xl backdrop-blur-md border border-white/10 shadow-2xl overflow-hidden aspect-square flex items-center justify-center">
           <div class="text-white/20 text-center">
             <div class="text-8xl mb-4">🎓</div>
             <span class="text-sm font-medium tracking-widest uppercase">Portal Preview</span>
           </div>
        </div>
        <!-- Floaters -->
        <div class="absolute -top-6 -left-6 bg-brand-yellow p-4 rounded-2xl shadow-lg animate-bounce">
          ✨
        </div>
      </div>
    </div>
  </section>
</template>