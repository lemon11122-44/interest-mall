// 初始化云开发 - ⬇️ 把 YOUR_ENV_ID 替换成你的云开发环境ID
wx.cloud.init({
  env: 'YOUR_ENV_ID',
  traceUser: true,
})

const callCloudFunction = (path, method = 'GET', data = {}) => {
  return new Promise((resolve, reject) => {
    const token = wx.getStorageSync('token')
    wx.cloud.callFunction({
      name: 'api',
      data: { path, method, data, token },
      success: (res) => {
        const result = res.result
        if (result.code === 0) {
          resolve(result.data)
        } else if (result.code === 401) {
          wx.removeStorageSync('token')
          wx.removeStorageSync('userInfo')
          reject(result)
        } else {
          wx.showToast({ title: result.error || '请求失败', icon: 'none' })
          reject(result)
        }
      },
      fail: (err) => {
        wx.showToast({ title: '网络错误', icon: 'none' })
        reject(err)
      },
    })
  })
}

module.exports = {
  calcMode1: (data) => callCloudFunction('/api/calculator/mode1', 'POST', data),
  calcMode2: (data) => callCloudFunction('/api/calculator/mode2', 'POST', data),
  register: (data) => callCloudFunction('/api/auth/register', 'POST', data),
  login: (data) => callCloudFunction('/api/auth/login', 'POST', data),
  getUserInfo: () => callCloudFunction('/api/user/me'),
  getProducts: (page = 1, category = '') =>
    callCloudFunction(`/api/products?page=${page}&pageSize=20&category=${category}`),
  getProduct: (id) => callCloudFunction(`/api/products/${id}`),
  getCart: () => callCloudFunction('/api/cart'),
  addCart: (data) => callCloudFunction('/api/cart', 'POST', data),
  updateCart: (id, data) => callCloudFunction(`/api/cart/${id}`, 'PUT', data),
  removeCart: (id) => callCloudFunction(`/api/cart/${id}`, 'DELETE'),
  clearCart: () => callCloudFunction('/api/cart', 'DELETE'),
  createOrder: (data) => callCloudFunction('/api/orders', 'POST', data),
  getOrders: () => callCloudFunction('/api/orders'),
  getOrder: (id) => callCloudFunction(`/api/orders/${id}`),
  payOrder: (id) => callCloudFunction(`/api/orders/${id}/pay`, 'POST'),
  cancelOrder: (id) => callCloudFunction(`/api/orders/${id}/cancel`, 'POST'),
  adminProducts: (page = 1) => callCloudFunction(`/api/admin/products/all?page=${page}`),
  createProduct: (data) => callCloudFunction('/api/admin/products', 'POST', data),
  updateProduct: (id, data) => callCloudFunction(`/api/admin/products/${id}`, 'PUT', data),
  deleteProduct: (id) => callCloudFunction(`/api/admin/products/${id}`, 'DELETE'),
  adminOrders: (status = '') => callCloudFunction(`/api/admin/orders?status=${status}`),
  updateOrderStatus: (id, status) =>
    callCloudFunction(`/api/admin/orders/${id}/status?status=${status}`, 'PUT'),
  adminUsers: () => callCloudFunction('/api/admin/users'),
  adminStats: () => callCloudFunction('/api/admin/stats'),
}
