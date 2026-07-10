const api = require("../../utils/api");

Page({
  data: {
    fees: [],
    stats: null,
    showForm: false,
    editId: null,
    // 表单
    platform: "",
    description: "",
    amount: "",
    cycle: "monthly",
    category: "其他",
    next_date: "",
    cycleOptions: ["monthly", "quarterly", "yearly", "one_time"],
    cycleLabels: { monthly: "每月", quarterly: "每季度", yearly: "每年", one_time: "一次性" },
    categoryOptions: ["视频", "音乐", "云存储", "工具", "生活", "游戏", "学习", "其他"],
  },

  onShow() {
    this.loadData();
  },

  async loadData() {
    try {
      const [fees, stats] = await Promise.all([api.getFees(), api.getFeeStats()]);
      this.setData({ fees, stats });
    } catch {}
  },

  showAddForm() {
    this.setData({
      showForm: true, editId: null,
      platform: "", description: "", amount: "", cycle: "monthly",
      category: "其他", next_date: "",
    });
  },

  showEditForm(e) {
    const fee = e.currentTarget.dataset.fee;
    this.setData({
      showForm: true, editId: fee.id,
      platform: fee.platform, description: fee.description,
      amount: String(fee.amount), cycle: fee.cycle,
      category: fee.category, next_date: fee.next_date || "",
    });
  },

  hideForm() {
    this.setData({ showForm: false });
  },

  onInput(e) {
    this.setData({ [e.currentTarget.dataset.field]: e.detail.value });
  },

  selectCycle(e) {
    this.setData({ cycle: e.currentTarget.dataset.val });
  },

  selectCategory(e) {
    this.setData({ category: e.currentTarget.dataset.val });
  },

  async saveFee() {
    const { editId, platform, amount, cycle, category, description, next_date } = this.data;
    if (!platform || !amount) return wx.showToast({ title: "请填写平台和金额", icon: "none" });

    const data = {
      platform, description, cycle, category,
      amount: parseFloat(amount),
      next_date: next_date || undefined,
    };

    try {
      if (editId) {
        await api.updateFee(editId, data);
      } else {
        await api.createFee(data);
      }
      this.hideForm();
      this.loadData();
      wx.showToast({ title: editId ? "已更新" : "已添加", icon: "success" });
    } catch {}
  },

  async deleteFee(e) {
    const id = e.currentTarget.dataset.id;
    wx.showModal({
      title: "确认删除", content: "确定要删除这条扣费记录吗？",
      success: async (r) => {
        if (r.confirm) {
          await api.deleteFee(id);
          this.loadData();
          wx.showToast({ title: "已删除", icon: "success" });
        }
      },
    });
  },

  getCycleText(cycle) {
    return this.data.cycleLabels[cycle] || cycle;
  },

  formatDate(d) {
    if (!d) return "未设置";
    return d.slice(0, 10);
  },
});
