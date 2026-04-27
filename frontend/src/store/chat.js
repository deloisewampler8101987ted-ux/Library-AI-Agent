// filepath: frontend/src/store/chat.js
/**
 * 管理多轮对话上下文与历史记录
 */

import { createStore } from 'vuex'
import { chatStream, createSession, getSessionHistory } from '../api/ai'

export default createStore({
  state: {
    // 当前会话
    currentSession: null,
    
    // 会话历史列表
    sessions: [],
    
    // 当前会话的消息列表
    messages: [],
    
    // 是否正在加载
    isLoading: false,
    
    // 是否正在流式输出
    isStreaming: false,
    
    // 用户画像
    userProfile: {
      major: '计算机',
      grade: '大一',
      interests: ['技术', '科幻'],
      read_books: []
    },
    
    // AI 配置
    aiConfig: {
      temperature: 0.7,
      maxTokens: 2000,
      stream: true
    }
  },
  
  mutations: {
    // 设置当前会话
    SET_CURRENT_SESSION(state, session) {
      state.currentSession = session
    },
    
    // 设置会话列表
    SET_SESSIONS(state, sessions) {
      state.sessions = sessions
    },
    
    // 添加消息
    ADD_MESSAGE(state, message) {
      state.messages.push({
        ...message,
        timestamp: message.timestamp || new Date()
      })
    },
    
    // 更新最后一条消息
    UPDATE_LAST_MESSAGE(state, content) {
      if (state.messages.length > 0) {
        const lastMsg = state.messages[state.messages.length - 1]
        if (lastMsg.role === 'assistant') {
          lastMsg.content += content
        }
      }
    },
    
    // 设置消息列表
    SET_MESSAGES(state, messages) {
      state.messages = messages
    },
    
    // 清除消息
    CLEAR_MESSAGES(state) {
      state.messages = []
    },
    
    // 设置加载状态
    SET_LOADING(state, isLoading) {
      state.isLoading = isLoading
    },
    
    // 设置流式输出状态
    SET_STREAMING(state, isStreaming) {
      state.isStreaming = isStreaming
    },
    
    // 更新用户画像
    UPDATE_USER_PROFILE(state, profile) {
      state.userProfile = {
        ...state.userProfile,
        ...profile
      }
    },
    
    // 添加已读图书
    ADD_READ_BOOK(state, bookId) {
      if (!state.userProfile.read_books.includes(bookId)) {
        state.userProfile.read_books.push(bookId)
      }
    },
    
    // 添加兴趣
    ADD_INTEREST(state, interest) {
      if (!state.userProfile.interests.includes(interest)) {
        state.userProfile.interests.push(interest)
      }
    }
  },
  
  actions: {
    // 创建新会话
    async createNewSession({ commit }, userId = 'default_user') {
      commit('SET_LOADING', true)
      try {
        const res = await createSession(userId)
        if (res.success) {
          const session = res.data
          commit('SET_CURRENT_SESSION', session)
          commit('SET_MESSAGES', [])
          return session
        }
      } catch (e) {
        console.error('创建会话失败:', e)
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 发送消息
    async sendMessage({ commit, state }, message) {
      // 添加用户消息
      commit('ADD_MESSAGE', {
        role: 'user',
        content: message
      })
      
      // 添加 AI 消息占位
      commit('ADD_MESSAGE', {
        role: 'assistant',
        content: '',
        isStreaming: true
      })
      
      commit('SET_STREAMING', true)
      
      try {
        await chatStream(message, {
          onMessage: (chunk) => {
            commit('UPDATE_LAST_MESSAGE', chunk)
          },
          onComplete: () => {
            commit('SET_STREAMING', false)
            // 标记最后消息为非流式
            if (state.messages.length > 0) {
              const lastMsg = state.messages[state.messages.length - 1]
              if (lastMsg) {
                lastMsg.isStreaming = false
              }
            }
          },
          onError: (error) => {
            console.error('聊天错误:', error)
            commit('SET_STREAMING', false)
            // 更新最后消息为错误信息
            if (state.messages.length > 0) {
              const lastMsg = state.messages[state.messages.length - 1]
              if (lastMsg) {
                lastMsg.content = '抱歉，服务暂时不可用，请稍后重试。'
                lastMsg.isStreaming = false
              }
            }
          }
        })
      } catch (e) {
        console.error('发送消息失败:', e)
        commit('SET_STREAMING', false)
      }
    },
    
    // 重新生成
    async regenerateResponse({ dispatch, state }, messageIndex) {
      // 找到对应的用户消息
      const msg = state.messages[messageIndex]
      if (!msg || msg.role !== 'assistant') return
      
      // 找到对应的用户消息
      let userMessage = null
      for (let i = messageIndex - 1; i >= 0; i--) {
        if (state.messages[i].role === 'user') {
          userMessage = state.messages[i].content
          break
        }
      }
      
      if (!userMessage) return
      
      // 清除当前 AI 消息
      state.messages.splice(messageIndex)
      
      // 重新发送
      await dispatch('sendMessage', userMessage)
    },
    
    // 加载会话历史
    async loadSessionHistory({ commit }, sessionId) {
      commit('SET_LOADING', true)
      try {
        const res = await getSessionHistory(sessionId)
        if (res.success) {
          commit('SET_MESSAGES', res.data.messages)
        }
      } catch (e) {
        console.error('加载会话历史失败:', e)
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 清除当前会话
    clearCurrentSession({ commit }) {
      commit('SET_CURRENT_SESSION', null)
      commit('SET_MESSAGES', [])
    },
    
    // 更新用户画像
    updateUserProfile({ commit }, profile) {
      commit('UPDATE_USER_PROFILE', profile)
    }
  },
  
  getters: {
    // 获取当前会话ID
    currentSessionId: state => state.currentSession?.session_id,
    
    // 获取当前消息列表
    currentMessages: state => state.messages,
    
    // 获取用户画像
    userProfile: state => state.userProfile,
    
    // 是否正在聊天
    isChatting: state => state.isLoading || state.isStreaming,
    
    // 获取最后一条 AI 消息
    lastAssistantMessage: state => {
      for (let i = state.messages.length - 1; i >= 0; i--) {
        if (state.messages[i].role === 'assistant') {
          return state.messages[i]
        }
      }
      return null
    },
    
    // 获取消息数量
    messageCount: state => state.messages.length,
    
    // 获取用户消息数量
    userMessageCount: state => {
      return state.messages.filter(m => m.role === 'user').length
    }
  }
})