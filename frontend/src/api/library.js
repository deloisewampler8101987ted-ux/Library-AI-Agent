// filepath: frontend/src/api/library.js
/**
 * 对接 LMS 借阅、预约、查书接口
 */

import axios from 'axios'

// 创建 axios 实例
const libraryApi = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000
})

// 请求拦截器
libraryApi.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
libraryApi.interceptors.response.use(
  response => response.data,
  error => {
    console.error('Library API Error:', error)
    return Promise.reject(error)
  }
)

// ==================== 图书查询 ====================

/**
 * 搜索图书
 * @param {string} keyword - 搜索关键词
 * @param {string} category - 分类（可选）
 * @param {number} page - 页码
 * @param {number} pageSize - 每页数量
 */
export function searchBooks(keyword, category = null, page = 1, pageSize = 10) {
  return libraryApi.get('/v1/books/search', {
    params: { keyword, category, page, page_size: pageSize }
  })
}

/**
 * 获取图书分类列表
 */
export function getCategories() {
  return libraryApi.get('/v1/books/category')
}

/**
 * 根据分类获取图书
 * @param {string} category - 分类名称
 * @param {number} page - 页码
 * @param {number} pageSize - 每页数量
 */
export function getBooksByCategory(category, page = 1, pageSize = 10) {
  return libraryApi.get(`/v1/books/category/${encodeURIComponent(category)}`, {
    params: { page, page_size: pageSize }
  })
}

/**
 * 获取热门图书
 * @param {number} limit - 返回数量
 */
export function getHotBooks(limit = 10) {
  return libraryApi.get('/v1/books/hot', {
    params: { limit }
  })
}

/**
 * 获取新书
 * @param {number} limit - 返回数量
 */
export function getNewBooks(limit = 10) {
  return libraryApi.get('/v1/books/new', {
    params: { limit }
  })
}

/**
 * 获取图书详情
 * @param {string} bookId - 图书ID
 */
export function getBookDetail(bookId) {
  return libraryApi.get(`/v1/books/${bookId}`)
}

// ==================== 借阅管理 ====================

/**
 * 获取借阅状态
 * @param {string} userId - 用户ID
 */
export function getBorrowStatus(userId = 'default_user') {
  return libraryApi.get('/v1/borrow/status', {
    params: { user_id: userId }
  })
}

/**
 * 借书
 * @param {string} bookId - 图书ID
 * @param {string} userId - 用户ID
 */
export function borrowBook(bookId, userId = 'default_user') {
  return libraryApi.post('/v1/books/borrow', {
    book_id: bookId,
    user_id: userId
  })
}

/**
 * 还书
 * @param {string} recordId - 借阅记录ID
 * @param {string} userId - 用户ID
 */
export function returnBook(recordId, userId = 'default_user') {
  return libraryApi.post('/v1/books/return', {
    params: { record_id: recordId, user_id: userId }
  })
}

/**
 * 续借
 * @param {string} recordId - 借阅记录ID
 * @param {string} userId - 用户ID
 */
export function renewBook(recordId, userId = 'default_user') {
  return libraryApi.post('/v1/books/renew', {
    params: { record_id: recordId, user_id: userId }
  })
}

// ==================== 预约管理 ====================

/**
 * 预约图书
 * @param {string} bookId - 图书ID
 * @param {string} userId - 用户ID
 */
export function reserveBook(bookId, userId = 'default_user') {
  return libraryApi.post('/v1/books/reserve', {
    book_id: bookId,
    user_id: userId
  })
}

/**
 * 取消预约
 * @param {string} reservationId - 预约记录ID
 * @param {string} userId - 用户ID
 */
export function cancelReservation(reservationId, userId = 'default_user') {
  return libraryApi.post('/v1/books/reserve/cancel', {
    params: { reservation_id: reservationId, user_id: userId }
  })
}

// ==================== 推荐 ====================

/**
 * 获取推荐分类
 */
export function getRecommendCategories() {
  return libraryApi.get('/v1/books/recommend/categories')
}

/**
 * 获取推荐图书
 * @param {string} categoryId - 分类ID
 * @param {string} userId - 用户ID
 * @param {number} page - 页码
 * @param {number} pageSize - 每页数量
 */
export function getRecommendBooks(categoryId, userId = 'default_user', page = 1, pageSize = 10) {
  return libraryApi.get(`/v1/books/recommend/${categoryId}`, {
    params: { user_id: userId, page, page_size: pageSize }
  })
}

/**
 * 刷新推荐（换一批）
 * @param {string} categoryId - 分类ID
 * @param {string} excludeIds - 排除的图书ID
 */
export function refreshRecommend(categoryId, excludeIds = '') {
  return libraryApi.post('/v1/books/recommend/refresh', {
    params: { category_id: categoryId, exclude_ids: excludeIds }
  })
}

/**
 * 自定义推荐
 * @param {string} query - 用户需求
 * @param {string} userId - 用户ID
 */
export function customRecommend(query, userId = 'default_user') {
  return libraryApi.post('/v1/books/recommend/custom', {
    params: { query, user_id: userId }
  })
}

// ==================== 通知 ====================

/**
 * 获取通知列表
 * @param {string} userId - 用户ID
 */
export function getNotifications(userId = 'default_user') {
  return libraryApi.get('/v1/notifications', {
    params: { user_id: userId }
  })
}

export default {
  // 图书查询
  searchBooks,
  getCategories,
  getBooksByCategory,
  getHotBooks,
  getNewBooks,
  getBookDetail,
  
  // 借阅管理
  getBorrowStatus,
  borrowBook,
  returnBook,
  renewBook,
  
  // 预约管理
  reserveBook,
  cancelReservation,
  
  // 推荐
  getRecommendCategories,
  getRecommendBooks,
  refreshRecommend,
  customRecommend,
  
  // 通知
  getNotifications
}