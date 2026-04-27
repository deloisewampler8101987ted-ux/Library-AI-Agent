<template>
  <div class="book-card" @click="handleClick">
    <div class="book-cover">
      <img 
        v-if="book.cover" 
        :src="book.cover" 
        :alt="book.title"
        @error="handleImageError"
      />
      <div v-else class="default-cover">
        <span>{{ book.title?.charAt(0) }}</span>
      </div>
    </div>
    
    <div class="book-info">
      <h3 class="book-title">{{ book.title }}</h3>
      <p class="book-author">{{ book.author }}</p>
      <p class="book-publisher">{{ book.publisher }}</p>
      
      <p class="book-reason" v-if="book.recommend_reason">
        {{ truncatedReason }}
      </p>
      
      <div class="book-meta">
        <span class="location">
          <svg viewBox="0 0 24 24" width="12" height="12">
            <path fill="currentColor" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
          </svg>
          {{ book.location }}
        </span>
        <span class="availability" :class="{ available: book.available > 0 }">
          可借：{{ book.available }}/{{ book.total }}
        </span>
      </div>
      
      <div class="book-actions">
        <button 
          class="action-btn reserve" 
          :disabled="book.available === 0"
          @click.stop="handleReserve"
        >
          预约
        </button>
        <button 
          class="action-btn detail"
          @click.stop="handleDetail"
        >
          详情
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'BookCard',
  props: {
    book: {
      type: Object,
      required: true,
      default: () => ({})
    }
  },
  emits: ['click', 'reserve', 'detail'],
  setup(props, { emit }) {
    const imageError = ref(false)
    
    const truncatedReason = computed(() => {
      const reason = props.book.recommend_reason || ''
      if (reason.length > 60) {
        return reason.substring(0, 60) + '...'
      }
      return reason
    })
    
    const handleClick = () => {
      emit('click', props.book)
    }
    
    const handleReserve = () => {
      emit('reserve', props.book)
    }
    
    const handleDetail = () => {
      emit('detail', props.book)
    }
    
    const handleImageError = () => {
      imageError.value = true
    }
    
    return {
      truncatedReason,
      handleClick,
      handleReserve,
      handleDetail,
      handleImageError
    }
  }
}
</script>

<style scoped>
.book-card {
  display: flex;
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin: 0 16px 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.3s;
}

.book-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.book-cover {
  width: 80px;
  height: 120px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
  background: #f5f5f5;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.default-cover {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 32px;
  font-weight: bold;
}

.book-info {
  flex: 1;
  margin-left: 12px;
  display: flex;
  flex-direction: column;
}

.book-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author,
.book-publisher {
  font-size: 12px;
  color: #999;
  margin: 0;
}

.book-author {
  margin-bottom: 2px;
}

.book-reason {
  font-size: 12px;
  color: #666;
  margin: 8px 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  font-size: 11px;
  color: #999;
}

.location {
  display: flex;
  align-items: center;
  gap: 2px;
}

.availability {
  color: #f56c6c;
}

.availability.available {
  color: #67c23a;
}

.book-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.action-btn {
  padding: 6px 16px;
  border-radius: 14px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.reserve {
  background: #409eff;
  color: white;
  border: none;
}

.action-btn.reserve:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

.action-btn.detail {
  background: white;
  color: #666;
  border: 1px solid #dcdfe6;
}

.action-btn.detail:hover {
  border-color: #409eff;
  color: #409eff;
}
</style>