<script setup lang="ts">
// @ts-expect-error - epic-spinners does not ship proper TS typings in this project
import { FingerprintSpinner } from 'epic-spinners'

interface Props {
	colorVar?: string
	size?: number
}

const props = defineProps<Props>();
</script>

<template>
    <fingerprint-spinner
            :animation-duration="1500"
            :size="size ? size : 100"
            :color="colorVar ? 'var('+colorVar+')' : 'red'"
    />
</template>

<style lang="css" scoped>

</style>
