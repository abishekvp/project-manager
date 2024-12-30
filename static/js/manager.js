function load_tasks(tasks){
    const tasksTableBody = $(".project_tasks_table");
    tasksTableBody.empty();
    tasks.forEach((task, index) => {
        setTimeout(function () {
            let taskActions;
            if (task.assigned) {
                taskActions = `
                    <i class="fas fa-user-slash text-warning ms-1" onclick="remove_assigned_peer(${task.id})" style="cursor: pointer;" title="Remove User"></i>
                    <span class="text-success ms-2">${task.assigned}</span>
                `;
            } else {
                taskActions = `
                    <i class="fas fa-trash-alt text-danger me-3 px-1" onclick="delete_task(${task.id})" style="cursor: pointer;" title="Delete"></i>
                    <i class="fa-solid fa-user text-primary me-3 px-1" onclick="open_assign_task_form(${task.id})" style="cursor: pointer;" title="Assign"></i>
                `;
            }

            const statusOptions = `
                <select onchange="update_task_status('${encodeURIComponent(JSON.stringify(task))}', this.value)" class="form-select task-status" id="${task.id}" style="${TASK_STATUS_COLORS[task.status]}">
                    <option value="TODO" ${task.status === 'TODO' ? 'selected' : ''}>TODO</option>
                    <option value="PROGRESS" ${task.status === 'PROGRESS' ? 'selected' : ''}>PROGRESS</option>
                    <option value="VERIFY" ${task.status === 'VERIFY' ? 'selected' : ''}>VERIFY</option>
                    <option value="CORRECTION" ${task.status === 'CORRECTION' ? 'selected' : ''}>CORRECTION</option>
                    <option value="HOLD" ${task.status === 'HOLD' ? 'selected' : ''}>HOLD</option>
                    <option value="COMPLETE" ${task.status === 'COMPLETE' ? 'selected' : ''}>COMPLETE</option>
                </select>
            `;

            tasksTableBody.append(
                `<tr>
                    <td>${task.id}</td>
                    <td>${task.name} <i class="fas fa-file-alt text-primary me-3 px-1" onclick="view_task_details('${task.id}')" style="cursor: pointer;" title="Description"></i></td>
                    <td>${task.created}</td>
                    <td>${task.started}</td>
                    <td>${task.updated}</td>
                    <td>${task.due}</td>
                    <td>${statusOptions}</td>
                    <td>${taskActions}</td>
                </tr>`
            );
        }, 0);
    });
}

function load_tasks_for_view(tasks){
    const tasksTableBody = $(".tasks_table_data");
    $(tasksTableBody).empty();
    tasks.forEach((task, index) => {
        tasksTableBody.append(
            `<tr>
                <td>${task.id}</td>
                <td>${task.name} <i class="fas fa-file-alt text-primary me-3 px-1" onclick="view_task_details('${task.id}')" style="cursor: pointer;" title="Description"></i></td>
                <td>${task.project}</td>
                <td>${task.created}</td>
                <td>${task.started}</td>
                <td>${task.updated}</td>
                <td>${task.due}</td>
                <td><span class="task-status-badge" style="${TASK_STATUS_COLORS[task.status]}">${task.status}</span></td>
                <td>${task.assigned}</td>
            </tr>`
        );
        wait(1000);
    });
}

function assign_task() {
    $.ajax({
        type: "POST",
        url: "/assign-task",
        data: {
            task_id: $('#assignTaskForm input[name="task_id"]').val(),
            user_id: $('#assignTaskForm input[name="user_id"]').val(),
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            reload_project_task(response.project_id);
        },
    });
    $('#assignTaskModal').modal('hide');
}

function remove_assigned_peer(taskid) {
    $('#confirmRemoveAssigned').modal('show');    
    $("#confirmRemoveAssignedBtn").click(function(){
        $.ajax({
            type: "POST",
            url: `/remove-assigned-peer`,
            data: {
                taskid: taskid,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function (response) {
                $('#confirmRemoveAssigned').modal('hide');
                reload_project_task(response.project_id);
            },
        });
    })
}

function create_task(id=NaN){
    if (id){
        $("#search-project").hide()
        $('#projectCreateTask').val(id)
    }
    $('#createTaskModal').modal('show');
    $('#create-task').click(function(){
        var task_name = $('#createTaskModalForm input[name="task-name"]').val()
        var task_description = $('#createTaskModalForm textarea[name="task-description"]').val()
        var task_user = $('#userCreateTask').val()
        var task_due = $('#createTaskModalForm input[name="task-due"]').val()
        $.ajax({
            type: "POST",
            url: `/manager/create-task`,
            data: {
                task_name: task_name,
                task_description: task_description,
                task_user: task_user,
                task_project: $('#projectCreateTask').val(),
                task_due: task_due,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function (response) {
                $('#createTaskModal').modal('hide');
                window.location.reload();
            },
        });
    })
}

function delete_task(taskid) {
    $('#confirmDeleteTask').modal('show');
    $("#confirmDeleteTaskBtn").click(function(){
        $.ajax({
            url: '/delete-task',
            type: 'POST',
            data: {
                taskid: taskid,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function(response){
                $('#confirmDeleteTask').modal('hide');
                reload_project_task(response.projectid);
            },
        });
    })
}

function edit_task(taskid) {
    $('#detailTaskModal').modal('show');
    $('#detailTaskModal').modal('hide');
    $('#detailTaskModalEditName').val($('#detailTaskModalName').text())
    $('#detailTaskModalEditDescription').val($('#detailTaskModalDescription').html())
    $('#detailTaskModalEditProject').text($('#detailTaskModalProject').text())
    $('#detailTaskModalEditAssigned').text($('#detailTaskModalAssigned').text())
    $('#detailTaskModalEditStatus').text($('#detailTaskModalStatus').text())
    $('#detailTaskModalEditDue').val($('#detailTaskModalDue').text())
    $('#detailTaskModalEditPullRequest').val($('#detailTaskModalPullRequest').html())
    $('#detailTaskModalEditCorrection').val($('#detailTaskModalCorrection').html())
    $('#detailTaskModalEditHold').val($('#detailTaskModalHold').html())
    $('#detailTaskModalEditCreated').text($('#detailTaskModalCreated').text())
    $('#detailTaskModalEditStarted').text($('#detailTaskModalStarted').text())
    $('#detailTaskModalEditUpdated').text($('#detailTaskModalUpdated').text())
    $('#detailTaskModalEdit').modal('show');
    $('#edit-task-btn').click(function(){
        $.ajax({
            url: '/update-task',
            type: 'POST',
            data: {
                taskid: taskid,
                name: $('#detailTaskModalEditName').val(),
                description: $('#detailTaskModalEditDescription').val(),
                due: $('#detailTaskModalEditDue').val(),
                pull_request: $('#detailTaskModalEditPullRequest').val(),
                correction: $('#detailTaskModalEditCorrection').val(),
                hold: $('#detailTaskModalEditHold').val(),
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function(response){
                $('#detailTaskModalEdit').modal('hide');
                if(response.redirect){
                    window.location.reload()
                }
            },
        });
    })
}

function update_task_status(task, newStatus){
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

function add_task_correction(){
    $('#taskCorrection').modal('hide');
    $.ajax({
        url: '/add-task-correction',
        type: 'POST',
        data: {
            taskid: $('#taskCorrectionForm input[name="task_id"]').val(),
            correction: $('#taskCorrectionForm textarea[name="taskCorrectionContext"]').val(),
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function(response){
            reload_project_task(response.projectid);
        }
    });
}

function add_task_pull_request() {
    $('#taskPullRequest').modal('hide');
    $.ajax({
        url: '/add-task-pull-request',
        type: 'POST',
        data: {
            taskid: $('#taskPullRequestForm input[name="task_id"]').val(),
            pull_request: $('#taskPullRequestForm textarea[name="taskPullRequestContext"]').val(),
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function(response){
            reload_project_task(response.projectid);
        }
    });
}

function hold_task(){
    $('#taskHold').modal('hide');
    $.ajax({
        url: '/hold-task',
        type: 'POST',
        data: {
            taskid: $('#taskHoldForm input[name="task_id"]').val(),
            reason: $('#taskHoldForm textarea[name="taskHoldReason"]').val(),
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function(response){
            reload_project_task(response.projectid);
        }
    });
}

function edit_task(taskid) {
    $('#detailTaskModal').modal('show');
    $('#detailTaskModal').modal('hide');
    $('#detailTaskModalEditName').val($('#detailTaskModalName').text())
    $('#detailTaskModalEditDescription').val($('#detailTaskModalDescription').html())
    $('#detailTaskModalEditProject').text($('#detailTaskModalProject').text())
    $('#detailTaskModalEditAssigned').text($('#detailTaskModalAssigned').text())
    $('#detailTaskModalEditStatus').text($('#detailTaskModalStatus').text())
    $('#detailTaskModalEditDue').val($('#detailTaskModalDue').text())
    $('#detailTaskModalEditPullRequest').val($('#detailTaskModalPullRequest').html())
    $('#detailTaskModalEditCorrection').val($('#detailTaskModalCorrection').html())
    $('#detailTaskModalEditHold').val($('#detailTaskModalHold').html())
    $('#detailTaskModalEditCreated').text($('#detailTaskModalCreated').text())
    $('#detailTaskModalEditStarted').text($('#detailTaskModalStarted').text())
    $('#detailTaskModalEditUpdated').text($('#detailTaskModalUpdated').text())
    $('#detailTaskModalEdit').modal('show');
    $('#edit-task-btn').click(function(){
        $.ajax({
            url: '/update-task',
            type: 'POST',
            data: {
                taskid: taskid,
                name: $('#detailTaskModalEditName').val(),
                description: $('#detailTaskModalEditDescription').val(),
                due: $('#detailTaskModalEditDue').val(),
                pull_request: $('#detailTaskModalEditPullRequest').val(),
                correction: $('#detailTaskModalEditCorrection').val(),
                hold: $('#detailTaskModalEditHold').val(),
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function(response){
                $('#detailTaskModalEdit').modal('hide');
                if(response.redirect){
                    window.location.reload()
                }
            },
        });
    })
}

// projects
function change_project_status(projectId) {
    const selectedStatus = document.getElementById("project-status-select").value;
    $.ajax({
        type: "POST",
        url: `/change-project-status`,
        data: {
            status: selectedStatus,
            project_id: projectId,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function(response) {
            setProjectStatusBadge(selectedStatus);
        },
        error: function(error) {
            window.location.reload();
        }
    });
}

