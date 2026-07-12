const CONFIG = require("../../utils/config")
const API_BASE = CONFIG.API_BASE

Page({
  data: {
    tools: [
      [
        { id: 'debx', icon: '月', color: '#1677FF', name: '等额本息测算', bg: '#1677FF' },
        { id: 'debj', icon: '本', color: '#1677FF', name: '等额本金测算', bg: '#1677FF' },
        { id: 'xxhb', icon: '息', color: '#FF9922', name: '先息后本测算', bg: '#FF9922' },
        { id: 'arjs', icon: '日', color: '#FF9922', name: '按日计息测算', bg: '#FF9922' }
      ],
      [
        { id: 'ktx', icon: '砍', color: '#00BB77', name: '砍头息IRR测算', bg: '#00BB77' },
        { id: 'fljs', icon: '复', color: '#00BB77', name: '复利利率换算', bg: '#00BB77' },
        { id: 'llzh', icon: '转', color: '#9966EE', name: '名义/真实利率转换', bg: '#9966EE' },
        { id: 'mjdk', icon: '上', color: '#9966EE', name: '民间借贷利率上限', bg: '#9966EE' }
      ]
    ],
    // 轮播默认文本（后台可覆盖）
    banner: {
      title: '真实年化IRR怎么算？',
      subtitle: '网贷隐藏担保费、会员费全部计入真实成本',
      more: '查看测算教程 →'
    },
    kf_wechat: '',
    kf_qrcode: '',
    currentBanner: 0
  },

  onLoad() {
    this.loadSettings()
  },

  loadSettings() {
    wx.request({
      url: API_BASE + '/api/admin/settings',
      success: (res) => {
        if (res.statusCode === 200) {
          const s = res.data
          const update = {}
          if (s.home_title) update['banner.title'] = s.home_title
          if (s.home_subtitle) update['banner.subtitle'] = s.home_subtitle
          if (s.home_desc) update['banner.more'] = s.home_desc
          if (s.kf_wechat) update.kf_wechat = s.kf_wechat
          if (s.kf_qrcode) update.kf_qrcode = s.kf_qrcode
          if (Object.keys(update).length > 0) this.setData(update)
        }
      }
    })
  },

  onToolTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/tool/${id}/${id}` })
  },

  onBannerChange(e) {
    this.setData({ currentBanner: e.detail.current })
  },

  onBannerTap() {
    wx.navigateTo({ url: '/pages/knowledge/knowledge' })
  },

  onKfTap() {
    const wechat = this.data.kf_wechat
    if (wechat) {
      wx.setClipboardData({
        data: wechat,
        success: () => wx.showToast({ title: '微信号已复制', icon: 'success' })
      })
    } else {
      wx.showToast({ title: '暂未设置客服', icon: 'none' })
    }
  }
})
