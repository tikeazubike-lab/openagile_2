import { createRouter, createWebHistory } from 'vue-router'
import Index from '../pages/Index.vue'
import NotFound from '../pages/NotFound.vue'

const router = createRouter({
    history: createWebHistory('/landing'),
    routes: [
        {
            path: '/',
            name: 'Index',
            component: Index,
        },
        {
            path: '/:pathMatch(.*)*',
            name: 'NotFound',
            component: NotFound,
        },
    ],
})

export default router
