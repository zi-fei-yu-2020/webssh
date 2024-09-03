<template>
    <el-card shadow="always" class="border-0 m-4">
        <!-- 新增|刷新 -->
        <div class="flex items-center justify-between mb-16">
            <el-button type="primary" size="small" @click="handleCreate">新增</el-button>
            <el-tooltip effect="dark" content="刷新数据" placement="top">
                <el-button text @click="getData">
                    <el-icon :size="20"><Refresh /></el-icon>
                </el-button>
            </el-tooltip>
        </div>

        <el-table
            :data="tableData"
            stripe
            style="width: 100%"
            v-loading="loading"
        >
            <!-- <el-table-column prop="id" label="用户id" /> -->
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="create_time" label="创建时间" />
            <el-table-column prop="permission_id" label="用户权限" />
            <el-table-column label="操作" align="center">
                <template #default="scope">
                    <el-button type="primary" size="small" text>修改</el-button>

                    <el-popconfirm
                        width="220"
                        confirm-button-text="确认"
                        cancel-button-text="取消"
                        icon-color="#626AEF"
                        title="确认删除用户?"
                        @confirm="handleDelete(scope.row.id)"
                    >
                        <template #reference>
                            <el-button size="small" type="primary" text
                                >删除</el-button
                            >
                        </template>
                    </el-popconfirm>
                </template>
            </el-table-column>
        </el-table>

        <div class="flex items-center justify-center mt-5">
            <el-pagination
                background
                layout="prev, pager, next"
                :total="total"
                :current-page="currentPage"
                :page-size="limit"
                @current-change="getData"
            />
        </div>

        <form-drawer
            ref="formDrawerRef"
            title="新增用户"
            @submit="handleSubmit"
        >
            <el-form
                ref="formRef"
                :rules="rules"
                :model="form"
                label-width="80px"
                size="small"
            >
                <el-form-item prop="username" label="用户名">
                    <el-input
                        v-model="form.username"
                        placeholder="请输入用户名"
                    ></el-input>
                </el-form-item>
                <el-form-item prop="password" label="密码">
                    <el-input
                        type="password"
                        v-model="form.password"
                        placeholder="请输入密码"
                        show-password
                    ></el-input>
                </el-form-item>
            </el-form>
        </form-drawer>
    </el-card>
</template>


<script setup>
import { ref,reactive } from 'vue'
import { get_userlist, add_user,delete_user,update_user } from '@/api/api.js'
import { toast } from '@/utils/tips.js'
import FormDrawer from '@/components/FormDrawer.vue'

//类型定义
const tableData = ref([])
const loading = ref(false)
const form = reactive({
    username: '',
    password: ''
})

const rules = {
    username: [
        {
            required: true,
            message: '账号不能为空',
            trigger: 'blur'
        }
    ],
    password: [
        {
            required: true,
            message: '密码不能为空',
            trigger: 'blur'
        }
    ]
}

//分页
const currentPage = ref(1)
const total = ref(0)
const limit = ref(10)

//获取数据
function getData(p = null) {
    if (typeof p == 'number') {
        currentPage.value = p
    }
    loading.value = true
    get_userlist(currentPage.value)
        .then((res) => {
            if (res.data.code === 200) {
                tableData.value = res.data.result.data
                total.value = res.data.result.totalCount
            } else {
                toast(res.data.result.data, 'error')
            }
        })
        .finally(() => {
            loading.value = false
        })
}
getData()

//添加用户
const formDrawerRef = ref(null)
const formRef = ref(null)
const handleSubmit = () => {
    formRef.value.validate((valid) => {
        if (!valid) {
            return false
        }
        formDrawerRef.value.showLoading()
        add_user(form)
            .then((response) => {
                if (response.data.code === 200) {
                    toast('添加用户成功')
                    getData(1)
                    formDrawerRef.value.close()
                } else{ 
                    toast(response.data.result.data,"error")
                }
            })
            .finally(() => {
                formDrawerRef.value.hideLoading()
            })
    })
}

//删除
const handleDelete = (id) => {
    loading.value = true
    delete_user(id).then(
        res => { 
            if (res.data.code === 200) {
                toast("删除成功")
                getData()
            } else { 
                toast(res.data.result.data)
            }
        }
    ).finally(() => { 
        loading.value = false
    }

    )
}


//让抽屉出现
function handleCreate() { 
    formDrawerRef.value.open()
}

</script>