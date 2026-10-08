import { createRouter, createWebHistory, type RouteRecordRaw, type Router } from 'vue-router'


const routes: RouteRecordRaw[] = [
    {
        path: '/',
        name: 'productsList',
        component: () => import('../views/ProductsList.vue')
    },
    {
        path: '/products/:id',
        name: 'productDetail',
        component: () => import('../views/ProductDetail.vue')
    },
    {
        path: '/add',
        name: 'addProduct',
        component: () => import('../views/AddProduct.vue')
    },
    {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: () => import('../views/NotFound.vue')
    }
]

const router: Router = createRouter({
    history: createWebHistory(),
    routes,
    // scrollBehavior(to, from, savedPosition) {
    scrollBehavior() {
        // always scroll to top
        return {
            top: 0,
            behavior: 'smooth',
        }
    },
})

export default router
