const api = require("../../utils/api");

Page({
  data: { products: [], category: "", page: 1, hasMore: true, categories: ["全部", "手机", "电脑", "耳机", "平板"] },

  onLoad() {
    this.loadProducts();
  },
  onShow() {
    if (this.data.page > 1) this.loadProducts(true);
  },

  async loadProducts(refresh = false) {
    if (refresh) this.setData({ page: 1, products: [], hasMore: true });
    const { page, category, products } = this.data;
    const cat = category === "全部" ? "" : category;
    const res = await api.getProducts(page, cat);
    this.setData({
      products: refresh ? res.items : [...products, ...res.items],
      hasMore: res.items.length === 20,
    });
  },

  selectCategory(e) {
    const cat = e.currentTarget.dataset.cat;
    this.setData({ category: cat, page: 1 }, () => this.loadProducts(true));
  },

  goProduct(e) {
    wx.navigateTo({ url: `/pages/product/product?id=${e.currentTarget.dataset.id}` });
  },
});
