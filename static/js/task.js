// function load_project_tasks(tasks){
//     const tasksTableBody = $(".project_tasks_table");
//     tasksTableBody.empty();
//     tasks.forEach((task, index) => {
//         let taskActions;
//         if (task.assigned) {
//             taskActions = `
//                 <i class="fas fa-user-slash text-warning ms-1" onclick="remove_assigned_peer(${task.id})" style="cursor: pointer;" title="Remove User"></i>
//                 <span class="text-success ms-2">${task.assigned}</span>
//             `;
//         } else {
//             taskActions = `
//                 <i class="fas fa-trash-alt text-danger me-3 px-1" onclick="delete_task(${task.id})" style="cursor: pointer;" title="Delete"></i>
//                 <i class="fa-solid fa-user text-primary me-3 px-1" onclick="open_assign_task_form(${task.id})" style="cursor: pointer;" title="Assign"></i>
//             `;
//         }

//         const statusOptions = `
//             <select onchange="update_task_status('${encodeURIComponent(JSON.stringify(task))}', this.value)" class="form-select task-status" id="${task.id}" style="${TASK_STATUS_COLORS[task.status]}">
//                 <option value="TODO" ${task.status === 'TODO' ? 'selected' : ''}>TODO</option>
//                 <option value="PROGRESS" ${task.status === 'PROGRESS' ? 'selected' : ''}>PROGRESS</option>
//                 <option value="VERIFY" ${task.status === 'VERIFY' ? 'selected' : ''}>VERIFY</option>
//                 <option value="CORRECTION" ${task.status === 'CORRECTION' ? 'selected' : ''}>CORRECTION</option>
//                 <option value="HOLD" ${task.status === 'HOLD' ? 'selected' : ''}>HOLD</option>
//                 <option value="COMPLETE" ${task.status === 'COMPLETE' ? 'selected' : ''}>COMPLETE</option>
//             </select>
//         `;

//         tasksTableBody.append(
//             `<tr>
//                 <td>${task.id}</td>
//                 <td>${task.name} <i class="fas fa-file-alt text-primary me-3 px-1" onclick="view_task_details('${task.id}')" style="cursor: pointer;" title="Description"></i></td>
//                 <td>${task.created}</td>
//                 <td>${task.started}</td>
//                 <td>${task.updated}</td>
//                 <td>${task.due}</td>
//                 <td>${statusOptions}</td>
//                 <td>${taskActions}</td>
//             </tr>`
//         );
//     });
// }

function view_task_details(taskid) {
    $.ajax({
        type: "GET",
        url: `/task-detail/`,
        data: { taskid: taskid },
        success: function (response) {
            var myModal = new bootstrap.Modal(document.getElementById('detailTaskModal'));
            myModal.show();
            $('#detailTaskModalName').text(response.task.name);
            $('#edit-task-btn').attr('id', response.task.id);
            $('#detailTaskModalDescription').html(convertUrlsToLinks(response.task.description));
            $('#detailTaskModalProject').text(response.task.project);
            $('#detailTaskModalAssigned').text(response.task.assigned);
            $('#detailTaskModalStatus').text(response.task.status);
            $('#detailTaskModalDue').text(response.task.due);
            if (response.task.pull_request){
                $('#detailTaskModalPullRequest').html(convertUrlsToLinks(response.task.pull_request));
            }
            if (response.task.correction){
                $('#detailTaskModalCorrection').html(convertUrlsToLinks(response.task.correction));
            }
            if (response.task.reason){
                $('#detailTaskModalHold').html(convertUrlsToLinks(response.task.reason));
            }
            $('#detailTaskModalCreated').text(response.task.created);
            $('#detailTaskModalStarted').text(response.task.started);
            $('#detailTaskModalUpdated').text(response.task.updated);
        },
        error: function (error) {
            console.error("Error searching users:", error);
        }
    });
}

function sortTaskByStatus(status){
    $.ajax({
        type: "POST",
        url: `/sort-tasks-by-status`,
        data: {
            status: status,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            load_tasks_for_view(response.tasks);
        },
    });
}

function get_tasks(){
    $.ajax({
        url: '/get-tasks-list',
        type: 'GET',
        success: function(response){
            load_tasks_for_view(response.tasks);
        }
    });
}

$('#search-task').on('keyup', function() {
    const query = $(this).val();
    if (query) {  // Trigger search when input has more than 2 characters
        $.ajax({
            type: "GET",
            url: `/search-task/`,
            data: { query: query },
            success: function (response) {
                load_tasks_for_view(response.tasks);
            },
            error: function (error) {
                console.error("Error searching users:", error);
            }
        });
    }
    else{
        get_tasks();
    }
});

function reload_project_task(projectid){
    $.ajax({
        url: '/get-project-tasks',
        type: 'POST',
        data: {
            projectid: projectid,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function(response){
            load_tasks(response['tasks']);
        },
    });
}

function reload_project_task_with_localstorage(){
    const projectid = window.localStorage.getItem('project_id');
    reload_project_task(projectid);
}