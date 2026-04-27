<template>
  <div 
    class="voice-button" 
    :class="{ listening: isListening, pressed: isPressed }"
    @mousedown="handlePress"
    @mouseup="handleRelease"
    @mouseleave="handleRelease"
    @touchstart.prevent="handlePress"
    @touchend.prevent="handleRelease"
  >
    <div class="voice-icon">
      <svg v-if="!isListening" viewBox="0 0 24 24" width="28" height="28">
        <path fill="currentColor" d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
      </svg>
      <div v-else class="listening-animation">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
    
    <div v-if="isListening" class="listening-text">
      <span class="text">{{ listeningText }}</span>
    </div>
    
    <!-- 提示气泡 -->
    <div v-if="showHint" class="voice-hint">
      {{ hintText }}
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'VoiceButton',
  props: {
    hintText: {
      type: String,
      default: '长按说话，松开发送'
    },
    listeningText: {
      type: String,
      default: '正在聆听...'
    }
  },
  emits: ['voice-start', 'voice-end', 'voice-result'],
  setup(props, { emit }) {
    const isListening = ref(false)
    const isPressed = ref(false)
    const showHint = ref(false)
    const pressTimer = ref(null)
    
    const handlePress = () => {
      isPressed.value = true
      showHint.value = false
      
      // 延迟触发监听
      pressTimer.value = setTimeout(() => {
        isListening.value = true
        emit('voice-start')
        
        // 模拟语音识别（实际应调用 ASR API）
        startVoiceRecognition()
      }, 200)
    }
    
    const handleRelease = () => {
      isPressed.value = false
      clearTimeout(pressTimer.value)
      
      if (isListening.value) {
        isListening.value = false
        emit('voice-end')
      }
    }
    
    const startVoiceRecognition = () => {
      // 这里应该调用 ASR API
      // 模拟识别结果
      setTimeout(() => {
        // 模拟结果
        const mockResults = [
          '推荐计算机专业的书',
          '帮我查一下借阅状态',
          '图书馆开放时间',
          '搜索三体'
        ]
        const result = mockResults[Math.floor(Math.random() * mockResults.length)]
        emit('voice-result', result)
      }, 2000)
    }
    
    // 显示提示
    setTimeout(() => {
      showHint.value = true
      setTimeout(() => {
        showHint.value = false
      }, 3000)
    }, 1000)
    
    return {
      isListening,
      isPressed,
      showHint,
      hintText,
      listeningText,
      handlePress,
      handleRelease
    }
  }
}
</script>

<style scoped>
.voice-button {
  position: fixed;
  bottom: 80px;
  right: 20px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.voice-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: all 0.3s;
}

.voice-button.pressed .voice-icon {
  transform: scale(0.95);
}

.voice-button.listening .voice-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4); }
  50% { box-shadow: 0 4px 24px rgba(245, 87, 108, 0.6); }
}

.listening-animation {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
}

.listening-animation span {
  width: 4px;
  height: 16px;
  background: white;
  border-radius: 2px;
  animation: sound-wave 1s infinite ease-in-out;
}

.listening-animation span:nth-child(2) {
  animation-delay: 0.2s;
}

.listening-animation span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes sound-wave {
  0%, 100% { height: 8px; }
  50% { height: 20px; }
}

.listening-text {
  position: absolute;
  bottom: 70px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 12px;
  white-space: nowrap;
  animation: fade-in 0.3s;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateX(-50%) translateY(10px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}

.voice-hint {
  position: absolute;
  bottom: 70px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 11px;
  white-space: nowrap;
  animation: fade-in 0.3s;
}
</style>