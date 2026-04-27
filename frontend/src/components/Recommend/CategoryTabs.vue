<template>
  <div class="category-tabs">
    <div class="tabs-wrapper" ref="tabsRef">
      <div 
        v-for="tab in tabs" 
        :key="tab.id"
        class="tab-item"
        :class="{ active: currentTab === tab.id }"
        @click="handleTabClick(tab)"
      >
        <span class="tab-icon" v-if="tab.icon">
          <svg v-if="tab.id === 'recommend_for_you'" viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
          </svg>
          <svg v-else-if="tab.id === 'major_related'" viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z"/>
          </svg>
          <svg v-else-if="tab.id === 'hot_borrow'" viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M13.5.67s.74 2.65.74 4.8c0 2.06-1.35 3.73-3.41 3.73-2.07 0-3.63-1.67-3.63-3.73l.03-.36C5.21 7.51 4 10.62 4 14c0 4.42 3.58 8 8 8s8-3.58 8-8C20 8.61 17.41 3.8 13.5.67zM11.71 19c-1.78 0-3.22-1.4-3.22-3.14 0-1.62 1.05-2.76 2.81-3.12 1.77-.36 3.6-1.21 4.62-2.58.39 1.29.59 2.65.59 4.04 0 2.65-2.15 4.8-4.8 4.8z"/>
          </svg>
          <svg v-else-if="tab.id === 'new_books'" viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M17.63 5.84C17.27 5.33 16.67 5 16 5L5 5.01C3.9 5.01 3 5.9 3 7v10c0 1.1.9 1.99 2 1.99L16 19c.67 0 1.27-.33 1.63-.84L22 12l-4.37-6.16z"/>
          </svg>
          <span v-else>{{ tab.name.charAt(0) }}</span>
        </span>
        <span class="tab-name">{{ tab.name }}</span>
        <div class="tab-indicator" v-if="currentTab === tab.id"></div>
      </div>
      
      <!-- 自定义推荐按钮 -->
      <div 
        class="tab-item custom"
        @click="handleCustomClick"
      >
        <span class="tab-icon">+</span>
        <span class="tab-name">自定义</span>
      </div>
    </div>
    
    <!-- 自定义推荐输入弹窗 -->
    <div v-if="showCustomInput" class="custom-input-overlay" @click="closeCustomInput">
      <div class="custom-input-modal" @click.stop>
        <h3>自定义推荐</h3>
        <p>请输入你的推荐需求，例如"推荐考研政治冲刺资料"</p>
        <input 
          v-model="customQuery"
          type="text"
          placeholder="输入你的需求..."
          @keyup.enter="submitCustomQuery"
        />
        <div class="modal-actions">
          <button class="cancel-btn" @click="closeCustomInput">取消</button>
          <button class="submit-btn" @click="submitCustomQuery">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'CategoryTabs',
  props: {
    tabs: {
      type: Array,
      default: () => [
        { id: 'recommend_for_you', name: '为你推荐', icon: 'star' },
        { id: 'major_related', name: '专业相关', icon: 'book' },
        { id: 'hot_borrow', name: '热门借阅', icon: 'fire' },
        { id: 'new_books', name: '新书上架', icon: 'new' }
      ]
    },
    initialTab: {
      type: String,
      default: ''
    }
  },
  emits: ['tab-change', 'custom-query'],
  setup(props, { emit }) {
    const currentTab = ref(props.initialTab || props.tabs[0]?.id || '')
    const tabsRef = ref(null)
    const showCustomInput = ref(false)
    const customQuery = ref('')
    
    const handleTabClick = (tab) => {
      currentTab.value = tab.id
      emit('tab-change', tab)
    }
    
    const handleCustomClick = () => {
      showCustomInput.value = true
    }
    
    const closeCustomInput = () => {
      showCustomInput.value = false
      customQuery.value = ''
    }
    
    const submitCustomQuery = () => {
      if (!customQuery.value.trim()) return
      
      emit('custom-query', customQuery.value)
      closeCustomInput()
    }
    
    // 滚动到当前标签
    const scrollToCurrentTab = () => {
      if (!tabsRef.value) return
      
      const activeTab = tabsRef.value.querySelector('.tab-item.active')
      if (activeTab) {
        const container = tabsRef.value
        const offset = activeTab.offsetLeft - container.clientWidth / 2 + activeTab.clientWidth / 2
        container.scrollTo({ left: offset, behavior: 'smooth' })
      }
    }
    
    onMounted(() => {
      scrollToCurrentTab()
    })
    
    return {
      currentTab,
      tabsRef,
      showCustomInput,
      customQuery,
      handleTabClick,
      handleCustomClick,
      closeCustomInput,
      submitCustomQuery
    }
  }
}
</script>

<style scoped>
.category-tabs {
  background: white;
  position: sticky;
  top: 0;
  z-index: 100;
}

.tabs-wrapper {
  display: flex;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.tabs-wrapper::-webkit-scrollbar {
  display: none;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  position: relative;
  flex-shrink: 0;
}

.tab-item.active {
  color: #409eff;
}

.tab-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}

.tab-name {
  font-size: 14px;
  white-space: nowrap;
}

.tab-indicator {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 3px;
  background: #409eff;
  border-radius: 2px;
}

.tab-item.custom {
  color: #909399;
}

.tab-item.custom .tab-icon {
  font-size: 18px;
  font-weight: bold;
}

/* 自定义输入弹窗 */
.custom-input-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.custom-input-modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 80%;
  max-width: 400px;
}

.custom-input-modal h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #333;
}

.custom-input-modal p {
  margin: 0 0 16px;
  font-size: 14px;
  color: #999;
}

.custom-input-modal input {
  width: 100%;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
}

.custom-input-modal input:focus {
  border-color: #409eff;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}

.cancel-btn,
.submit-btn {
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
  border: none;
}

.submit-btn {
  background: #409eff;
  color: white;
  border: none;
}

.submit-btn:hover {
  background: #66b1ff;
}
</style>