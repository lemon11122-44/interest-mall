const api = require("../../utils/api");

Page({
  data: { product: null, quantity: 1, cartCount: 0 },

  onLoad(options) {
    this.loadProduct(options.id);
  },

  async loadProduct(id) {
    const p = await api.getProduct(id);
    this.setData({ product: p });
  },

  changeQty(e) {
    const { delta } = e.currentTarget.dataset;
    let qty = this.data.quantity + delta;
    if (qty < 1) qty = 1;
    this.setData({ quantity: qty });
  },

  async addCart() {
    const token = wx.getStorageSync("token");
    if (!token) return wx.navigateTo({ url: "/pages/mine/mine" });
    await api.addCart({ product_id: this.data.product.id, quantity: this.data.quantity });
    wx.showToast({ title: "已加入购物车", icon: "success" });
  },

  async buyNow() {
    const token = wx.getStorageSync("token");
    if (!token) return wx.navigateTo({ url: "/pages/mine/mine" });
    await api.addCart({ product_id: this.data.product.id, quantity: this.data.quantity });
    wx.switchTab({ url: "/pages/cart/cart" });
  },
});
