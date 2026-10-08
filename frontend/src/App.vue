<script setup lang="ts">
import HeaderBar from './views/HeaderBar.vue';
import { RouterView } from 'vue-router';

</script>

<template>
    <HeaderBar />

    <router-view v-slot="{ Component }">
        <transition name="fade">
            <component :is="Component" />
        </transition>
    </router-view>
</template>

<style scoped>

</style>
