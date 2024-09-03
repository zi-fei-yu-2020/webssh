<template>
    <div class="container">
        <Xterm :wsuri="wsuri"></Xterm>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Xterm from "@/views/terminal/xterm.vue";
import { BASE_URL } from '@/api/api.js';

console.log("Baseurl:", BASE_URL);

// 去掉 BASE_URL 中的协议部分
const cleanBaseUrl = BASE_URL.replace(/^https?:\/\//, '');
console.log("cleanBaseUrl", cleanBaseUrl);

// Initialize wsuri with a ref
const wsuri = ref('');

onMounted(() => {
    const url = window.location.href;
    const getqyinfo = url.split('?')[1];
    const getqys = new URLSearchParams('?' + getqyinfo);
    const id = getqys.get('id');
    const host = getqys.get('host');

    document.title = host + "在线终端WEBSSH";

    // 根据协议选择WebSocket协议
    const protocol = window.location.protocol === 'http:' ? 'ws://' : 'wss://';

    // 构建WebSocket URL
    wsuri.value = `${protocol}${cleanBaseUrl.replace('/api', '').replace('8000','8001')}/ws/webssh/?id=${id}`;
    console.log("Constructed wsuri:", wsuri.value);
});
</script>

<style lang="scss" scoped>
.container {
    background: black;
    height: 100%;
    width: 100%;
    overflow: auto;
}
</style>
