<script setup lang="ts">

</script>

<template>
    <header>
        <nav>
            <router-link to="/">Products</router-link>
            <router-link to="/add">Add Product</router-link>
        </nav>
    </header>
</template>

<style lang="css" scoped>
header {
    width: 100%;
    height: 3rem;
    background-color: var(--color-surface);
    padding-inline: 2rem;

    nav {
        height: 100%;
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        gap: 2rem;
        align-items: center;

        a {
            position: relative;
            color: var(--color-text);

            &:hover::after {
                content: '';
                position: absolute;
                bottom: -4px;
                left: 0;
                right: 20%;
                height: 2px;
                background: var(--color-primary);
                animation: slideIn 0.3s ease;
            }

            &.router-link-active {
                color: var(--color-primary);

                &::after {
                    content: '';
                    position: absolute;
                    bottom: -4px;
                    left: 0;
                    right: 20%;
                    height: 2px;
                    background: var(--color-primary);
                    animation: slideIn 0.3s ease;
                }
            }
        }
    }
}

@keyframes slideIn {
    from {
        width: 0;
    }
    to {
        width: 80%;
    }
}
</style>
