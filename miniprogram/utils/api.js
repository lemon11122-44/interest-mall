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
        console.error("网络错误:", err);
        wx.showToast({ title: "网络错误", icon: "none" });
        reject(err);
      },
    });
  });
};

module.exports = {
  // 利息计算器
  calcMode1: (data) => request("/api/calculator/mode1", "POST", data),
  calcMode2: (data) => request("/api/calculator/mode2", "POST", data),

  // 用户
  register: (data) => request("/api/auth/register", "POST", data),
  login: (data) => request("/api/auth/login", "POST", data),
  getUserInfo: () => request("/api/user/me"),

  // 扣费管理
  getFees: () => request("/api/fees"),
  createFee: (data) => request("/api/fees", "POST", data),
  updateFee: (id, data) => request(`/api/fees/${id}`, "PUT", data),
  deleteFee: (id) => request(`/api/fees/${id}`, "DELETE"),
  getFeeStats: () => request("/api/fees/stats"),
};
