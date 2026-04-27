<template>
  <div class="search-bar">
    <div class="search-input-wrapper">
      <input
        v-model="searchText"
        type="text"
        class="search-input"
        :placeholder="placeholder"
        @keyup.enter="handleSearch"
        @focus="showHistory = true"
        @blur="hideHistory"
      />
      <div class="search-actions">
        <span v-if="isListening" class="listening-indicator">
          <span class="pulse"></span>
          正在聆听...
        </span>
        <button
          v-if="searchText"
          class="clear-btn"
          @click="clearSearch"
        >
          ×
        </button>
        <button
          class="voice-btn"
          :class="{ active: isListening }"
          @mousedown="startVoiceInput"
          @mouseup="stopVoiceInput"
          @mouseleave="stopVoiceInput"
        >
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
          </svg>
        </button>
      </div>
    </div>
    
    <!-- 搜索历史 -->
    <div v-if="showHistory && searchHistory.length > 0" class="search-history">
      <div class="history-header">
        <span>最近搜索</span>
        <span class="clear-history" @click="clearHistory">清除</span>
      </div>
      <div
        v-for="(item, index) in searchHistory"
        :key="index"
        class="history-item"
        @click="selectHistory(item)"
      >
        {{ item }}
      </div>
    </div>
    
    <!-- 搜索建议 -->
    <div v-if="showSuggestions && suggestions.length > 0" class="search-suggestions">
      <div
        v-for="(suggestion, index) in suggestions"
        :key="index"
        class="suggestion-item"
        @click="selectSuggestion(suggestion)"
      >
        {{ suggestion }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'SearchBar',
  props: {
    placeholder: {
      type: String,
      default: '想问 AI 图书管理员什么？比如推荐图书、查借阅状态'
    },
    initialValue: {
      type: String,
      default: ''
    }
  },
  emits: ['search', 'voice-input'],
  setup(props, { emit }) {
    const searchText = ref(props.initialValue)
    const isListening = ref(false)
    const showHistory = ref(false)
    const showSuggestions = ref(false)
    const searchHistory = ref([])
    const suggestions = ref([])
    
    // 模拟建议数据
    const mockSuggestions = [
      '推荐计算机专业图书',
      '搜索三体',
      '我的借阅状态',
      '图书馆开放时间',
      '推荐科幻小说',
      '如何预约图书'
    ]
    
    watch(searchText, (val) => {
      if (val.length > 0) {
        // 简单过滤建议
        suggestions.value = mockSuggestions.filter(s => 
          s.includes(val)
        ).slice(0, 5)
        showSuggestions.value = suggestions.value.length > 0
      } else {
        showSuggestions.value = false
      }
    })
    
    const handleSearch = () => {
      if (!searchText.value.trim()) return
      
      // 保存搜索历史
      const history = searchHistory.value
      const index = history.indexOf(searchText.value)
      if (index > -1) {
        history.splice(index, 1)
      }
      history.unshift(searchText.value)
      if (history.length > 10) {
        history.pop()
      }
      searchHistory.value = history
      localStorage.setItem('searchHistory', JSON.stringify(history))
      
      emit('search', searchText.value)
      showSuggestions.value = false
    }
    
    const clearSearch = () => {
      searchText.value = ''
      emit('search', '')
    }
    
    const startVoiceInput = () => {
      isListening.value = true
      emit('voice-input', true)
      // 模拟语音识别结果
      setTimeout(() => {
        // 这里应该调用 ASR API
        // 模拟结果
      }, 2000)
    }
    
    const stopVoiceInput = () => {
      isListening.value = false
      emit('voice-input', false)
    }
    
    const selectHistory = (item) => {
      searchText.value = item
      handleSearch()
      showHistory.value = false
    }
    
    const selectSuggestion = (suggestion) => {
      searchText.value = suggestion
      handleSearch()
    }
    
    const clearHistory = () => {
      searchHistory.value = []
      localStorage.removeItem('searchHistory')
    }
    
    const hideHistory = () => {
      setTimeout(() => {
        showHistory.value = false
      }, 200)
    }
    
    // 加载历史记录
    const savedHistory = localStorage.getItem('searchHistory')
    if (savedHistory) {
      try {
        searchHistory.value = JSON.parse(savedHistory)
      } catch (e) {
        console.error('加载搜索历史失败:', e)
      }
    }
    
    return {
      searchText,
      isListening,
      showHistory,
      showSuggestions,
      searchHistory,
      suggestions,
      handleSearch,
      clearSearch,
      startVoiceInput,
      stopVoiceInput,
      selectHistory,
      selectSuggestion,
      clearHistory,
      hideHistory
    }
  }
}
</script>

<style scoped>
.search-bar {
  position: relative;
  width: 100%;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 24px;
  padding: 8px 16px;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  outline: none;
}

.search-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.listening-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #409eff;
  font-size: 12px;
}

.pulse {
  width: 8px;
  height: 8px;
  background: #409eff;
  border-radius: 50%;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.clear-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: #999;
  cursor: pointer;
  padding: 4px;
}

.voice-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
  padding: 4px;
  transition: color 0.3s;
}

.voice-btn.active {
  color: #409eff;
}

.search-history,
.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-top: 8px;
  z-index: 100;
  max-height: 300px;
  overflow-y: auto;
}

.history-header {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 12px;
  color: #999;
}

.clear-history {
  color: #409eff;
  cursor: pointer;
}

.history-item,
.suggestion-item {
  padding: 12px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.history-item:hover,
.suggestion-item:hover {
  background: #f5f5f5;
}
</style>