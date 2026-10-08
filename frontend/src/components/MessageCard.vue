<script setup lang="ts">
interface Props {
    popup?: boolean
    type?: 'success' | 'error' | 'info'
    title?: string
    message: string
    redBtnText?: string
    greenBtnText?: string
    onRedClick?: () => void
    onGreenClick?: () => void
}

withDefaults(defineProps<Props>(), {
    popup: false,
    type: 'info'
})
</script>

<template>
    <div :class="['card-container', popup ? 'popup' : '']">
        <div :class="['card', type]">
            <h3 v-if="title">{{ title }}</h3>
            <p>{{ message }}</p>
            <div v-if="greenBtnText || redBtnText" class="btn-container">
                <button v-if="greenBtnText" class="success" @click="onGreenClick">{{ greenBtnText }}</button>
                <button v-if="redBtnText" class="error" @click="onRedClick">{{ redBtnText }}</button>
            </div>
        </div>
    </div>
</template>

<style lang="css" scoped>
.card-container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;

    &.popup {
        position: fixed;
        top: 0;
        left: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 1000;
    }
}

.card {
    min-width: 300px;
    padding: 1.5rem;
    background-color: var(--color-surface);
    border-radius: var(--border-radius);
    text-align: center;

    &.success {
        color: var(--color-success);
        box-shadow: inset 0 0 10px 1px var(--color-success);
    }

    &.error {
        color: var(--color-error);
        box-shadow: inset 0 0 10px 1px var(--color-error);
    }

    &.info {
        /* color: var(--color-primary); */
        color: var(--color-text);
        box-shadow: inset 0 0 10px 1px var(--color-primary);
    }

    h3 {
        margin-bottom: 0.5rem;
    }

    .btn-container {
        display: inline-flex;
        justify-content: space-evenly;
        gap: 1rem;
        margin-top: 1.5rem;

        button {
            font-size: 1rem;
            font-weight: bold;
            padding: 0.5rem 2rem;
            color: #fff;
            /* color: var(--color-secondary); */
            border: none;
            border-radius: var(--border-radius);
            cursor: pointer;
            transition: opacity 0.3s ease;

            &.success {
                background: var(--color-success);
            }

            &.error {
                background: var(--color-error);
            }

            &:hover {
                opacity: 0.7;
            }
        }
    }
}
</style>
