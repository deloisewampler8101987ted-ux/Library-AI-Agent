// filepath: frontend/src/api/ai.js
/**
 * 对接后端千问流式响应接口
 */

import axios from 'axios'

// 创建 axios 实例
const aiApi = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000
})

// 请求拦截器
aiApi.interceptors.request.use(
  config => {
    // 可以添加认证 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
aiApi.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

/**
 * 发送消息（非流式）
 * @param {string} message - 用户消息
 * @param {string} userId - 用户ID
 * @param {string} sessionId - 会话ID
 */
export function sendMessage(message, userId = 'default_user', sessionId = null) {
  return aiApi.post('/v1/chat/send', {
    message,
    user_id: userId,
    session_id: sessionId
  })
}

/**
 * 发送消息（流式响应）
 * @param {string} message - 用户消息
 * @param {string} userId - 用户ID
 * @param {string} sessionId - 会话ID
 * @returns {EventSource} SSE 连接
 */
export function sendMessageStream(message, userId = 'default_user', sessionId = null) {
  return new Promise((resolve, reject) => {
    const url = `${aiApi.defaults.baseURL}/v1/chat/stream`
    const eventSource = new EventSource(`${url}?message=${encodeURIComponent(message)}&user_id=${userId}&session_id=${sessionId || ''}`)
    
    eventSource.onopen = () => {
      console.log('SSE 连接已建立')
    }
    
    eventSource.onmessage = (event) => {
      console.log('收到消息:', event.data)
    }
    
    eventSource.onerror = (error) => {
      console.error('SSE 错误:', error)
      eventSource.close()
      reject(error)
    }
    
    resolve(eventSource)
  })
}

/**
 * 流式聊天（使用 fetch API）
 * @param {string} message - 用户消息
 * @param {function} onMessage - 消息回调
 * @param {function} onComplete - 完成回调
 * @param {function} onError - 错误回调
 */
export async function chatStream(message, { onMessage, onComplete, onError }) {
  const url = `${aiApi.defaults.baseURL}/v1/chat/stream`
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message,
        user_id: 'default_user',
        use_stream: true
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    
    while (true) {
      const { done, value } = await reader.read()
      
      if (done) {
        break
      
      buffer += decoder.decode(value, { stream: true })
      
      // 处理 SSE 格式
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          
          if (data === '[DONE]') {
            onComplete?.()
            return
          }
          
          try {
            const parsed = JSON.parse(data)
            if (parsed.content) {
              onMessage?.(parsed.content)
            }
            if (parsed.error) {
              onError?.(parsed.error)
            }
          } catch (e) {
            // 非 JSON，直接输出
            if (data) {
              onMessage?.(data)
            }
          }
        }
      }
    }
  } catch (error) {
    onError?.(error)
  }
}

/**
 * 重新生成响应
 * @param {string} sessionId - 会话ID
 * @param {string} message - 原始消息
 */
export function regenerateResponse(sessionId, message) {
  return aiApi.post('/v1/chat/regenerate', {
    session_id: sessionId,
    message
  })
}

/**
 * 创建新会话
 * @param {string} userId - 用户ID
 */
export function createSession(userId = 'default_user') {
  return aiApi.post('/v1/chat/session/create', {
    user_id: userId
  })
}

/**
 * 获取会话历史
 * @param {string} sessionId - 会话ID
 */
export function getSessionHistory(sessionId) {
  return aiApi.get(`/v1/chat/history/${sessionId}`)
}

/**
 * 获取常见问题
 */
export function getFAQ() {
  return aiApi.get('/v1/chat/faq')
}

/**
 * 获取 FAQ 详情
 * @param {number} faqId - FAQ ID
 */
export function getFAQDetail(faqId) {
  return aiApi.get(`/v1/chat/faq/${faqId}`)
}

export default {
  sendMessage,
  sendMessageStream,
  chatStream,
  regenerateResponse,
  createSession,
  getSessionHistory,
  getFAQ,
  getFAQDetail
}