// 云函数：api
// 接收小程序请求，转发到云托管后端
const https = require('https')
const http = require('http')

exports.main = async (event) => {
  const { method = 'GET', path, data, token } = event
  const API_BASE = 'https://lemon1-280065-9-1452195104.sh.run.tcloudbase.com'

  const url = new URL(API_BASE + path)
  const options = {
    hostname: url.hostname,
    port: 443,
    path: url.pathname + url.search,
    method,
    headers: { 'Content-Type': 'application/json' },
    rejectUnauthorized: false,
  }
  if (token) options.headers['Authorization'] = `Bearer ${token}`

  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let body = ''
      res.on('data', (chunk) => (body += chunk))
      res.on('end', () => {
        try {
          const result = JSON.parse(body)
          // 如果后端返回了 status_code 错误，包装一下
          if (res.statusCode >= 400) {
            resolve({ code: res.statusCode, error: result.detail || '请求失败' })
          } else {
            resolve({ code: 0, data: result })
          }
        } catch {
          resolve({ code: res.statusCode, data: body })
        }
      })
    })
    req.on('error', (e) => reject({ code: -1, error: e.message }))
    if (data && method !== 'GET') req.write(JSON.stringify(data))
    req.end()
  })
}
