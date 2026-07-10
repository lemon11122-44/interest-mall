// index.js - 首页
Page({
  data: {
    date: '2026年7月11日',
    lpr: { year1: '3.0', year5: '3.5', loanLimit: '12' },
    tools: [
      [
        { id: 'debx', icon: '月', color: '#1677FF', name: '等额月供', bg: '#1677FF' },
        { id: 'debj', icon: '本', color: '#1677FF', name: '等额本金', bg: '#1677FF' },
        { id: 'xxhb', icon: '息', color: '#FF9922', name: '先息后本', bg: '#FF9922' },
        { id: 'arjs', icon: '日', color: '#FF9922', name: '按日计息', bg: '#FF9922' }
      ],
      [
        { id: 'dqlc', icon: '定', color: '#00BB77', name: '定期理财', bg: '#00BB77' },
        { id: 'fljs', icon: '复', color: '#00BB77', name: '复利计算', bg: '#00BB77' },
        { id: 'llzh', icon: '转', color: '#9966EE', name: '利率转换', bg: '#9966EE' },
        { id: 'qrnh', icon: '七', color: '#9966EE', name: '七日年化', bg: '#9966EE' }
      ]
    ],
    banners: [
      {
        title: 'LPR是什么？',
        subtitle: '贷款市场报价利率如何影响你的房贷月供',
        bg: '#FF44BB'
      }
    ],
    currentBanner: 0
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
  }
})
