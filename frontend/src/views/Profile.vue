<template>
  <div class="profile-page">
    <!-- 顶部用户信息 -->
    <div class="profile-header">
      <div class="user-avatar">
        <svg viewBox="0 0 24 24" width="48" height="48">
          <path fill="currentColor" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
        </svg>
      </div>
      <h2>读者用户</h2>
      <p>计算机科学与技术专业 · 大一</p>
    </div>
    
    <!-- 借阅状态卡片 -->
    <div class="borrow-card">
      <div class="borrow-header">
        <h3>当前借阅</h3>
        <span class="borrow-count">{{ borrowStatus.borrowing_count }} 本</span>
      </div>
      
      <div v-if="borrowStatus.records && borrowStatus.records.length > 0" class="borrow-list">
        <div 
          v-for="record in borrowStatus.records" 
          :key="record.id"
          class="borrow-item"
        >
          <div class="book-info">
            <h4>{{ record.book_title }}</h4>
            <p>借阅日期：{{ record.borrow_date }}</p>
            <p :class="{ overdue: record.is_overdue }">
              到期日期：{{ record.due_date }}
              <span v-if="record.is_overdue" class="overdue-tag">已逾期</span>
            </p>
          </div>
          <div class="book-actions">
            <button class="renew-btn" @click="handleRenew(record)">续借</button>
            <button class="return-btn" @click="handleReturn(record)">还书</button>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-borrow">
        <p>暂无借阅图书</p>
        <button class="browse-btn" @click="goToHome">去借书</button>
      </div>
    </div>
    
    <!-- 预约记录 -->
    <div class="reserve-card">
      <div class="card-header">
        <h3>我的预约</h3>
        <span class="count">{{ reservations.length }} 本</span>
      </div>
      
      <div v-if="reservations.length > 0" class="reserve-list">
        <div 
          v-for="res in reservations" 
          :key="res.id"
          class="reserve-item"
        >
          <div class="book-info">
            <h4>{{ res.book_title }}</h4>
            <p>预约日期：{{ res.reserve_date }}</p>
            <p>到期日期：{{ res.expire_date }}</p>
          </div>
          <button class="cancel-btn" @click="handleCancelReserve(res)">取消预约</button>
        </div>
      </div>
      
      <div v-else class="empty-reserve">
        <p>暂无预约记录</p>
      </div>
    </div>
    
    <!-- 功能菜单 -->
    <div class="menu-section">
      <div class="menu-item" @click="goToHistory">
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/>
        </svg>
        <span>借阅历史</span>
        <svg class="arrow" viewBox="0 0 24 24" width="16" height="16">
          <path fill="currentColor" d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
        </svg>
      </div>
      
      <div class="menu-item" @click="goToFavorites">
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
        </svg>
        <span>我的收藏</span>
        <svg class="arrow" viewBox="0 0 24 24" width="16" height="16">
          <path fill="currentColor" d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
        </svg>
      </div>
      
      <div class="menu-item" @click="goToSettings">
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
        </svg>
        <span>设置</span>
        <svg class="arrow" viewBox="0 0 24 24" width="16" height="16">
          <path fill="currentColor" d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
        </svg>
      </div>
      
      <div class="menu-item" @click="goToHelp">
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/>
        </svg>
        <span>帮助与反馈</span>
        <svg class="arrow" viewBox="0 0 24 24" width="16" height="16">
          <path fill="currentColor" d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
        </svg>
      </div>
    </div>
    
    <!-- 底部 Tab -->
    <div class="bottom-tab">
      <div 
        class="tab-item"
        :class="{ active: currentTab === 'home' }"
        @click="goToHome"
      >
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
        </svg>
        <span>首页</span>
      </div>
      <div 
        class="tab-item"
        :class="{ active: currentTab === 'recommend' }"
        @click="goToRecommend"
      >
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
        </svg>
        <span>推荐</span>
      </div>
      <div 
        class="tab-item"
        :class="{ active: currentTab === 'chat' }"
        @click="goToChat"
      >
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
        </svg>
        <span>咨询</span>
      </div>
      <div 
        class="tab-item"
        :class="{ active: currentTab === 'profile' }"
        @click="goToProfile"
      >
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
        </svg>
        <span>我的</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { getBorrowStatus, renewBook, returnBook, cancelReservation } from '../api/library'

export default {
  name: 'ProfilePage',
  setup() {
    const currentTab = ref('profile')
    const borrowStatus = ref({
      borrowing_count: 0,
      overdue_count: 0,
      records: []
    })
    const reservations = ref([])
    
    // 加载借阅状态
    const loadBorrowStatus = async () => {
      try {
        const res = await getBorrowStatus()
        if (res.success) {
          borrowStatus.value = res.data
        }
      } catch (e) {
        console.error('加载借阅状态失败:', e)
        // 模拟数据
        borrowStatus.value = {
          borrowing_count: 2,
          overdue_count: 0,
          records: [
            {
              id: 'BR001',
              book_title: 'Python编程：从入门到实践',
              borrow_date: '2026-04-01',
              due_date: '2026-04-30',
              is_overdue: false
            },
            {
              id: 'BR002',
              book_title: '活着',
              borrow_date: '2026-04-15',
              due_date: '2026-05-15',
              is_overdue: false
            }
          ]
        }
      }
    }
    
    // 续借
    const handleRenew = async (record) => {
      try {
        const res = await renewBook(record.id)
        if (res.success) {
          alert('续借成功！')
          loadBorrowStatus()
        } else {
          alert(res.message || '续借失败')
        }
      } catch (e) {
        console.error('续借失败:', e)
      }
    }
    
    // 还书
    const handleReturn = async (record) => {
      try {
        const res = await returnBook(record.id)
        if (res.success) {
          alert('还书成功！')
          loadBorrowStatus()
        } else {
          alert(res.message || '还书失败')
        }
      } catch (e) {
        console.error('还书失败:', e)
      }
    }
    
    // 取消预约
    const handleCancelReserve = async (res) => {
      try {
        const result = await cancelReservation(res.id)
        if (result.success) {
          alert('取消预约成功！')
          // 刷新预约列表
        } else {
          alert(result.message || '取消失败')
        }
      } catch (e) {
        console.error('取消预约失败:', e)
      }
    }
    
    // 页面跳转
    const goToHome = () => {
      console.log('跳转首页')
    }
    
    const goToRecommend = () => {
      console.log('跳转推荐')
    }
    
    const goToChat = () => {
      console.log('跳转咨询')
    }
    
    const goToProfile = () => {
      console.log('跳转我的')
    }
    
    const goToHistory = () => {
      console.log('跳转借阅历史')
    }
    
    const goToFavorites = () => {
      console.log('跳转收藏')
    }
    
    const goToSettings = () => {
      console.log('跳转设置')
    }
    
    const goToHelp = () => {
      console.log('跳转帮助')
    }
    
    onMounted(() => {
      loadBorrowStatus()
    })
    
    return {
      currentTab,
      borrowStatus,
      reservations,
      handleRenew,
      handleReturn,
      handleCancelReserve,
      goToHome,
      goToRecommend,
      goToChat,
      goToProfile,
      goToHistory,
      goToFavorites,
      goToSettings,
      goToHelp
    }
  }
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 70px;
}

.profile-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
  text-align: center;
  color: white;
}

.user-avatar {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-header h2 {
  margin: 0 0 8px;
  font-size: 20px;
}

.profile-header p {
  margin: 0;
  font-size: 14px;
  opacity: 0.8;
}

.borrow-card,
.reserve-card {
  background: white;
  margin: 16px;
  border-radius: 12px;
  padding: 16px;
}

.borrow-header,
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.borrow-header h3,
.card-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.borrow-count,
.count {
  font-size: 14px;
  color: #409eff;
}

.borrow-item,
.reserve-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.borrow-item:last-child,
.reserve-item:last-child {
  border-bottom: none;
}

.book-info h4 {
  margin: 0 0 4px;
  font-size: 14px;
  color: #333;
}

.book-info p {
  margin: 2px 0;
  font-size: 12px;
  color: #999;
}

.book-info .overdue {
  color: #f56c6c;
}

.overdue-tag {
  background: #f56c6c;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  margin-left: 8px;
}

.book-actions {
  display: flex;
  gap: 8px;
}

.renew-btn,
.return-btn,
.cancel-btn {
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.renew-btn {
  background: #f0f7ff;
  color: #409eff;
  border: 1px solid #409eff;
}

.return-btn {
  background: #fef0f0;
  color: #f56c6c;
  border: 1px solid #f56c6c;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
  border: 1px solid #dcdfe6;
}

.empty-borrow,
.empty-reserve {
  text-align: center;
  padding: 20px 0;
  color: #999;
}

.browse-btn {
  margin-top: 12px;
  padding: 8px 24px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
}

.menu-section {
  background: white;
  margin: 16px;
  border-radius: 12px;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item svg:first-child {
  color: #409eff;
  margin-right: 12px;
}

.menu-item span {
  flex: 1;
  font-size: 14px;
  color: #333;
}

.menu-item .arrow {
  color: #c0c4cc;
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