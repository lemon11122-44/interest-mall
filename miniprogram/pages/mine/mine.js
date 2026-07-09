const api = require("../../utils/api");

Page({
  data: { user: null, isLoggedIn: false, username: "", password: "" },

  onShow() {
    const userInfo = wx.getStorageSync("userInfo");
    this.setData({ user: userInfo, isLoggedIn: !!userInfo });
  },

  onInput(e) {
    this.setData({ [e.currentTarget.dataset.field]: e.detail.value });
  },

  async login() {
    const { username, password } = this.data;
    if (!username || !password) return wx.showToast({ title: "请填写信息", icon: "none" });
    try {
      const res = await api.login({ username, password });
      getApp().setUser(res.access_token, res.user);
      this.setData({ user: res.user, isLoggedIn: true });
      wx.showToast({ title: "登录成功", icon: "success" });
    } catch { }
  },

  async register() {
    const { username, password } = this.data;
    if (!username || !password) return wx.showToast({ title: "请填写信息", icon: "none" });
    try {
      const res = await api.register({ username, password, nickname: username });
      getApp().setUser(res.access_token, res.user);
      this.setData({ user: res.user, isLoggedIn: true });
      wx.showToast({ title: "注册成功", icon: "success" });
    } catch { }
  },

  goOrders() { wx.navigateTo({ url: "/pages/order/order" }); },
  goAdmin() { wx.navigateTo({ url: "/pages/admin/admin" }); },

  logout() {
    wx.showModal({ title: "提示", content: "确定退出登录？", success: (r) => {
      if (r.confirm) { getApp().logout(); this.setData({ user: null, isLoggedIn: false }); }
    }});
  },
});
