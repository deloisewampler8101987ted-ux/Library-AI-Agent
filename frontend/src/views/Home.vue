<template>
  <div class="home-page">
    <!-- 顶部智能交互区 -->
    <div class="top-section">
      <SearchBar 
        @search="handleSearch"
        @voice-input="handleVoiceInput"
      />
      
      <div class="top-actions">
        <div class="borrow-status" @click="goToProfile">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9h-4v4h-2v-4H9V9h4V5h2v4h4v2z"/>
          </svg>
          <span v-if="borrowCount > 0" class="badge">{{ borrowCount }}</span>
        </div>
        
        <div class="notification" @click="goToNotifications">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
          </svg>
          <span v-if="unreadCount > 0" class="badge-dot"></span>
        </div>
      </div>
    </div>
    
    <!-- AI 个性化推荐区 -->
    <div class="recommend-section">
      <CategoryTabs 
        :tabs="categories"
        :initial-tab="currentCategory"
        @tab-change="handleTabChange"
        @custom-query="handleCustomQuery"
      />
      
      <div class="book-list" ref="bookListRef">
        <BookCard
          v-for="book in books"
          :key="book.id"
          :book="book"
          @click="goToBookDetail"
          @reserve="handleReserve"
          @detail="goToBookDetail"
        />
        
        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          <span>AI 正在为你重新推荐...</span>
        </div>
        
        <div v-if="!loading && books.length === 0" class="empty">
          <span>暂无推荐图书</span>
        </div>
        
        <!-- 换一批按钮 -->
        <div v-if="books.length > 0" class="refresh-btn" @click="handleRefresh">
          <svg viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
          </svg>
          换一批
        </div>
      </div>
    </div>
    
    <!-- 常见问题快捷入口 -->
    <div class="faq-section">
      <h3>常见问题</h3>
      <div class="faq-tags">
        <div
          v-for="faq in faqs"
          :key="faq.id"
          class="faq-tag"
          @click="handleFAQClick(faq)"
        >
          {{ faq.question }}
        </div>
      </div>
    </div>
    
    <!-- 底部 Tab -->
    <div class="bottom-tab">
      <div 
        class="tab-item"
        :class="{ active: currentTab === 'home' }"
        @click="switchTab('home')"
      >
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
        </svg>
        <span>首页</span>
      </div>
      <div 
        class="tab-item"
        :class="{ active: currentTab === 'recommend' }"
        @click="switchTab('recommend')"
      >
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
        </svg>
        <span>推荐</span>
      </div>
      <div 
        class="tab-item"
        :class="{ active: currentTab === 'chat' }"
        @click="switchTab('chat')"
      >
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
        </svg>
        <span>咨询</span>
      </div>
      <div 
        class="tab-item"
        :class="{ active: currentTab === 'profile' }"
        @click="switchTab('profile')"
      >
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
        </svg>
        <span>我的</span>
      </div>
    </div>
    
    <!-- 悬浮语音按钮 -->
    <VoiceButton
      @voice-result="handleVoiceResult"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import SearchBar from '../components/AIAgent/SearchBar.vue'
import ChatBubble from '../components/AIAgent/ChatBubble.vue'
import VoiceButton from '../components/AIAgent/VoiceButton.vue'
import BookCard from '../components/Recommend/BookCard.vue'
import CategoryTabs from '../components/Recommend/CategoryTabs.vue'
import { getRecommendCategories, getRecommendBooks, customRecommend, refreshRecommend, reserveBook } from '../api/library'
import { getFAQ } from '../api/ai'

export default {
  name: 'HomePage',
  components: {
    SearchBar,
    ChatBubble,
    VoiceButton,
    BookCard,
    CategoryTabs
  },
  setup() {
    const currentTab = ref('home')
    const currentCategory = ref('recommend_for_you')
    const categories = ref([])
    const books = ref([])
    const faqs = ref([])
    const borrowCount = ref(2)
    const unreadCount = ref(1)
    const loading = ref(false)
    const bookListRef = ref(null)
    const excludeBookIds = ref([])
    
    // 加载推荐分类
    const loadCategories = async () => {
      try {
        const res = await getRecommendCategories()
        if (res.success) {
          categories.value = res.data
        }
      } catch (e) {
        console.error('加载分类失败:', e)
        // 使用默认分类
        categories.value = [
          { id: 'recommend_for_you', name: '为你推荐' },
          { id: 'major_related', name: '专业相关' },
          { id: 'hot_borrow', name: '热门借阅' },
          { id: 'new_books', name: '新书上架' }
        ]
      }
    }
    
    // 加载推荐图书
    const loadBooks = async (categoryId) => {
      loading.value = true
      try {
        const res = await getRecommendBooks(categoryId)
        if (res.success) {
          books.value = res.data.list
          // 更新排除列表
          excludeBookIds.value = books.value.map(b => b.id)
        }
      } catch (e) {
        console.error('加载推荐图书失败:', e)
      } finally {
        loading.value = false
      }
    }
    
    // 加载 FAQ
    const loadFAQs = async () => {
      try {
        const res = await getFAQ()
        if (res.success) {
          faqs.value = res.data.slice(0, 6)
        }
      } catch (e) {
        console.error('加载FAQ失败:', e)
        // 默认 FAQ
        faqs.value = [
          { id: 1, question: '图书馆开放时间' },
          { id: 2, question: '最多能借几本书' },
          { id: 3, question: '续借规则' },
          { id: 4, question: '怎么预约图书' },
          { id: 5, question: '借书要收费吗' },
          { id: 6, question: '逾期罚款多少' }
        ]
      }
    }
    
    // 搜索处理
    const handleSearch = (keyword) => {
      console.log('搜索:', keyword)
      // 跳转到聊天页进行 AI 搜索
    }
    
    // 语音输入
    const handleVoiceInput = (isActive) => {
      console.log('语音输入:', isActive)
    }
    
    // 标签切换
    const handleTabChange = (tab) => {
      currentCategory.value = tab.id
      loadBooks(tab.id)
    }
    
    // 自定义推荐
    const handleCustomQuery = async (query) => {
      loading.value = true
      try {
        const res = await customRecommend(query)
        if (res.success) {
          books.value = res.data.list
        }
      } catch (e) {
        console.error('自定义推荐失败:', e)
      } finally {
        loading.value = false
      }
    }
    
    // 刷新推荐
    const handleRefresh = async () => {
      loading.value = true
      try {
        const res = await refreshRecommend(currentCategory.value, excludeBookIds.value.join(','))
        if (res.success) {
          books.value = res.data.list
          excludeBookIds.value = [...excludeBookIds.value, ...books.value.map(b => b.id)]
        }
      } catch (e) {
        console.error('刷新推荐失败:', e)
      } finally {
        loading.value = false
      }
    }
    
    // 预约图书
    const handleReserve = async (book) => {
      try {
        const res = await reserveBook(book.id)
        if (res.success) {
          alert('预约成功！')
        } else {
          alert(res.message || '预约失败')
        }
      } catch (e) {
        console.error('预约失败:', e)
      }
    }
    
    // FAQ 点击
    const handleFAQClick = (faq) => {
      console.log('FAQ点击:', faq)
    }
    
    // 语音结果
    const handleVoiceResult = (result) => {
      console.log('语音识别结果:', result)
      handleSearch(result)
    }
    
    // 页面跳转
    const goToProfile = () => {
      currentTab.value = 'profile'
    }
    
    const goToNotifications = () => {
      console.log('跳转通知页')
    }
    
    const goToBookDetail = (book) => {
      console.log('跳转图书详情:', book)
    }
    
    const switchTab = (tab) => {
      currentTab.value = tab
    }
    
    onMounted(() => {
      loadCategories()
      loadBooks(currentCategory.value)
      loadFAQs()
    })
    
    return {
      currentTab,
      currentCategory,
      categories,
      books,
      faqs,
      borrowCount,
      unreadCount,
      loading,
      bookListRef,
      handleSearch,
      handleVoiceInput,
      handleTabChange,
      handleCustomQuery,
      handleRefresh,
      handleReserve,
      handleFAQClick,
      handleVoiceResult,
      goToProfile,
      goToNotifications,
      goToBookDetail,
      switchTab
    }
  }
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 70px;
}

.top-section {
  background: white;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.top-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.borrow-status,
.notification {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #666;
}

.badge {
  position: absolute;
  top: 0;
  right: 0;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: #f56c6c;
  color: white;
  font-size: 10px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.badge-dot {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 8px;
  height: 8px;
  background: #f56c6c;
  border-radius: 50%;
}

.recommend-section {
  margin-top: 12px;
  background: white;
}

.book-list {
  padding: 12px 0;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #999;
  font-size: 14px;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #f3f3f3;
  border-top-color: #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty {
  text-align: center;
  padding: 40px 0;
  color: #999;
}

.refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  margin: 0 16px;
  background: #f5f5f5;
  border-radius: 20px;
  color: #409eff;
  font-size: 14px;
  cursor: pointer;
}

.faq-section {
  margin-top: 12px;
  background: white;
  padding: 16px;
}

.faq-section h3 {
  margin: 0 0 12px;
  font-size: 16px;
  color: #333;
}

.faq-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.faq-tag {
  padding: 8px 16px;
  background: #f5f5f5;
  border-radius: 18px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: background 0.2s;
}

.faq-tag:hover {
  background: #e6e6e6;
}

.bottom-tab {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: white;
  display: flex;
  justify-content: space-around;
  align-items: center;
  box-shadow: 0 -1dp 10px rgba(0, 0, 0, 0.05);
  z-index: 1000;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  color: #999;
  cursor: pointer;
}

.tab-item.active {
  color: #409eff;
}

.tab-item span {
  font-size: 12px;
}
</style>