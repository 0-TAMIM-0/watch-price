import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

import type { Product } from '@types'


const api = axios.create({
    baseURL: '/api'
})

export const useProductsStore = defineStore('products', () => {
    const products = ref<Product[]>([])
    const product = ref<Product>()

    const loading = ref<boolean>(false)
    const errored = ref<boolean>(false)


    const getAllProducts = async (): Promise<void> => {
        loading.value = true
        errored.value = false

        products.value = []

        try {
            const { data } = await api.get<Product[]>('/products')
            products.value = data
        } catch (error) {
            errored.value = true
            console.error('Failed to fetch products:', error)
        } finally {
            loading.value = false
        }
    }


    const createProduct = async (product: {
        name: string
        category: string | null
        target_price: number
        current_price: number
        image?: File | null
    }): Promise<Product> => {

        loading.value = true
        errored.value = false

        const form = new FormData()
        form.append('name', product.name)
        form.append('target_price', String(product.target_price))
        form.append('current_price', String(product.current_price))
        if (product.category) form.append('category', product.category)
        if (product.image) form.append('image', product.image)

        try {
            const { data } = await api.post<Product>('/products', form)
            return data
        } catch (error) {
            errored.value = true
            console.error('Failed to create product:', error)
            throw error
        } finally {
            loading.value = false
        }
    }


    const getProduct = async (id: number): Promise<void> => {
        loading.value = true
        errored.value = false

        product.value = undefined

        try {
            const { data } = await api.get<Product>(`/products/${id}`)
            product.value = data
        } catch (error) {
            errored.value = true
            console.error(`Failed to fetch product ${id}:`, error)
        } finally {
            loading.value = false
        }
    }


    const deleteProduct = async (id: number): Promise<string> => {
        loading.value = true
        errored.value = false

        try {
            const { data } = await api.delete<{ message: string }>(`/products/${id}`)
            return data.message
        } catch (error) {
            errored.value = true
            console.error(`Failed to delete product ${id}:`, error)
            throw error
        } finally {
        loading.value = false
        }
    }


    return { products, product, loading, errored, getAllProducts, createProduct, getProduct, deleteProduct }
})
