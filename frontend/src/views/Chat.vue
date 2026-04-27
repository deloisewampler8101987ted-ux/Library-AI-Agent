<template>
  <div class="chat-page">
    <!-- 顶部导航 -->
    <div class="chat-header">
      <div class="back-btn" @click="goBack">
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
        </svg>
      </div>
      <h1>AI 图书管理员</h1>
      <div class="header-actions">
        <button class="icon-btn" @click="clearChat">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
          </svg>
        </button>
      </div>
    </div>
    
    <!-- 聊天内容区 -->
    <div class="chat-content" ref="chatContentRef">
      <div class="welcome-message" v-if="messages.length === 0">
        <div class="ai-avatar">
          <svg viewBox="0 0 24 24" width="48" height="48">
            <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
          </svg>
        </div>
        <h2>你好，我是图书馆 AI 管理员</h2>
        <p>我可以帮你：</p>
        <ul>
          <li>📚 推荐图书</li>
          <li>🔍 搜索查找</li>
          <li>📖 查询借阅状态</li>
          <li>❓ 解答图书馆相关问题</li>
        </ul>
        <p class="hint">请在下方输入你的问题</p>
      </div>
      
      <div v-else class="message-list">
        <ChatBubble
          v-for="(msg, index) in messages"
          :key="index"
          :role="msg.role"
          :content="msg.content"
          :timestamp="msg.timestamp"
          :show-regenerate="msg.role === 'assistant' && !msg.isStreaming"
          :is-streaming="msg.isStreaming"
          @regenerate="handleRegenerate(index)"
        />
        
        <!-- 正在输入提示 -->
        <div v-if="isTyping" class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
    
    <!-- 输入区域 -->
    <div class="chat-input-area">
      <div class="input-wrapper">
        <input
          v-model="inputMessage"
          type="text"
          placeholder="想问 AI 图书管理员什么？"
          @keyup.enter="sendMessage"
          :disabled="isTyping"
        />
        <button 
          class="send-btn"
          :class="{ active: inputMessage.trim() }"
          @click="sendMessage"
          :disabled="!inputMessage.trim() || isTyping"
        >
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, watch } from 'vue'
import ChatBubble from '../components/AIAgent/ChatBubble.vue'
import { sendMessage, chatStream, createSession } from '../api/ai'

export default {
  name: 'ChatPage',
  components: {
    ChatBubble
  },
  setup() {
    const messages = ref([])
    const inputMessage = ref('')
    const isTyping = ref(false)
    const chatContentRef = ref(null)
    const sessionId = ref(null)
    
    // 初始化会话
    const initSession = async () => {
      try {
        const res = await createSession()
        if (res.success) {
          sessionId.value = res.data.session_id
        }
      } catch (e) {
        console.error('创建会话失败:', e)
      }
    }
    
    // 发送消息
    const sendMessage = async () => {
      if (!inputMessage.value.trim() || isTyping.value) return
      
      const userMessage = inputMessage.value.trim()
      inputMessage.value = ''
      
      // 添加用户消息
      messages.value.push({
        role: 'user',
        content: userMessage,
        timestamp: new Date()
      })
      
      // 滚动到底部
      await nextTick()
      scrollToBottom()
      
      // 添加 AI 消息占位
      const aiMessage = {
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true
      }
      messages.value.push(aiMessage)
      
      isTyping.value = true
      
      try {
        // 流式调用
        await chatStream(userMessage, {
          onMessage: (chunk) => {
            const lastMsg = messages.value[messages.value.length - 1]
            if (lastMsg.role === 'assistant') {
              lastMsg.content += chunk
            }
          },
          onComplete: () => {
            const lastMsg = messages.value[messages.value.length - 1]
            if (lastMsg) {
              lastMsg.isStreaming = false
            }
            isTyping.value = false
            nextTick(() => scrollToBottom())
          },
          onError: (error) => {
            console.error('聊天错误:', error)
            const lastMsg = messages.value[messages.value.length - 1]
            if (lastMsg) {
              lastMsg.content = '抱歉，服务暂时不可用，请稍后重试。'
              lastMsg.isStreaming = false
            }
            isTyping.value = false
          }
        })
      } catch (e) {
        console.error('发送消息失败:', e)
        isTyping.value = false
      }
    }
    
    // 重新生成
    const handleRegenerate = async (index) => {
      const msg = messages.value[index]
      if (msg.role !== 'assistant') return
      
      // 找到对应的用户消息
      let userMsg = null
      for (let i = index - 1; i >= 0; i--) {
        if (messages.value[i].role === 'user') {
          userMsg = messages.value[i]
          break
        }
      }
      
      if (!userMsg) return
      
      // 重新发送
      msg.content = ''
      msg.isStreaming = true
      isTyping.value = true
      
      try {
        await chatStream(userMsg.content, {
          onMessage: (chunk) => {
            msg.content += chunk
          },
          onComplete: () => {
            msg.isStreaming = false
            isTyping.value = false
          },
          onError: (error) => {
            msg.content = '抱歉，重新生成失败。'
            msg.isStreaming = false
            isTyping.value = false
          }
        })
      } catch (e) {
        console.error('重新生成失败:', e)
        isTyping.value = false
      }
    }
    
    // 滚动到底部
    const scrollToBottom = () => {
      if (chatContentRef.value) {
        chatContentRef.value.scrollTop = chatContentRef.value.scrollHeight
      }
    }
    
    // 清除聊天
    const clearChat = () => {
      messages.value = []
    }
    
    // 返回
    const goBack = () => {
      console.log('返回上一页')
    }
    
    onMounted(() => {
      initSession()
    })
    
    return {
      messages,
      inputMessage,
      isTyping,
      chatContentRef,
      sendMessage,
      handleRegenerate,
      clearChat,
      goBack
    }
  }
}
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.back-btn,
.header-actions .icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
  padding: 4px;
}

.chat-header h1 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.welcome-message {
  text-align: center;
  padding: 40px 20px;
}

.ai-avatar {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.welcome-message h2 {
  font-size: 20px;
  color: #333;
  margin: 0 0 16px;
}

.welcome-message p {
  font-size: 14px;
  color: #666;
  margin: 0 0 8px;
}

.welcome-message ul {
  list-style: none;
  padding: 0;
  margin: 16px 0;
  text-align: left;
  display: inline-block;
}

.welcome-message li {
  font-size: 14px;
  color: #666;
  margin: 8px 0;
}

.welcome-message .hint {
  color: #999;
  font-size: 12px;
  margin-top: 20px;
}

.message-list {
  display: flex;
  flex-direction: column;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: #f5f5f5;
  border-radius: 16px;
  width: fit-content;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #999;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-4px); }
}

.chat-input-area {
  background: white;
  padding: 12px 16px;
  box-shadow: 0 -1px 4px rgba(0, 0, 0, 0.05);
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 24px;
  padding: 8px 12px;
}

.input-wrapper input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  outline: none;
}

.send-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e6e6e6;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all 0.2s;
}

.send-btn.active {
  background: #409eff;
}

.send-btn:disabled {
  cursor: not-allowed;
}
</style>