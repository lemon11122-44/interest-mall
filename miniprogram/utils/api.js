const CONFIG = require("./config");
const API_BASE = CONFIG.API_BASE;

const request = (url, method = "GET", data = {}) => {
  return new Promise((resolve, reject) => {
    const token = wx.getStorageSync("token");
    const header = { "Content-Type": "application/json" };
    if (token) header["Authorization"] = `Bearer ${token}`;

    wx.request({
      url: API_BASE + url,
      method,
      header,
      data,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          wx.showToast({ title: res.data?.detail || "请求失败", icon: "none" });
          reject(res.data);
        }
      },
      fail: (err) => {
        console.error("网络错误:", err)
        wx.showToast({ title: "网络错误，请检查域名白名单配置", icon: "none" });
        reject(err);
      },
    });
  });
};

module.exports = {
  calcMode1: (data) => request("/api/calculator/mode1", "POST", data),
  calcMode2: (data) => request("/api/calculator/mode2", "POST", data),
  register: (data) => request("/api/auth/register", "POST", data),
  login: (data) => request("/api/auth/login", "POST", data),
  getUserInfo: () => request("/api/user/me"),
  getProducts: (page = 1, category = "") =>
    request(`/api/products?page=${page}&pageSize=20&category=${category}`),
  getProduct: (id) => request(`/api/products/${id}`),
  getCart: () => request("/api/cart"),
  addCart: (data) => request("/api/cart", "POST", data),
  updateCart: (id, data) => request(`/api/cart/${id}`, "PUT", data),
  removeCart: (id) => request(`/api/cart/${id}`, "DELETE"),
  clearCart: () => request("/api/cart", "DELETE"),
  createOrder: (data) => request("/api/orders", "POST", data),
  getOrders: () => request("/api/orders"),
  getOrder: (id) => request(`/api/orders/${id}`),
  payOrder: (id) => request(`/api/orders/${id}/pay`, "POST"),
  cancelOrder: (id) => request(`/api/orders/${id}/cancel`, "POST"),
  adminProducts: (page = 1) => request(`/api/admin/products/all?page=${page}`),
  createProduct: (data) => request("/api/admin/products", "POST", data),
  updateProduct: (id, data) => request(`/api/admin/products/${id}`, "PUT", data),
  deleteProduct: (id) => request(`/api/admin/products/${id}`, "DELETE"),
  adminOrders: (status = "") => request(`/api/admin/orders?status=${status}`),
  updateOrderStatus: (id, status) =>
    request(`/api/admin/orders/${id}/status?status=${status}`, "PUT"),
  adminUsers: () => request("/api/admin/users"),
  adminStats: () => request("/api/admin/stats"),
};
