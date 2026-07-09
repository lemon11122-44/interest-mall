App({
  globalData: {
    userInfo: null,
    token: null,
  },
  onLaunch() {
    const token = wx.getStorageSync("token");
    const userInfo = wx.getStorageSync("userInfo");
    if (token) this.globalData.token = token;
    if (userInfo) this.globalData.userInfo = userInfo;
  },
  setUser(token, userInfo) {
    this.globalData.token = token;
    this.globalData.userInfo = userInfo;
    wx.setStorageSync("token", token);
    wx.setStorageSync("userInfo", userInfo);
  },
  logout() {
    this.globalData.token = null;
    this.globalData.userInfo = null;
    wx.removeStorageSync("token");
    wx.removeStorageSync("userInfo");
  },
});
