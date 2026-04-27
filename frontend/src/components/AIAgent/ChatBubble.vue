<template>
  <div class="chat-bubble" :class="[role, { streaming: isStreaming }]">
    <div class="bubble-content">
      <div v-if="role === 'assistant'" class="avatar">
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
        </svg>
      </div>
      
      <div class="message-wrapper">
        <div class="message-text" v-html="formattedContent"></div>
        
        <!-- 重新生成按钮 -->
        <button
          v-if="role === 'assistant' && !isStreaming && showRegenerate"
          class="regenerate-btn"
          @click="handleRegenerate"
        >
          <svg viewBox="0 0 24 24" width="14" height="14">
            <path fill="currentColor" d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
          </svg>
          重新生成
        </button>
        
        <!-- 操作按钮 -->
        <div v-if="actions && actions.length > 0" class="bubble-actions">
          <button
            v-for="action in actions"
            :key="action.type"
            class="action-btn"
            :class="action.type"
            @click="handleAction(action)"
          >
            {{ action.label }}
          </button>
        </div>
      </div>
    </div>
    
    <div class="bubble-time">{{ formatTime(timestamp) }}</div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'ChatBubble',
  props: {
    role: {
      type: String,
      default: 'user', // user | assistant
      validator: v => ['user', 'assistant'].includes(v)
    },
    content: {
      type: String,
      default: ''
    },
    timestamp: {
      type: [Date, String],
      default: () => new Date()
    },
    showRegenerate: {
      type: Boolean,
      default: true
    },
    isStreaming: {
      type: Boolean,
      default: false
    },
    actions: {
      type: Array,
      default: () => []
    }
  },
  emits: ['regenerate', 'action'],
  setup(props, { emit }) {
    const displayContent = ref(props.content)
    
    // 实时更新内容（流式输出时）
    watch(() => props.content, (newVal) => {
      displayContent.value = newVal
    })
    
    const formattedContent = computed(() => {
      let text = displayContent.value
      
      // 换行处理
      text = text.replace(/\n/g, '<br>')
      
      // 图书链接高亮
      text = text.replace(/《([^》]+)》/g, 
        '<span class="book-title">《$1》</span>'
      )
      
      // 关键词高亮
      const keywords = ['预约', '借阅', '到期', '逾期', '推荐']
      keywords.forEach(kw => {
        const regex = new RegExp(`(${kw})`, 'g')
        text = text.replace(regex, '<span class="keyword">$1</span>')
      })
      
      return text
    })
    
    const formatTime = (time) => {
      const date = new Date(time)
      const hours = date.getHours().toString().padStart(2, '0')
      const minutes = date.getMinutes().toString().padStart(2, '0')
      return `${hours}:${minutes}`
    }
    
    const handleRegenerate = () => {
      emit('regenerate')
    }
    
    const handleAction = (action) => {
      emit('action', action)
    }
    
    return {
      displayContent,
      formattedContent,
      formatTime,
      handleRegenerate,
      handleAction
    }
  }
}
</script>

<style scoped>
.chat-bubble {
  display: flex;
  flex-direction: column;
  max-width: 80%;
  margin-bottom: 16px;
}

.chat-bubble.user {
  align-self: flex-end;
}

.chat-bubble.assistant {
  align-self: flex-start;
}

.bubble-content {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.user .bubble-content {
  flex-direction: row-reverse;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.message-wrapper {
  padding: 12px 16px;
  border-radius: 16px;
  position: relative;
}

.user .message-wrapper {
  background: #667eea;
  color: white;
  border-bottom-right-radius: 4px;
}

.assistant .message-wrapper {
  background: #f5f5f5;
  color: #333;
  border-bottom-left-radius: 4px;
}

.streaming .message-wrapper {
  background: #f0f7ff;
}

.message-text {
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.message-text :deep(.book-title) {
  color: #409eff;
  font-weight: 500;
}

.message-text :deep(.keyword) {
  color: #e6a23c;
  font-weight: 500;
}

.regenerate-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  padding: 4px 8px;
  background: transparent;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 12px;
  color: #909399;
  cursor: pointer;
  transition: all 0.2s;
}

.regenerate-btn:hover {
  color: #409eff;
  border-color: #409eff;
}

.bubble-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.action-btn {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.primary {
  background: #409eff;
  color: white;
  border: none;
}

.action-btn.default {
  background: white;
  color: #666;
  border: 1px solid #dcdfe6;
}

.bubble-time {
  font-size: 10px;
  color: #c0c4cc;
  margin-top: 4px;
}

.user .bubble-time {
  text-align: right;
}
</style>