<template>
  <footer class="bg-slate-900 text-slate-400 pt-16 pb-8">
    <div class="container mx-auto px-6">
      <div class="grid md:grid-cols-4 gap-12 mb-12">
        <div class="col-span-2">
          <div class="text-white font-bold text-2xl mb-6">EDUMA</div>
          <p class="max-w-sm leading-relaxed">
            The standard for modern educational institutions. Integrated with ERPNext for seamless management of students, faculty, and assets.
          </p>
        </div>
        <div>
          <h4 class="text-white font-bold mb-6">Links</h4>
          <ul class="space-y-4 text-sm">
            <li><a href="#" class="hover:text-white transition">About Us</a></li>
            <li><a href="#" class="hover:text-white transition">Privacy Policy</a></li>
            <li><a href="#" class="hover:text-white transition">Terms of Service</a></li>
          </ul>
        </div>
        <div>
          <h4 class="text-white font-bold mb-6">Contact</h4>
          <ul class="space-y-4 text-sm">
            <li>info@zubbystudio.shop</li>
            <li>+234 800 EDUMA</li>
          </ul>
        </div>
      </div>
      <div class="border-t border-slate-800 pt-8 text-center text-xs tracking-widest uppercase">
        <p>&copy; {{ new Date().getFullYear() }} Eduma. Built on Frappe Framework.</p>
      </div>
    </div>
  </footer>
</template>
