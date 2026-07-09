const api = require("../../utils/api");

Page({
  data: { orders: [], statusTabs: ["全部", "pending", "paid", "shipped", "completed", "cancelled"], activeTab: "全部", address: "", phone: "", remark: "" },

  onShow() { this.loadOrders(); },

  async loadOrders() {
    const res = await api.getOrders();
    this.setData({ orders: res.items });
  },

  selectTab(e) {
    const tab = e.currentTarget.dataset.tab;
    this.setData({ activeTab: tab });
  },

  get filteredOrders() {
    if (this.data.activeTab === "全部") return this.data.orders;
    return this.data.orders.filter((o) => o.status === this.data.activeTab);
  },

  async payOrder(e) {
    await api.payOrder(e.currentTarget.dataset.id);
    wx.showToast({ title: "支付成功", icon: "success" });
    this.loadOrders();
  },

  async cancelOrder(e) {
    wx.showModal({ title: "提示", content: "确定取消订单？", success: async (r) => {
      if (r.confirm) { await api.cancelOrder(e.currentTarget.dataset.id); this.loadOrders(); }
    }});
  },

  getStatusText(status) {
    const map = { pending: "待付款", paid: "待发货", shipped: "已发货", completed: "已完成", cancelled: "已取消" };
    return map[status] || status;
  },
});
