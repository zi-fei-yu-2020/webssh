import axios from "@/utils/axios.js"

//创建终端设备
export function create_device(data) {
    return axios.post("webssh/terminal/create", data)
}

//查看终端列表
export function device_list(page, search='') {
    return axios.get(`webssh/terminal/list?page=${page}&search=${search}`)
}


// 对终端设备进行删除
export function delete_device(data) {
    return axios.delete(`webssh/terminal/delete/${data}`)
}

//对终端设备信息进行更新
export function update_device(data) {
    return axios.put(`webssh/terminal/update/${data.id}`, data);
}


import { config } from "@/utils/config.js"
const BASE_URL = import.meta.env.MODE === 'development'
    ? config.development.apiBaseUrl
    : config.production.apiBaseUrl

export function uploadFile(data) {
    return axios.post(`${BASE_URL}/form/upload`, data);
}

export {
    BASE_URL
}