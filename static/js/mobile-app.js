/**
 * Mobile App JavaScript
 * Project Manager - Responsive Web Application
 */

// Configuration
const API_URL = window.location.origin;
const WS_PROTOCOL = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_URL = `${WS_PROTOCOL}//${window.location.host}`;

// State
let notificationsSocket = null;
let unreadCount = 0;
let currentUser = null;

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Initialize notifications WebSocket connection
 */
function initializeNotifications() {
  try {
    notificationsSocket = new WebSocket(`${WS_URL}/ws/notifications/`);

    notificationsSocket.onopen = () => {
      console.log('✅ WebSocket connected for notifications');
      loadNotifications();
    };

    notificationsSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'notification') {
        handleNewNotification(data.notification);
      } else if (data.type === 'unread_count') {
        unreadCount = data.count;
        updateNotificationBadge();
      }
    };

    notificationsSocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    notificationsSocket.onclose = () => {
      console.log('WebSocket disconnected');
      // Attempt to reconnect after 3 seconds
      setTimeout(initializeNotifications, 3000);
    };
  } catch (error) {
    console.error('Failed to initialize WebSocket:', error);
  }
}

// ============================================================================
// NOTIFICATIONS
// ============================================================================

/**
 * Load notifications from API
 */
async function loadNotifications() {
  try {
    const notificationsList = document.getElementById('notifications-list');
    if (notificationsList) {
      notificationsList.innerHTML = `
        <div style="display: flex; justify-content: center; align-items: center; padding: 40px 16px;">
          <span class="spinner"></span>
          <span style="margin-left: 12px;">Loading notifications...</span>
        </div>
      `;
    }

    const response = await fetch(`${API_URL}/api/notifications/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      credentials: 'include',
    });

    if (!response.ok) throw new Error('Failed to load notifications');

    const data = await response.json();
    displayNotifications(data.notifications);
    updateNotificationCount(data);
  } catch (error) {
    console.error('Error loading notifications:', error);
    const notificationsList = document.getElementById('notifications-list');
    if (notificationsList) {
      notificationsList.innerHTML = `
        <div style="padding: 20px; text-align: center; color: #999;">
          <p>Failed to load notifications</p>
        </div>
      `;
    }
  }
}

/**
 * Display notifications in the list
 */
function displayNotifications(notifications) {
  const notificationsList = document.getElementById('notifications-list');

  if (!notifications || notifications.length === 0) {
    notificationsList.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🔔</div>
        <div class="empty-state-text">No notifications</div>
      </div>
    `;
    return;
  }

  notificationsList.innerHTML = notifications.map(notif => `
    <div class="list-item ${notif.is_read ? '' : 'unread'}" onclick="markNotificationRead(${notif.id})">
      <div class="list-item-content">
        <div class="list-item-title">${notif.title}</div>
        <div class="list-item-subtitle">${notif.message}</div>
        <div class="comment-time">${new Date(notif.created_at).toLocaleString()}</div>
      </div>
      ${!notif.is_read ? '<span style="color: var(--primary);">●</span>' : ''}
    </div>
  `).join('');
}

/**
 * Handle new notification in real-time
 */
function handleNewNotification(notification) {
  unreadCount++;
  updateNotificationBadge();

  // Show toast notification
  showToast(notification.title, 'info');

  // Reload notifications list if modal is open
  if (document.getElementById('notificationsModal').classList.contains('active')) {
    loadNotifications();
  }
}

/**
 * Mark notification as read
 */
async function markNotificationRead(notificationId, buttonElement = null) {
  try {
    // Show loading on button if provided
    if (buttonElement && buttonElement.classList) {
      setButtonLoading(buttonElement, true, '');
    }

    const response = await fetch(`${API_URL}/api/notifications/mark-read/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ notification_id: notificationId }),
      credentials: 'include',
    });

    if (response.ok) {
      loadNotifications();
      showToast('Notification marked as read', 'success');
    }
  } catch (error) {
    console.error('Error marking notification as read:', error);
    showToast('Failed to mark notification as read', 'error');
  } finally {
    // Clear loading state
    if (buttonElement && buttonElement.classList) {
      setButtonLoading(buttonElement, false);
    }
  }
}

/**
 * Update notification badge count
 */
function updateNotificationBadge() {
  const badge = document.getElementById('notif-count');
  if (unreadCount > 0) {
    badge.textContent = unreadCount > 9 ? '9+' : unreadCount;
    badge.style.display = 'flex';
  } else {
    badge.style.display = 'none';
  }
}

/**
 * Update notification count from API response
 */
function updateNotificationCount(data) {
  const unreadNotifications = data.notifications.filter(n => !n.is_read).length;
  unreadCount = unreadNotifications;
  updateNotificationBadge();
}

// ============================================================================
// LOADING STATE MANAGEMENT
// ============================================================================

/**
 * Set button loading state
 */
function setButtonLoading(buttonElement, isLoading, loadingText = 'Loading...') {
  if (!buttonElement) return;

  if (isLoading) {
    buttonElement.disabled = true;
    buttonElement.dataset.originalContent = buttonElement.innerHTML;
    buttonElement.innerHTML = `<span class="spinner" style="width: 16px; height: 16px; border: 2px solid rgba(0,0,0,0.2); border-top-color: white;"></span> ${loadingText}`;
    buttonElement.classList.add('loading');
  } else {
    buttonElement.disabled = false;
    buttonElement.innerHTML = buttonElement.dataset.originalContent || 'Done';
    buttonElement.classList.remove('loading');
  }
}

/**
 * Debounce function to prevent rapid repeated calls
 */
function debounce(func, wait = 300) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Throttle function for repeated events (like scroll, resize)
 */
function throttle(func, wait = 300) {
  let timeout;
  let previous = 0;
  return function executedFunction(...args) {
    const now = Date.now();
    const remaining = wait - (now - previous);
    if (remaining <= 0 || remaining > wait) {
      if (timeout) clearTimeout(timeout);
      previous = now;
      func(...args);
    } else if (!timeout) {
      timeout = setTimeout(() => {
        previous = Date.now();
        func(...args);
      }, remaining);
    }
  };
}

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Generic fetch wrapper with error handling
 */
async function apiCall(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
        ...options.headers,
      },
      credentials: 'include',
      ...options,
    });

    if (!response.ok) {
      if (response.status === 401) {
        window.location.href = '/signin/';
      }
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    showToast('Error: ' + error.message, 'error');
    throw error;
  }
}

/**
 * Get dashboard analytics
 */
async function getDashboardAnalytics() {
  return apiCall('/api/dashboard/analytics/');
}

/**
 * Load and display dashboard (with loading state)
 */
async function loadDashboard() {
  try {
    const dashboardContent = document.querySelector('.page-content');
    if (dashboardContent) {
      dashboardContent.innerHTML = `
        <div style="display: flex; justify-content: center; align-items: center; padding: 40px 16px;">
          <span class="spinner"></span>
          <span style="margin-left: 12px;">Loading dashboard...</span>
        </div>
      `;
    }

    const data = await getDashboardAnalytics();
    displayDashboard(data);
    showToast('Dashboard loaded', 'success');
    return data;
  } catch (error) {
    console.error('Error loading dashboard:', error);
    showToast('Failed to load dashboard', 'error');
    throw error;
  }
}

/**
 * Display dashboard data
 */
function displayDashboard(data) {
  const dashboardContent = document.querySelector('.page-content');
  if (!dashboardContent) return;

  const statsHtml = `
    <div class="stats-container">
      <div class="stat-card">
        <div class="stat-icon">📋</div>
        <div class="stat-value">${data.total_tasks || 0}</div>
        <div class="stat-label">Total Tasks</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⏳</div>
        <div class="stat-value">${data.in_progress_count || 0}</div>
        <div class="stat-label">In Progress</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✓</div>
        <div class="stat-value">${data.completed_count || 0}</div>
        <div class="stat-label">Completed</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⚠</div>
        <div class="stat-value">${data.overdue_count || 0}</div>
        <div class="stat-label">Overdue</div>
      </div>
    </div>
  `;

  dashboardContent.innerHTML = statsHtml;
}

/**
 * Get tasks list
 */
async function getTasks(filters = {}) {
  const params = new URLSearchParams(filters);
  return apiCall(`/api/tasks/?${params}`);
}

/**
 * Load and display tasks (with loading state)
 */
async function loadTasks(filters = {}) {
  try {
    const data = await getTasks(filters);
    displayTasks(data.tasks);
    return data;
  } catch (error) {
    console.error('Error loading tasks:', error);
    showToast('Failed to load tasks', 'error');
    throw error;
  }
}

/**
 * Display tasks in list
 */
function displayTasks(tasks) {
  const tasksList = document.getElementById('tasks-list');
  if (!tasksList) return;

  if (!tasks || tasks.length === 0) {
    tasksList.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">✓</div>
        <div class="empty-state-text">No tasks found</div>
      </div>
    `;
    return;
  }

  tasksList.innerHTML = tasks.map(task => `
    <div class="list-item" onclick="openTaskDetail(${task.id})">
      <div class="list-item-content">
        <div class="list-item-title">${task.title}</div>
        <div class="list-item-subtitle">${task.description || 'No description'}</div>
        <div style="margin-top: 8px;">
          <span class="badge badge-${task.priority.toLowerCase()}">${task.priority}</span>
          <span class="badge badge-${task.status.toLowerCase()}">${task.status}</span>
        </div>
      </div>
      <span style="color: var(--primary);">›</span>
    </div>
  `).join('');
}

/**
 * Get projects list
 */
async function getProjects() {
  return apiCall('/api/projects/');
}

/**
 * Get task comments
 */
async function getTaskComments(taskId) {
  return apiCall(`/api/tasks/${taskId}/comments/`);
}

/**
 * Create task comment
 */
async function createComment(taskId, content) {
  return apiCall(`/api/tasks/${taskId}/comments/create/`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
}

/**
 * Update task status
 */
async function updateTaskStatus(taskId, status, buttonElement = null) {
  try {
    // Show loading on button if provided
    if (buttonElement && buttonElement.classList) {
      setButtonLoading(buttonElement, true, 'Updating...');
    }

    const result = await apiCall('/api/tasks/update-status/', {
      method: 'POST',
      body: JSON.stringify({ task_id: taskId, status }),
    });

    showToast('Task status updated successfully', 'success');

    // Reload task list
    loadTasks();

    return result;
  } catch (error) {
    showToast('Failed to update task status', 'error');
    throw error;
  } finally {
    // Clear loading state
    if (buttonElement && buttonElement.classList) {
      setButtonLoading(buttonElement, false);
    }
  }
}

/**
 * Get activity feed
 */
async function getActivityFeed(taskId = null, projectId = null) {
  const params = new URLSearchParams();
  if (taskId) params.append('task_id', taskId);
  if (projectId) params.append('project_id', projectId);
  return apiCall(`/api/activity-feed/?${params}`);
}

/**
 * Upload file attachment
 */
async function uploadAttachment(taskId, file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_URL}/api/tasks/${taskId}/attachments/upload/`, {
    method: 'POST',
    body: formData,
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
    },
    credentials: 'include',
  });

  if (!response.ok) throw new Error('Upload failed');
  return response.json();
}

/**
 * Watch a task
 */
async function watchTask(taskId) {
  return apiCall(`/api/tasks/${taskId}/watch/`, { method: 'POST' });
}

/**
 * Unwatch a task
 */
async function unwatchTask(taskId) {
  return apiCall(`/api/tasks/${taskId}/unwatch/`, { method: 'POST' });
}

// ============================================================================
// UI INTERACTIONS
// ============================================================================

/**
 * Toggle notifications panel
 */
function toggleNotifications() {
  const modal = document.getElementById('notificationsModal');
  modal.classList.toggle('active');
  if (modal.classList.contains('active')) {
    loadNotifications();
  }
}

/**
 * Open notifications panel
 */
function openNotificationsPanel() {
  document.getElementById('notificationsModal').classList.add('active');
  loadNotifications();
}

/**
 * Close notifications panel
 */
function closeNotificationsPanel() {
  document.getElementById('notificationsModal').classList.remove('active');
}

/**
 * Toggle menu dropdown
 */
function toggleMenu() {
  const modal = document.getElementById('menuModal');
  modal.classList.toggle('active');
}

/**
 * Close menu
 */
function closeMenu() {
  document.getElementById('menuModal').classList.remove('active');
}

/**
 * Toggle dark mode
 */
function toggleDarkMode() {
  document.body.classList.toggle('dark-mode');
  localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
  closeMenu();
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
  // Create toast element
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    bottom: 100px;
    left: 16px;
    right: 16px;
    padding: 12px 16px;
    background: ${type === 'error' ? 'var(--danger)' : type === 'success' ? 'var(--secondary)' : 'var(--primary)'};
    color: white;
    border-radius: 8px;
    z-index: 2000;
    animation: slideUp 0.3s ease-out;
  `;

  document.body.appendChild(toast);

  // Remove after 3 seconds
  setTimeout(() => {
    toast.remove();
  }, 3000);
}

/**
 * Pull to refresh
 */
function enablePullToRefresh() {
  let startY = 0;
  const pageContent = document.querySelector('.page-content');

  document.addEventListener('touchstart', (e) => {
    startY = e.touches[0].clientY;
  });

  document.addEventListener('touchmove', (e) => {
    if (pageContent.scrollTop === 0 && e.touches[0].clientY > startY + 50) {
      // User pulled down
      showRefreshing();
    }
  });

  document.addEventListener('touchend', () => {
    // Refresh page on complete
  });
}

function showRefreshing() {
  showToast('Refreshing...', 'info');
  location.reload();
}

// ============================================================================
// FILTER & SEARCH
// ============================================================================

/**
 * Filter tasks by status
 */
function filterTasksByStatus(status) {
  // Update active filter button and show loading
  const buttons = document.querySelectorAll('.filter-btn');
  buttons.forEach(btn => {
    btn.classList.remove('active');
    if (btn.dataset.status === status || (status === 'all' && btn.textContent.toLowerCase() === 'all')) {
      btn.classList.add('active');
      setButtonLoading(btn, true, '');
    }
  });

  // Load filtered tasks
  const fetchTasks = async () => {
    try {
      showToast('Loading tasks...', 'info');
      let data;
      if (status === 'all') {
        data = await getTasks();
      } else {
        data = await getTasks({ status });
      }
      displayTasks(data.tasks);
      showToast('Tasks loaded', 'success');
    } catch (error) {
      showToast('Failed to load tasks', 'error');
    } finally {
      // Clear loading state
      document.querySelectorAll('.filter-btn.active').forEach(btn => {
        setButtonLoading(btn, false);
      });
    }
  };

  fetchTasks();
}

/**
 * Search tasks with debounce
 */
const searchTasks = debounce(async function(query) {
  if (query.length < 2) return;

  try {
    showToast('Searching...', 'info');
    const response = await fetch(`${API_URL}/search-task/?q=${encodeURIComponent(query)}`, {
      credentials: 'include',
    });

    if (response.ok) {
      const html = await response.text();
      // Display results
      console.log('Search results:', html);
      showToast('Search complete', 'success');
    }
  } catch (error) {
    console.error('Search error:', error);
    showToast('Search failed', 'error');
  }
}, 500);

// ============================================================================
// MODAL FUNCTIONS
// ============================================================================

/**
 * Open create task modal
 */
function openCreateTaskModal() {
  const modal = document.getElementById('createTaskModal');
  if (modal) {
    modal.classList.add('active');
  }
}

/**
 * Close modal
 */
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
  }
}

/**
 * Open task detail modal
 */
async function openTaskDetail(taskId) {
  const modal = document.getElementById(`taskDetailModal-${taskId}`);
  if (!modal) {
    console.warn('Modal not found for task', taskId);
    return;
  }

  // Show loading state
  const modalBody = modal.querySelector('.modal-body');
  const originalContent = modalBody.innerHTML;
  modalBody.innerHTML = `
    <div style="display: flex; justify-content: center; align-items: center; padding: 40px 16px;">
      <span class="spinner"></span>
      <span style="margin-left: 12px;">Loading task details...</span>
    </div>
  `;
  modal.classList.add('active');

  try {
    const [comments, activity] = await Promise.all([
      getTaskComments(taskId),
      getActivityFeed(taskId)
    ]);

    // Update modal with task data
    const taskContent = `
      <div class="comment-section">
        <h3>Comments</h3>
        ${comments.comments && comments.comments.length > 0 ?
          comments.comments.map(c => `
            <div class="comment">
              <div class="comment-author">${c.author}</div>
              <div class="comment-text">${c.content}</div>
              <div class="comment-time">${formatDate(c.created_at)}</div>
            </div>
          `).join('')
          : '<p style="color: #999;">No comments yet</p>'
        }
      </div>
      <div class="comment-input">
        <input type="text" placeholder="Add a comment..." id="commentInput-${taskId}">
        <button onclick="submitComment(${taskId})" class="btn btn-primary btn-sm">Send</button>
      </div>
    `;
    modalBody.innerHTML = taskContent;
  } catch (error) {
    console.error('Error loading task details:', error);
    modalBody.innerHTML = `
      <div style="padding: 20px;">
        <p style="color: var(--danger);">Error loading task details</p>
        <button onclick="closeModal('taskDetailModal-${taskId}')" class="btn btn-secondary btn-block">Close</button>
      </div>
    `;
  }
}

/**
 * Submit comment with loading indicator
 */
async function submitComment(taskId) {
  const input = document.getElementById(`commentInput-${taskId}`);
  if (!input || !input.value.trim()) {
    showToast('Please enter a comment', 'warning');
    return;
  }

  const content = input.value;
  const button = event.target;

  try {
    setButtonLoading(button, true, 'Sending...');
    const result = await createComment(taskId, content);

    input.value = '';
    showToast('Comment added successfully', 'success');

    // Reload comments
    openTaskDetail(taskId);
  } catch (error) {
    showToast('Failed to add comment', 'error');
  } finally {
    setButtonLoading(button, false);
  }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get CSRF token from cookies
 */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/**
 * Format date to readable format
 */
function formatDate(dateString) {
  const date = new Date(dateString);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  if (date.toDateString() === today.toDateString()) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } else if (date.toDateString() === yesterday.toDateString()) {
    return 'Yesterday';
  } else {
    return date.toLocaleDateString();
  }
}

/**
 * Format time duration
 */
function formatDuration(minutes) {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  if (hours > 0) {
    return `${hours}h ${mins}m`;
  }
  return `${mins}m`;
}

/**
 * Redirect to URL
 */
function navigateTo(url) {
  window.location.href = url;
}

// ============================================================================
// INITIALIZATION
// ============================================================================

// Restore dark mode preference
document.addEventListener('DOMContentLoaded', () => {
  if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
  }

  // Enable pull to refresh
  enablePullToRefresh();

  // Load initial data
  loadNotifications();
});
