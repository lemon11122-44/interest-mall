// 云函数：api-proxy
// 作为代理转发请求到云托管后端
const cloud = require('wx-server-sdk')
cloud.init()

// 后端地址
const API_BASE = 'https://lemon1-280065-9-1452195104.sh.run.tcloudbase.com'

exports.main = async (event, context) => {
  const { path, method = 'GET', data = {} } = event

  const url = API_BASE + path
  const header = { 'Content-Type': 'application/json' }
  if (event.token) header['Authorization'] = `Bearer ${event.token}`

  try {
    const res = await cloud.callFunction({
      name: 'cloudbase_module',
      data: {
        http: {
          url,
          method,
          headers: header,
          body: method === 'GET' ? undefined : JSON.stringify(data),
        }
      }
    })
    return res
  } catch (e) {
    // fallback: direct HTTP request via cloud
    const result = await new Promise((resolve, reject) => {
      const https = require('https')
      const parsed = new URL(url)
      const options = {
        hostname: parsed.hostname,
        port: 443,
        path: parsed.pathname + parsed.search,
        method,
        headers: header,
      }
      const req = https.request(options, (res) => {
        let body = ''
        res.on('data', (chunk) => body += chunk)
        res.on('end', () => {
          try { resolve(JSON.parse(body)) }
          catch { resolve(body) }
        })
      })
      req.on('error', reject)
      if (data && method !== 'GET') req.write(JSON.stringify(data))
      req.end()
    })
    return result
  }
}
