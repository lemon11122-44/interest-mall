const api = require("../../utils/api");

Page({
  data: { tab: "stats", stats: {}, products: [], orders: [], users: [], orderStatus: "" },

  onShow() { this.loadStats(); },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab;
    this.setData({ tab });
    if (tab === "products") this.loadProducts();
    if (tab === "orders") this.loadOrders();
    if (tab === "stats") this.loadStats();
  },

  async loadStats() {
    const stats = await api.adminStats();
    this.setData({ stats });
  },

  async loadProducts() {
    const res = await api.adminProducts();
    this.setData({ products: res.items });
  },

  async loadOrders() {
    const res = await api.adminOrders(this.data.orderStatus);
    this.setData({ orders: res.items });
  },

  selectOrderStatus(e) {
    this.setData({ orderStatus: e.currentTarget.dataset.status }, () => this.loadOrders());
  },

  async updateStatus(e) {
    const { id, status } = e.currentTarget.dataset;
    await api.updateOrderStatus(id, status);
    wx.showToast({ title: "更新成功", icon: "success" });
    this.loadOrders();
  },

  getStatusText(status) {
    const m = { pending: "待付款", paid: "待发货", shipped: "已发货", completed: "已完成", cancelled: "已取消" };
    return m[status] || status;
  },
});
