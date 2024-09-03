<template>
      <div class="common-layout">
    <el-container>
      <el-header>
        <f-header/>
      </el-header>
      <el-container>
        <el-aside :width="asideWidth" class="bg-light-50">
            <f-menu/>
        </el-aside>
        <el-main>
            <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>



<script setup>
import FHeader from './components/FHeader.vue';
import FMenu from './components/FMenu.vue';
import { asideWidth } from '@/utils/asideWidth';
</script>

<style>
.el-aside{
    transition: all 0.2s;
}
</style>