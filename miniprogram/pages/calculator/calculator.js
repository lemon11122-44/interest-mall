const api = require("../../utils/api");

Page({
  data: {
    mode: 1,
    principal: "", annual_rate: "", months: "", total_repayment: "",
    repayment_method: "debx",
    result: null,
    methodLabels: { debx: "等额本息", debj: "等额本金" },
  },

  switchMode(e) {
    this.setData({ mode: parseInt(e.currentTarget.dataset.mode), result: null });
  },

  onInput(e) {
    this.setData({ [e.currentTarget.dataset.field]: e.detail.value });
  },

  selectMethod(e) {
    this.setData({ repayment_method: e.currentTarget.dataset.val, result: null });
  },

  async calculate() {
    const { mode, principal, annual_rate, months, total_repayment, repayment_method } = this.data;
    if (!principal || !months) return wx.showToast({ title: "请填写完整信息", icon: "none" });

    try {
      let res;
      if (mode === 1) {
        if (!annual_rate) return wx.showToast({ title: "请输入年利率", icon: "none" });
        res = await api.calcMode1({
          principal: parseFloat(principal),
          annual_rate: parseFloat(annual_rate),
          months: parseInt(months),
          repayment_method,
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

  getMethodText(m) {
    return this.data.methodLabels[m] || m;
  },
});
