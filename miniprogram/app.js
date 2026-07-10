App({
  globalData: {
    userInfo: null,
    token: null,
  },
  onLaunch() {
    const token = wx.getStorageSync("token")
    if (token) this.globalData.token = token
  }
})
