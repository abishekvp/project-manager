const TASK_STATUS = ['TODO', 'PROGRESS', 'VERIFY', 'CORRECTION', 'COMPLETE']
const PROJECT_STATUS = ["DESIGN", "DEV1", "TEST1", "DEV2", "TEST2", "FINAL", "COMPLETE"]
const TASK_STATUS_COLORS = {
    'TODO': 'background: gray; color: white',
    'PROGRESS': 'background: #0d6efd; color: white',
    'VERIFY': 'background: lightblue; color: black',
    'CORRECTION': 'background: #dc3545; color: white',
    'HOLD': 'background: red; color: white',
    'COMPLETE': 'background: #4BB543; color: white',
};
const LEAD_STATUS_COLORS = {
    'TODO': 'background: gray; color: white',
    'PROGRESS': 'background: #0d6efd; color: white',
    'VERIFY': 'background: lightblue; color: black',
    'CORRECTION': 'background: #dc3545; color: white',
    'HOLD': 'background: red; color: white',
    'COMPLETE': 'background: #4BB543; color: white',
};

const STATUS_COLOR = {
    "DESIGN": "secondary",
    "DEVELOPMENT": "info",
    "REVIEW": "warning",
    "CORRECTION": "primary",
    "UPDATE": "warning",
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
    $('#assignTaskModal').modal('show');
    $('#assignTaskForm input[name="task_id"]').val(taskid);
    $('#user-search-input').val('');
    $('#user-search-results').empty();
}

function open_assign_project_form(projectid) {
    $('#assignProjectModal').modal('show');
    $('#assignProjectForm input[name="project_id"]').val(projectid);
    $('#manager-search-input').val('');
    $('#manager-search-results').empty();
}

function loading(){
    document.getElementById("loader").style.display = "block";
}

function loaded(){
    document.getElementById("loader").style.display = "none";
}