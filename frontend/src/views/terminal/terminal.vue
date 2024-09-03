<template>
    <el-card shadow="never" class="border-0">
        <!-- 新增|刷新 -->
        <div class="flex items-center justify-between mb-4">
            <div class="tableSelect" ref="tableSelect">
                <el-form :inline="true" :model="formInline" label-position="left">
                    <el-form-item label="主机：">
                        <el-input v-model="search_content" size="default" maxlength="60" clearable
                            placeholder="服务器IP/域名" @change="search" style="width:200px"></el-input>
                    </el-form-item>
                    <el-form-item label=""><el-button @click="getData" type="primary"
                            icon="Search">查询</el-button></el-form-item>
                    <el-form-item label=""><el-button type="primary" icon="Plus"
                            @click="openDialog()">新增</el-button></el-form-item>
                </el-form>
            </div>


            <el-tooltip effect="dark" content="刷新数据" placement="top">
                <el-button text @click="getData">
                    <el-icon :size="20">
                        <Refresh />
                    </el-icon>
                </el-button>
            </el-tooltip>
        </div>


        <el-table
            :data="tableData"
            stripe
            style="width: 100%"
            v-loading="loading"
        >
            <el-table-column prop="host" label="主机"></el-table-column>
            <el-table-column prop="port" label="端口"></el-table-column>
            <el-table-column prop="remark" label="备注"></el-table-column>
            <el-table-column prop="typename" label="验证方式"></el-table-column>
            <el-table-column prop="username" label="用户名"></el-table-column>
            <el-table-column prop="created_time" label="创建时间"></el-table-column>
            <el-table-column label="操作" fixed="right" width="260">
                <template #header>
                    <div style="display: flex;justify-content: space-between;align-items: center;">
                        <div>操作</div>
                    </div>
                </template>
                <template #default="scope">
                    <el-button size="mini" type="danger" @click="opencontent(scope.row)">
                        打开终端
                    </el-button>
                    <el-button size="mini" type="danger" @click="openUpdateDialog(scope.row)">
                        编辑
                    </el-button>
                    <el-button size="mini" type="danger" @click="showRejectDelete(scope.row.id)">
                        删除
                    </el-button>
                </template>
            </el-table-column>
        </el-table>

        <div class="flex items-center justify-center mt-5">
            <el-pagination background layout="prev, pager, next" :total="total" :current-page="currentPage"
                :page-size="limit" @current-change="getData" :props="{
                    search: search_content
                }" />
        </div>


        <el-dialog :title="formData.id ? '编辑终端' : '新增终端'" width="30%" v-model="DialogVisible"
            :close-on-click-modal="false">
            <el-form :inline="false" :model="formData" :rules="device_rules" ref="rulesForm" label-position="right"
                label-width="auto">
                <el-form-item label="服务器IP：" prop="host">
                    <el-input v-model="formData.host"></el-input>
                </el-form-item>
                <el-form-item label="端口号：" prop="port">
                    <el-input-number v-model="formData.port" :min="1" :max="65536"></el-input-number>
                </el-form-item>
                <el-form-item label="SSH账号：" prop="username">
                    <el-input v-model="formData.username"></el-input>
                </el-form-item>
                <el-form-item label="验证方式：" prop="type">
                    <el-radio-group v-model="formData.type">
                        <el-radio-button label="0">密码验证</el-radio-button>
                        <el-radio-button label="1">私钥验证</el-radio-button>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="密码：" prop="password" v-if="formData.type == '0'">
                    <el-input v-model="formData.password" :show-password="true"></el-input>
                </el-form-item>
                <el-form-item label="私钥：" prop="pkey" v-if="formData.type == '1'">
                    <el-input v-model="formData.pkey" type="textarea" :rows="2"></el-input>
                </el-form-item>
                <el-form-item label="私钥密码：" prop="pkey_passwd" v-if="formData.type == '1'">
                    <el-input v-model="formData.pkey_passwd"></el-input>
                </el-form-item>
                <el-form-item label="备注：" prop="remark">
                    <el-input v-model="formData.remark" type="textarea" :rows="2"></el-input>
                </el-form-item>
            </el-form>
            <div style="text-align: right">
                <el-button @click="DialogVisible = false">取消</el-button>
                <el-button type="primary" @click="savedeviceForm">确定</el-button>
            </div>
        </el-dialog>
    </el-card>
</template>


<script setup>
import { ref, reactive, onMounted } from 'vue'
import { create_device, device_list, delete_device, update_device } from '@/api/api.js';
import { toast } from "@/utils/tips.js";
import { ElMessageBox } from "element-plus";
//分页
const loading = ref(false)
const currentPage = ref(1)
const total = ref(0)
const limit = ref(10)

//Dialog
const DialogVisible = ref(false);

//formData
const formData = reactive({
    username: '',
    port: 22,
    host: '',
    type: '0',
    remark: '',
    password: '',
    pkey_passwd: '',
    pkey: '',
});

function openUpdateDialog(rowData) {
    openDialog(rowData);
}

function openDialog(data = null) {
    if (data) {
        Object.assign(formData, data);
    } else {
        resetForm();
    }
    DialogVisible.value = true;
}



function resetForm() {
    formData.username = '';
    formData.port = 22;
    formData.host = '';
    formData.type = '0';
    formData.remark = '';
    formData.password = '';
    formData.pkey_passwd = '';
    formData.pkey = ''
    delete formData.id;
}



const device_rules = {
    host: [
        { required: true, message: '请输入服务器IP', trigger: 'blur' }
    ],
    port: [
        { required: true, message: '请输入端口号', trigger: 'blur' }
    ],
    username: [
        { required: true, message: '请输入SSH账号', trigger: 'blur' }
    ],
};



//创建和更新
const rulesForm = ref(null);
function savedeviceForm() {
    rulesForm.value.validate((valid) => {
        if (valid) {
            if (formData.id) {
                // 更新已有终端信息
                update_device(formData).then((resp) => {
                    if (resp.data.code === 200) {
                        toast("更新终端信息成功");
                        DialogVisible.value = false;
                        getData(); // 重新获取数据
                    } else {
                        toast(resp.data.message);
                    }
                });
            } else {
                // 新增终端信息
                create_device(formData).then((resp) => {
                    if (resp.data.code === 200) {
                        toast("新增终端信息成功");
                        DialogVisible.value = false;
                        getData(); // 重新获取数据
                    } else {
                        toast(resp.data.message);
                    }
                });
            }
        } else {
            return false;
        }
    });
}

//删除终端
function showRejectDelete(id) {
    ElMessageBox.confirm("确定删除此记录吗？", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
    })
        .then(() => {
            delete_device(id)
                .then((resp) => {
                    if (resp.data.code === 200) {
                        toast("删除成功");
                        getData();
                    } else {
                        toast(resp.data.message, "error");
                    }
                })
                .catch(() => {
                    toast("删除失败", "error");
                });
        })
        .catch(() => { });
}


//打开终端
function opencontent(row) {
    let baseurl = window.location.protocol + "//" + window.location.host
    window.open(baseurl + "/terminal?id=" + row.id + "&host=" + row.host, '_blank');
}

const search_content = ref('')
const tableData = ref([]);
function getData(p = null) {
    if (typeof p === "number") {
        currentPage.value = p;
    } else {
        currentPage.value = 1;
    }

    loading.value = true;

    const searchQuery = search_content.value;
    device_list(currentPage.value, searchQuery)
        .then((res) => {
            if (res.data.code === 200) {
                tableData.value = res.data.result.data;
                total.value = res.data.result.totalCount;
            } else {
                toast(res.data.result.data, (type = "error"));
            }
        })
        .finally(() => {
            loading.value = false;
        });
}

onMounted(() => {
    getData();
});

</script>