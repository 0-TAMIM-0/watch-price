<script setup lang="ts">
import { useProductsStore } from '@store/products'
import { onMounted } from 'vue'

import LoadingSpinner from '@components/LoadingSpinner.vue'
import MessageCard from '@components/MessageCard.vue'
import ProductCard from '@components/ProductCard.vue'


const store = useProductsStore()

onMounted(async () => {
    try {
        await store.getAllProducts()
    } catch (error) {
        // Handle error - show toast, etc
        console.log('Error loading products')
    }
})
</script>

<template>
    <div class="container">
        <div v-if="store.loading">
            <LoadingSpinner colorVar="--color-primary" />
        </div>

        <div v-else-if="store.errored">
            <MessageCard message="Error loading products..." type="error" />
        </div>

        <div v-else-if="!store.products?.length">
            <MessageCard message="There is no products..." type="info" />
        </div>

        <div v-else class="products-container">
            <ProductCard v-for="product in store.products" :key="product.id" :product="product" />
        </div>
    </div>
</template>

<style scoped>
.products-container {
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: space-evenly;
    flex-wrap: wrap;
    gap: 2rem;
}
</style>
