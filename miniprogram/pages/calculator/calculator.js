const api = require("../../utils/api");

Page({
  data: { mode: 1, principal: "", annual_rate: "", months: "", total_repayment: "", result: null },

  switchMode(e) {
    this.setData({ mode: parseInt(e.currentTarget.dataset.mode), result: null });
  },

  onInput(e) {
    this.setData({ [e.currentTarget.dataset.field]: e.detail.value });
  },

  async calculate() {
    const { mode, principal, annual_rate, months, total_repayment } = this.data;
    if (!principal || !months) return wx.showToast({ title: "请填写完整信息", icon: "none" });

    try {
      let res;
      if (mode === 1) {
        if (!annual_rate) return wx.showToast({ title: "请输入年利率", icon: "none" });
        res = await api.calcMode1({
          principal: parseFloat(principal),
          annual_rate: parseFloat(annual_rate),
          months: parseInt(months),
        });
      } else {
        if (!total_repayment) return wx.showToast({ title: "请输入总还款额", icon: "none" });
        res = await api.calcMode2({
          principal: parseFloat(principal),
          total_repayment: parseFloat(total_repayment),
          months: parseInt(months),
        });
      }
      this.setData({ result: res });
    } catch (e) {
      console.error(e);
    }
  },
});
