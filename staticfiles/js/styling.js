const TASK_STATUS = ['TODO', 'IN-PROGRESS', 'VERIFY', 'CORRECTION', 'COMPLETE']
const PROJECT_STATUS = ["DESIGN", "DEV1", "TEST1", "DEV2", "TEST2", "FINAL", "COMPLETE"]
const TASK_STATUS_COLORS = {
    'TODO': 'background: gray; color: white;',
    'IN-PROGRESS': 'background: #0d6efd; color: white;',
    'VERIFY': 'background: lightblue; color: black;font-weight: 600',
    'CORRECTION': 'background: #dc3545; color: white;font-weight: 600',
    'HOLD': 'background: red; color: white;font-weight: 600',
    'COMPLETE': 'background: #4BB543; color: white;font-weight: 600',
};
const STATUS_COLOR = {
    "DESIGN": "secondary",
    "DEV1": "info",
    "TEST1": "warning",
    "DEV2": "primary",
    "TEST2": "warning",
    "FINAL": "danger",
    "COMPLETE": "success"
};

function setTaskStatusBadge(taskId, status){
    var taskstatus = document.getElementById(taskId)
    taskstatus.style = TASK_STATUS_COLORS[status]
}

function setProjectStatusBadge(status) {
    const badge = document.getElementById("project-status-badge");
    badge.textContent = status;
    badge.className = `badge bg-${STATUS_COLOR[status]}`;
}

function open_assign_task_form(taskid) {
    localStorage.setItem("taskid", taskid);
    $('#assignTaskModal').modal('show');
    $('#assignTaskForm input[name="task_id"]').val(taskid);
    $('#user-search-input').val('');
    $('#user-search-results').empty();
}

function view_more(description) {
    $('#fullDescription').text(description);
    $('#viewMoreModal').modal('show');
}