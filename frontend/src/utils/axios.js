import axios from "axios";
import { ElNotification } from 'element-plus'
import { getToken } from '@/utils/auth.js';

const service = axios.create({
    baseURL: "/api"
})

// 添加请求拦截器
service.interceptors.request.use(function (config) {

    // 往header头自动添加token
    const token = getToken()
    if (token) {
        config.headers["Authorization"] = "Bearer "+token
    }

    return config;
}, function (error) {
    // 对请求错误做些什么
    return Promise.reject(error);
});




// 添加响应拦截器
// service.interceptors.response.use(function (response) {
//     // 对响应数据做点什么
//     return response.data;
// }, function (error) {
    // // 对响应错误做点什么
    // console.log(error);

    // ElNotification({
    //     message: error.response.data.message || "请求失败",
    //     type: 'error',
    //     duration: 3000
    // })
//     return Promise.reject(error);
// })

// service.interceptors.response.use(
//     (response) => {
//       return response;
//     },
//     (error) => {
//       if (error.response && (error.response.status === 401 || error.response.status === 500)) {
//         // Token 过期，显示提示并重定向到登录页面
//         removeToken('admin-token');
//         const router = useRouter();
//         router.push('/login');
//         toast('Token过期,请重新登录!!!', 'error');
//       }
//       return Promise.reject(error);
//     }
//   );




export default service