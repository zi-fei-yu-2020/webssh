<template>
    <div class="iframe-container">
      <iframe
        src="http://159.75.69.201/status/zifeiyu"
        frameborder="0"
        width="100%"
        height="100%"
      ></iframe>
    </div>
  </template>
  
  <script setup>
  </script>
  
  <style scoped>
  .iframe-container {
    width: 100%;
    height: 100vh; /* 设定高度为视口高度 */
    overflow: hidden; /* 防止出现滚动条 */
  }
  iframe {
    width: 100%;
    height: 100%;
    border: none; /* 移除iframe边框 */
  }
  </style>
  