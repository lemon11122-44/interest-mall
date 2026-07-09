const api = require("../../utils/api");

Page({
  data: { items: [], total: 0, isEmpty: true },

  onShow() {
    this.loadCart();
  },

  async loadCart() {
    try {
      const res = await api.getCart();
      this.setData({ items: res.items, total: res.total_amount, isEmpty: res.items.length === 0 });
    } catch {
      this.setData({ items: [], total: 0, isEmpty: true });
    }
  },

  async changeQty(e) {
    const { id, delta } = e.currentTarget.dataset;
    const item = this.data.items.find((i) => i.id === id);
    const qty = item.quantity + delta;
    if (qty <= 0) return this.removeItem(id);
    await api.updateCart(id, { quantity: qty });
    this.loadCart();
  },

  async removeItem(e) {
    const id = typeof e === "number" ? e : e.currentTarget.dataset.id;
    await api.removeCart(id);
    this.loadCart();
  },

  async clearCart() {
    wx.showModal({ title: "提示", content: "确定清空购物车？", success: async (r) => {
      if (r.confirm) { await api.clearCart(); this.loadCart(); }
    }});
  },

  goOrder() {
    if (this.data.isEmpty) return wx.showToast({ title: "购物车为空", icon: "none" });
    wx.navigateTo({ url: "/pages/order/order" });
  },
});
