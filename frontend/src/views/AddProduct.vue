<script setup lang="ts">
import { useProductsStore } from '@store/products'
import { ref } from 'vue'
import { z } from 'zod'

import LoadingSpinner from '@components/LoadingSpinner.vue'
import MessageCard from '@components/MessageCard.vue'
import { Product } from '@types'


const store = useProductsStore()

const productCreated = ref<boolean>(false)

const schema = z.object({
    name: z.string()
        .regex(/^[a-zA-Z0-9\s\-()]+$/, 'Only letters, numbers and - ( ) allowed')
        .max(255, 'Max 255 characters')
        .min(1, 'Name is required'),
    category: z.string()
        .regex(/^[a-zA-Z0-9\s\-]*$/, 'Only letters, numbers and - allowed')
        .max(100, 'Max 100 characters')
        .optional()
        .transform(val => val || null),
    image_url: z.string()
        .max(500, 'Max URL 100 characters')
        .optional()
        .transform(val => val || null),
    target_price: z.coerce.string()
        .regex(/^\d+(\.\d{1,2})?$/, 'Invalid price format (e.g., 10.50)')
        .min(1, 'Current price is required')
        .transform(Number).refine(val => val > 0, 'Must be > 0'),
    current_price: z.coerce.string()
        .regex(/^\d+(\.\d{1,2})?$/, 'Invalid price format (e.g., 10.50)')
        .min(1, 'Current price is required')
        .transform(Number).refine(val => val > 0, 'Must be > 0'),
})

const formData = ref<Product>({
    name: '',
    category: '' ,
    current_price: 0,
    target_price: 0,
    image_url: ''
})

const errors = ref<Record<string, string>>({})
const debounceMap = ref<Record<string, ReturnType<typeof setTimeout>>>({})


const validateField = (field: keyof typeof formData.value) => {
    try {
        schema.pick({ [field]: true } as any).parse({ [field]: formData.value[field] })
        delete errors.value[field]
    } catch (error) {
        if (error instanceof z.ZodError) {
            error.issues.forEach(err => {
                errors.value[field] = err.message
            })
        }
    }

    if (field === "target_price" || field === "current_price") {
        const target = Number(formData.value.target_price)
        const current = Number(formData.value.current_price)

        if (target > 0 && current > 0 && target >= current) {
            errors.value["target_price"] = "Target price must be less than current price"
        } else if (errors.value["target_price"] === "Target price must be less than current price") {
            delete errors.value["target_price"]
        }
    }
}

const debounceValidate = (field: keyof typeof formData.value) => {
    clearTimeout(debounceMap.value[field])
    debounceMap.value[field] = setTimeout(() => validateField(field), 3000)
}


const handleSubmit = async () => {
    productCreated.value = false
    // check all fields first
    Object.keys(formData.value).forEach(field => {
        validateField(field as keyof typeof formData.value)
    })

    // break if there is errors
    if (Object.keys(errors.value).length) {
        return
    }

    try {
        const validatedData = schema.parse(formData.value)
        const result = await store.createProduct(validatedData)
        console.log(result)
        formData.value = { name: '', category: '', current_price: 0, target_price: 0, image_url: '' }
        productCreated.value = true
    } catch (error) {
        console.error(error)
    }
}
</script>

<template>
    <div class="container">
        <form @submit.prevent="handleSubmit" class="form">
            <div class="form-group">
                <label for="name">Name : <span>*</span></label>
                <input id="name" v-model="formData.name" type="text" placeholder="Product Name"
                    :class="{ error: errors.name }"
                    @input="debounceValidate('name')"
                    >
                <span v-if="errors.name" class="error-msg">{{ errors.name }}</span>
            </div>

            <div class="form-group">
                <label for="category">Category :</label>
                <input id="category" v-model="formData.category" type="text" placeholder="Product Category"
                    :class="{ error: errors.category }"
                    @input="debounceValidate('category')"
                    >
                <span v-if="errors.category" class="error-msg">{{ errors.category }}</span>
            </div>

            <div class="form-group">
                <label for="current_price">Current Price : <span>*</span></label>
                <input id="current_price" v-model="formData.current_price" type="text" inputmode="decimal" placeholder="0.00"
                    :class="{ error: errors.current_price }"
                    @input="debounceValidate('current_price')"
                    >
                <span v-if="errors.current_price" class="error-msg">{{ errors.current_price }}</span>
            </div>

            <div class="form-group">
                <label for="target_price">Target Price : <span>*</span></label>
                <input id="target_price" v-model="formData.target_price" type="text" inputmode="decimal" placeholder="0.00"
                    :class="{ error: errors.target_price }"
                    @input="debounceValidate('target_price')"
                    >
                <span v-if="errors.target_price" class="error-msg">{{ errors.target_price }}</span>
            </div>

            <div class="form-group">
                <label for="image_url">Image :</label>
                <input id="image_url" type="file" accept="image/*"
                    :class="{ error: errors.image_url }"
                    @change="(e) => formData.image_url = (e.target as HTMLInputElement).files?.[0]?.name || ''"
                    @input="debounceValidate('image_url')"
                    >
                <span v-if="errors.image_url" class="error-msg">{{ errors.image_url }}</span>
            </div>

            <button type="submit" class="btn" :disabled="Object.keys(errors).length ? true : false">
                <span v-if="!store.loading">ADD</span>
                <span v-else="store.loading">
                    <LoadingSpinner colorVar="--color-text" :size="32"/>
                </span>
            </button>

            <div v-if="productCreated">
                <MessageCard message="Product added successfully..." type="success" />
            </div>

            <div v-if="store.errored">
                <MessageCard message="Failed to add the product..." type="error" />
            </div>
        </form>
    </div>
</template>

<style type="css" scoped>
.form {
    width: 100%;
    max-width: 400px;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    color: var(--color-text);

    .form-group {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;

        label {
            font-weight: 500;
            font-size: 0.875rem;

            & > span {
                color: var(--color-error);
            }
        }

        input {
            padding: 0.5rem 1rem;
            background-color: var(--color-surface);
            color: var(--color-text);
            border: 1px solid transparent;
            border-radius: var(--border-radius);
            font-size: 1rem;

            &:focus {
                outline: none;
                border-color: var(--color-primary);
                box-shadow: 0 0 0 3px #818cf840;
            }

            &.error {
                border-color: var(--color-error);
            }
        }

        .error-msg {
            font-size: 0.75rem;
            color: var(--color-error);
        }
    }

    .btn {
        height: 2.5rem;
        width: 10rem;
        align-self: center;
        font-size: 1rem;
        font-weight: bold;
        padding: 0.25rem 2.5rem;
        margin-top: 1.5rem;
        background: var(--color-primary);
        color: var(--color-secondary);
        border: none;
        border-radius: var(--border-radius);
        cursor: pointer;
        opacity: 1;
        transition: opacity 0.3s ease;

        &:hover:not(:disabled) {
            opacity: 0.7;
        }

        &:disabled {
            background: var(--color-text);
            color: var(--color-secondary);
            cursor: not-allowed;
            box-shadow: inset 0 0 10px 4px var(--color-error);
        }

        > span {
            display: inline-block;
        }
    }
}
</style>
