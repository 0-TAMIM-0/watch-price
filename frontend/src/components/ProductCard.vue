<script setup lang="ts">
import router from "../router";

import type { Product } from "@types";

import no_photo from "@img/photo-not-available.webp";

interface Props {
	product: Product
}

defineProps<Props>();

const pushRouter = (id: number): void => {
    router.push({ name: 'productDetail', params: { id: Number(id) } })
}

const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString(navigator.language, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}
</script>

<template>
    <div class="product-card" @click="pushRouter(Number(product.id))">
        <div class="product-img">
            <img
                :src="product.image_url || no_photo"
                :alt="product.image_url ? product.name+' Picture' : 'Picture not available'"
            />
        </div>
        <div class="product-info-header">
            <h4 v-if="product.name">{{ product.name }}</h4>
            <div v-if="product.category" class="product-cat">
                {{ product.category }}
            </div>
        </div>
        <div v-if="product.created_at" class="product-date">
            Created at: {{ formatDate(product.created_at) }}
        </div>
        <div class="product-price">
            <div>Target price: {{ product.target_price.toFixed(2) }} €</div>
            <div>
                Current price:
                <span :class="product.target_reached ? 'target-reached' : 'target-not-reached'">
                    {{ product.current_price.toFixed(2) }} €
                </span>
            </div>
        </div>
    </div>
</template>

<style lang="css" scoped>
.product-card {
    max-width: 300px;
    padding: 1.5rem;
    background-color: var(--color-surface);
    border-radius: var(--border-radius);
    color: var(--color-text);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.3s ease;

    &:hover {
        transform: scale(1.02);
    }

    .product-img {
        width: 250px;
        height: 250px;
        margin-bottom: 1rem;
        border-radius: var(--border-radius);
        overflow: hidden;
        box-shadow: 0px 0px 20px 3px #ffffff78;

        & > img {
            width: 100%;
            aspect-ratio: 1;
            object-fit: cover;
        }
    }

    .product-info-header {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        margin-bottom: 0.3rem;

        .product-cat {
            font-size: 0.875rem;
            border-radius: var(--border-radius);
            padding: 0.2rem 1rem;
            background: var(--color-secondary);
            color: var(--color-text);
            max-width: 100%;
            overflow: hidden;
        }
    }

    .product-date {
        width: 100%;
        padding-inline-start: 0.5rem;
        font-size: 0.8rem;
        opacity: 0.7;
    }

    .product-price {
        margin-top: 1rem;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: flex-start;

        .target-reached {
            color: var(--color-success);
        }

        .target-not-reached {
            color: var(--color-error);
        }
    }
}
</style>
