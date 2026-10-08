<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import router from "../router"

import { useProductsStore } from '@store/products'
import LoadingSpinner from '@components/LoadingSpinner.vue'
import MessageCard from '@components/MessageCard.vue'
import no_photo from '@img/photo-not-available.webp'
import MaterialSymbolsDelete from '@icon/MaterialSymbolsDelete.vue'


const store = useProductsStore()
const route = useRoute()

const deletePopup = ref<boolean>(false)
const deleteDonePopup = ref<boolean>(false)
const deleteErrorPopup = ref<boolean>(false)

onMounted(async () => {
    try {
        await store.getProduct(Number(route.params.id))
    } catch (error) {
        console.error('Error loading product:', error)
    }
})

const priceChange = computed(() => {
    if (!store.product?.price_history?.length) return 0
    const latest = store.product.price_history[store.product.price_history.length - 1]
    const oldest = store.product.price_history[0]
    return ((latest.price - oldest.price) / oldest.price * 100).toFixed(2)
})

const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString(navigator.language, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    })
}

const popupToggle = (): void => {
    deletePopup.value = !deletePopup.value
}

const handleDelete = async () => {
    try {
        await store.deleteProduct(Number(route.params.id))
        deleteDonePopup.value = true
        deletePopup.value = false
    } catch (error) {
        console.error('Delete failed:', error)
        deleteErrorPopup.value = true
        deletePopup.value = false
    }
}
</script>

<template>
    <div class="container">
        <LoadingSpinner v-if="store.loading" />

        <div v-else-if="store.product" class="product-detail">
            <div class="header">
                <div class="image-section">
                    <img
                        :src="store.product.image_url || no_photo"
                        :alt="store.product.image_url ? store.product.name+' Picture' : 'Picture not available'"
                    />
                </div>

                <div class="info-section">
                    <div class="title">
                        <h1>{{ store.product.name }}</h1>
                        <MaterialSymbolsDelete color="var(--color-error)" width="1.5rem" height="1.5rem" @click="popupToggle" />
                    </div>
                    <div v-if="store.product.category" class="category">
                        {{ store.product.category }}
                    </div>

                    <div class="price-box">
                        <div class="price-item">
                            <span class="label">Current Price</span>
                            <span class="value">{{ store.product.current_price }} $</span>
                        </div>
                        <div class="price-item">
                            <span class="label">Target Price</span>
                            <span :class="['value', store.product.target_reached ? 'success' : 'error']">
                                {{ store.product.target_price }} $
                            </span>
                        </div>
                        <div class="price-item">
                            <span class="label">Change</span>
                            <span :class="['value', Number(priceChange) >= 0 ? 'success' : 'error']">
                                {{ Number(priceChange) >= 0 ? '+' : '' }}{{ priceChange }}%
                            </span>
                        </div>
                    </div>

                <div v-if="store.product.created_at" class="meta">
                    Created at: {{ formatDate(store.product.created_at) }}
                </div>
            </div>
        </div>

        <div v-if="store.product.price_history?.length" class="history-section">
                <h2>Price History</h2>
                <div class="history-grid">
                    <div
                        v-for="history in store.product.price_history"
                        :key="history.id"
                        class="history-card"
                    >
                        <div class="price">${{ history.price }}</div>
                        <div class="date">{{ formatDate(history.checked_at) }}</div>
                    </div>
                </div>
            </div>
        </div>

        <div v-else>
            <MessageCard message="Error loading product..." type="error" />
        </div>

        <MessageCard
            v-if="deletePopup"
            :popup="true"
            type="info"
            title="Delete Product?"
            message="Sure?"
            green-btn-text="Cancel"
            red-btn-text="Delete"
            @green-click="popupToggle"
            @red-click="handleDelete"
        />

        <MessageCard
            v-if="deleteDonePopup"
            :popup="true"
            type="success"
            message="Product deleted successfully!"
            green-btn-text="Go back to products"
            @green-click="router.push('/')"
        />

        <MessageCard
            v-if="deleteErrorPopup"
            :popup="true"
            type="error"
            title="ERROR"
            message="Failed to delete product."
            red-btn-text="Close and try again"
            @red-click="deleteErrorPopup = false"
        />
    </div>
</template>

<style scoped>
.product-detail {
    display: flex;
    flex-direction: column;
    gap: 3rem;
    color: var(--color-text);

    .header {
        display: grid;
        grid-template-columns: 250px 1fr;
        gap: 3rem;
        align-items: start;

        .image-section {
            width: 250px;
            height: 250px;
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: 0px 0px 20px 3px #ffffff78;

            img {
                width: 100%;
                aspect-ratio: 1;
                object-fit: cover;
            }
        }

        .info-section {
            .title {
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                flex-direction: row;

                h1 {
                    margin-bottom: 0.5rem;
                }

                svg {
                    cursor: pointer;
                }
            }

            .category {
                display: inline-block;
                font-size: 0.875rem;
                border-radius: var(--border-radius);
                padding: 0.2rem 1rem;
                background: var(--color-secondary);
                color: var(--color-text);
                max-width: 100%;
                overflow: hidden;
            }

            .price-box {
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 1rem;
                padding: 1.5rem 2rem;
                background: var(--color-surface);
                border-radius: var(--border-radius);
                margin-block: 1.5rem;

                .price-item {
                    display: flex;
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 0.5rem;

                    .label {
                        font-size: 0.875rem;
                        opacity: 0.7;
                    }

                    .value {
                        font-size: 1.5rem;
                        font-weight: bold;

                        &.success {
                            color: var(--color-success);
                        }

                        &.error {
                            color: var(--color-error);
                        }
                    }
                }
            }

            .meta {
                font-size: 0.875rem;
                opacity: 0.7;
                margin-top: 1rem;
            }
        }
    }

    .history-section {
        h2 {
            margin-bottom: 1.5rem;
        }

        .history-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 1rem;

            .history-card {
                background: var(--color-surface);
                padding: 1rem;
                border-radius: var(--border-radius);
                text-align: center;
                border-left: 3px solid var(--color-primary);

                .price {
                    font-size: 1.25rem;
                    font-weight: bold;
                    margin-bottom: 0.5rem;
                }

                .date {
                    font-size: 0.75rem;
                    opacity: 0.7;
                }
            }
        }
    }
}
</style>