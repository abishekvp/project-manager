function load_tasks(tasks){
    $(".tasks_table_data").empty();
    tasks.forEach((task, index) => {
        setTimeout(function () {
            const statusOptions = `
                <select onchange="updatePeerTaskStatus('${encodeURIComponent(JSON.stringify(task))}', this.value)" class="form-select task-status" id="${task.id}" style="${TASK_STATUS_COLORS[task.status]}">
                    <option value="TODO" ${task.status === 'TODO' ? 'selected' : ''}>TODO</option>
                    <option value="PROGRESS" ${task.status === 'PROGRESS' ? 'selected' : ''}>PROGRESS</option>
                    <option value="VERIFY" ${task.status === 'VERIFY' ? 'selected' : ''}>VERIFY</option>
                    <option value="CORRECTION" ${task.status === 'CORRECTION' ? 'selected' : ''}>CORRECTION</option>
                    <option value="HOLD" ${task.status === 'HOLD' ? 'selected' : ''}>HOLD</option>
                    <option value="COMPLETE" ${task.status === 'COMPLETE' ? 'selected' : ''}>COMPLETE</option>
                </select>
            `;
            $(".tasks_table_data").append(`
                <tr>
                    <td>${task.id}</td>
                    <td>${task.name} <i class="fas fa-file-alt text-primary me-3 px-1" onclick="view_task_details('${task.id}')" style="cursor: pointer;" title="Description"></i></td>
                    <td>${task.created}</td>
                    <td>${task.started}</td>
                    <td>${task.updated}</td>
                    <td>${task.due}</td>
                    <td>${statusOptions}</td>
                </tr>
            `);
        }, 0); // Delay each task by 200ms (adjust as needed)
    });
}

function load_tasks_for_view(tasks){
    $(".tasks_table_data").empty();
    tasks.forEach((task, index) => {
        setTimeout(function () {
            $(".tasks_table_data").append(`
                <tr>
                    <td>${task.id}</td>
                    <td>${task.name} <i class="fas fa-file-alt text-primary me-3 px-1" onclick="view_task_details('${task.id}')" style="cursor: pointer;" title="Description"></i></td>
                    <td>${task.project}</td>
                    <td>${task.created}</td>
                    <td>${task.started}</td>
                    <td>${task.updated}</td>
                    <td>${task.due}</td>
                    <td><span class="task-status-badge" style="${TASK_STATUS_COLORS[task.status]}">${task.status}</span></td>
                </tr>
            `);
        }, 0); // Delay each task by 200ms (adjust as needed)
    });}

function get_peer_projects() {
    $.ajax({
        type: "GET",
        url: "/peer/view-projects",
        success: function (response) {
            $(".projects_table_data").empty();
            response["projects"].forEach(project => {
                setTimeout(function () {
                    $(".projects_table_data").append(`
                        <tr>
                            <td>${project.id}</td>
                            <td>${project.name} <i class="fa-solid fa-up-right-from-square text-info px-1" onclick="peer_view_project(${project.id})" style="cursor: pointer;" title="View"></i></td>
                            <td>${project.created}</td>
                            <td>${project.started}</td>
                            <td>${project.updated}</td>
                            <td>${project.due}</td>
                            <td><span class="badge bg-${STATUS_COLOR[project.status]}">${project.status}</span></td>
                        </tr>
                    `);
                }, 0);
            });
        },
    });
}

function peer_view_project(id) {
    window.localStorage.setItem('project_id', id);
    window.location.href = '/peer/view-project/' + id
}

function get_peer_tasks() {
    $.ajax({
        type: "GET",
        url: "/peer/peer-tasks",
        success: function (response) {
            load_tasks_for_view(response["tasks"]);
        },
    });
}

function updatePeerTaskStatus(task, newStatus) {
    var task = JSON.parse(decodeURIComponent(task))
    $('.modal-dialog span[id="task-name"]').text(task.name);
    if (newStatus === "VERIFY"){
        $('#taskPullRequest').modal('show');
        $('#taskPullRequestForm input[name="task_id"]').val(task.id);
    }else if (newStatus == "CORRECTION") {
        $('#taskCorrection').modal('show');
        $('#taskCorrectionForm input[name="task_id"]').val(task.id);
    }else if (newStatus == "HOLD") {
        $('#taskHold').modal('show');
        $('#taskHoldForm input[name="task_id"]').val(task.id);
    }else{
        updateTaskStatus(task.id, newStatus);
    }
};

function peersortTaskByStatus(status){
    $.ajax({
        type: "POST",
        url: `/peer/sort-tasks-by-status`,
        data: {
            status: status,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            load_tasks_for_view(response["tasks"]);
        },
    });
}


function updateTaskStatus(taskId, newStatus) {
    $.ajax({
        type: "POST",
        url: `/update-task-status`,
        data: {
            status: newStatus,
            taskid: taskId,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            setTaskStatusBadge(taskId, newStatus)
            reload_project_task(response.projectid);
        },
    });
};