<template>
  <nav class="bg-white shadow-sm py-4 sticky top-0 z-50">
    <div class="container mx-auto px-6 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <div class="bg-brand-yellow text-brand-blue font-bold px-3 py-1 rounded">EDUMA</div>
      </div>
      <div class="hidden md:flex space-x-8 text-gray-600 font-medium text-sm uppercase tracking-wide">
        <a href="#" class="hover:text-brand-blue transition">Home</a>
        <a href="#" class="hover:text-brand-blue transition">Courses</a>
        <a href="#" class="hover:text-brand-blue transition">Admissions</a>
        <a href="#" class="hover:text-brand-blue transition">News</a>
        <a href="#" class="hover:text-brand-blue transition">Contact</a>
      </div>
      <div class="flex items-center gap-4 text-sm font-semibold">
        <a href="/login" class="text-gray-600 hover:text-brand-blue transition">LOGIN</a>
        <a href="/app" class="bg-brand-blue text-white px-5 py-2 rounded hover:bg-blue-800 transition shadow-lg shadow-blue-900/20">
          DESK
        </a>
      </div>
    </div>
  </nav>
</template>
