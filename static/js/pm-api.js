/**
 * ProjectManager AJAX Library
 * Handles all dynamic interactions with loading spinners and error handling
 */

class ProjectManagerAPI {
    constructor() {
        this.baseUrl = '/api/';
        this.isLoading = false;
        this.setupGlobalLoadingSpinner();
    }

    /**
     * Setup global loading spinner
     */
    setupGlobalLoadingSpinner() {
        const spinnerHTML = `
            <div id="global-loader" class="global-loader hidden">
                <div class="loader-content">
                    <div class="spinner"></div>
                    <p id="loader-message">Loading...</p>
                </div>
            </div>
        `;

        if (!document.getElementById('global-loader')) {
            document.body.insertAdjacentHTML('afterbegin', spinnerHTML);
        }
    }

    /**
     * Show loading spinner
     */
    showLoader(message = 'Loading...') {
        const loader = document.getElementById('global-loader');
        if (loader) {
            document.getElementById('loader-message').textContent = message;
            loader.classList.remove('hidden');
            this.isLoading = true;
        }
    }

    /**
     * Hide loading spinner
     */
    hideLoader() {
        const loader = document.getElementById('global-loader');
        if (loader) {
            loader.classList.add('hidden');
            this.isLoading = false;
        }
    }

    /**
     * Fetch with error handling
     */
    async fetchWithHandler(url, options = {}) {
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                    ...options.headers
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            this.showNotification('Error: ' + error.message, 'error');
            throw error;
        }
    }

    /**
     * Get CSRF token from cookie
     */
    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Get all tasks with filters
     */
    async getTasks(filters = {}) {
        this.showLoader('Loading tasks...');
        try {
            const params = new URLSearchParams(filters);
            const response = await this.fetchWithHandler(`${this.baseUrl}tasks/?${params}`);
            this.hideLoader();
            return response;
        } catch (error) {
            this.hideLoader();
            throw error;
        }
    }

    /**
     * Get all projects
     */
    async getProjects(filters = {}) {
        this.showLoader('Loading projects...');
        try {
            const params = new URLSearchParams(filters);
            const response = await this.fetchWithHandler(`${this.baseUrl}projects/?${params}`);
            this.hideLoader();
            return response;
        } catch (error) {
            this.hideLoader();
            throw error;
        }
    }

    /**
     * Update task status
     */
    async updateTaskStatus(taskId, newStatus) {
        this.showLoader('Updating task...');
        try {
            const response = await this.fetchWithHandler(`${this.baseUrl}tasks/update-status/`, {
                method: 'POST',
                body: JSON.stringify({
                    task_id: taskId,
                    status: newStatus
                })
            });
            this.hideLoader();
            this.showNotification(response.message, 'success');
            return response;
        } catch (error) {
            this.hideLoader();
            throw error;
        }
    }

    /**
     * Log time on task
     */
    async logTaskTime(taskId, minutes) {
        this.showLoader('Logging time...');
        try {
            const response = await this.fetchWithHandler(`${this.baseUrl}tasks/log-time/`, {
                method: 'POST',
                body: JSON.stringify({
                    task_id: taskId,
                    minutes: minutes
                })
            });
            this.hideLoader();
            this.showNotification(response.message, 'success');
            return response;
        } catch (error) {
            this.hideLoader();
            throw error;
        }
    }

    /**
     * Update task priority
     */
    async updateTaskPriority(taskId, priority) {
        try {
            const response = await this.fetchWithHandler(`${this.baseUrl}tasks/update-priority/`, {
                method: 'POST',
                body: JSON.stringify({
                    task_id: taskId,
                    priority: priority
                })
            });
            this.showNotification(response.message, 'success');
            return response;
        } catch (error) {
            throw error;
        }
    }

    /**
     * Get dashboard statistics
     */
    async getDashboardStats() {
        try {
            const response = await this.fetchWithHandler(`${this.baseUrl}dashboard/stats/`);
            return response;
        } catch (error) {
            throw error;
        }
    }

    /**
     * Get kanban view data
     */
    async getKanbanData(projectId = null) {
        this.showLoader('Loading kanban view...');
        try {
            let url = `${this.baseUrl}kanban/`;
            if (projectId) {
                url += `?project_id=${projectId}`;
            }
            const response = await this.fetchWithHandler(url);
            this.hideLoader();
            return response;
        } catch (error) {
            this.hideLoader();
            throw error;
        }
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const notificationHTML = `
            <div class="notification notification-${type}" style="animation: slideInTop 0.3s ease;">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.remove()">×</button>
            </div>
        `;

        const container = document.getElementById('notification-container') || document.body;
        container.insertAdjacentHTML('afterbegin', notificationHTML);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            const notification = container.querySelector('.notification');
            if (notification) {
                notification.style.animation = 'slideOutTop 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }
}

// Global API instance
const pmAPI = new ProjectManagerAPI();

/**
 * Render tasks in table format
 */
function renderTasksTable(tasks, containerId) {
    const container = document.getElementById(containerId);
    if (!tasks || tasks.length === 0) {
        container.innerHTML = '<p class="text-center text-gray-400">No tasks found</p>';
        return;
    }

    let html = `
        <div class="table-responsive">
            <table class="tasks-table">
                <thead>
                    <tr>
                        <th>Task Name</th>
                        <th>Project</th>
                        <th>Priority</th>
                        <th>Status</th>
                        <th>Due Date</th>
                        <th>Progress</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
    `;

    tasks.forEach(task => {
        const statusColor = {
            'TODO': '#666',
            'IN_PROGRESS': '#0099ff',
            'REVIEW': '#ff9900',
            'COMPLETE': '#00cc00'
        };

        const priorityClass = {
            'urgent': 'priority-urgent',
            'high': 'priority-high',
            'medium': 'priority-medium',
            'low': 'priority-low'
        };

        html += `
            <tr class="task-row" data-task-id="${task.id}">
                <td class="task-name">${task.name}</td>
                <td>${task.project}</td>
                <td><span class="${priorityClass[task.priority] || 'priority-medium'}">${task.priority}</span></td>
                <td>
                    <select class="status-select" onchange="updateTaskStatusUI(${task.id}, this.value)">
                        <option value="TODO" ${task.status === 'TODO' ? 'selected' : ''}>To Do</option>
                        <option value="IN_PROGRESS" ${task.status === 'IN_PROGRESS' ? 'selected' : ''}>In Progress</option>
                        <option value="REVIEW" ${task.status === 'REVIEW' ? 'selected' : ''}>Review</option>
                        <option value="COMPLETE" ${task.status === 'COMPLETE' ? 'selected' : ''}>Complete</option>
                    </select>
                </td>
                <td>${task.due_date ? new Date(task.due_date).toLocaleDateString() : 'N/A'}</td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${task.progress}%"></div>
                    </div>
                    <span class="progress-text">${task.progress}%</span>
                </td>
                <td>
                    <button class="btn-icon" onclick="viewTaskDetail(${task.id})" title="View">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-icon" onclick="editTask(${task.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = html;
}

/**
 * Update task status via AJAX
     */
async function updateTaskStatusUI(taskId, newStatus) {
    try {
        await pmAPI.updateTaskStatus(taskId, newStatus);
        // UI already updated by the select change
    } catch (error) {
        console.error('Error updating task status:', error);
    }
}

/**
 * Load and render kanban board
 */
async function loadKanbanBoard(containerId, projectId = null) {
    try {
        const response = await pmAPI.getKanbanData(projectId);
        if (response.success) {
            renderKanban(response.kanban, containerId);
        }
    } catch (error) {
        console.error('Error loading kanban:', error);
    }
}

/**
 * Render kanban board
 */
function renderKanban(kanbanData, containerId) {
    const container = document.getElementById(containerId);
    const statuses = ['TODO', 'IN_PROGRESS', 'REVIEW', 'COMPLETE'];

    let html = '<div class="kanban-board">';

    statuses.forEach(status => {
        const tasks = kanbanData[status] || [];
        const statusLabel = status.replace('_', ' ');

        html += `
            <div class="kanban-column" data-status="${status}">
                <div class="kanban-header">
                    <h3>${statusLabel}</h3>
                    <span class="task-count">${tasks.length}</span>
                </div>
                <div class="kanban-cards" ondrop="dropTask(event)" ondragover="allowDrop(event)">
        `;

        tasks.forEach(task => {
            const priorityColor = {
                'urgent': '#ff0000',
                'high': '#ff6600',
                'medium': '#0066cc',
                'low': '#00aa00'
            };

            html += `
                <div class="kanban-card" draggable="true" ondragstart="dragTask(event)" data-task-id="${task.id}">
                    <div class="card-priority" style="border-left: 4px solid ${priorityColor[task.priority] || '#0066cc'}"></div>
                    <h4>${task.name}</h4>
                    <p class="card-assigned">👤 ${task.assigned_to}</p>
                    ${task.due_date ? `<p class="card-due">📅 ${new Date(task.due_date).toLocaleDateString()}</p>` : ''}
                    ${task.time_estimate ? `<p class="card-time">⏱️ ${task.time_logged}/${task.time_estimate} min</p>` : ''}
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

/**
 * Drag and drop support for kanban
 */
function allowDrop(event) {
    event.preventDefault();
}

function dragTask(event) {
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('taskId', event.target.closest('.kanban-card').dataset.taskId);
}

async function dropTask(event) {
    event.preventDefault();
    const taskId = event.dataTransfer.getData('taskId');
    const newStatus = event.currentTarget.closest('.kanban-column').dataset.status;

    await pmAPI.updateTaskStatus(taskId, newStatus);
    location.reload(); // Refresh to see changes
}
