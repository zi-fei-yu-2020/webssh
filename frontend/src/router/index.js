import { createRouter, createWebHistory } from "vue-router";
import Terminal from "@/views/terminal/terminal.vue";
import NotFound from "@/views/404.vue";
import Admin from "@/layout/admin.vue"
import TerminalInter from "@/views/terminal/terminal_inter.vue"

const routes = [{
    path: "/",
    component: Admin,
    children: [{
        path: "/",
        component: Terminal,
        name: "后台首页"
    },
    {
        path: "/terminal",
        component: TerminalInter,
        name: "终端连接",
        meta: { requiredMenu: "/" },
    }]
}, {
    path: "/:pathMatch(.*)*",
    component: NotFound,
    name: 'NotFound'
},
]

const router = createRouter({
    history: createWebHistory(),
    routes
})



export default router
