function load_project_tasks(tasks){
    const tasksTableBody = $(".project_tasks_table");
    tasksTableBody.empty();
    tasks.forEach((task, index) => {
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
                <option value="IN-PROGRESS" ${task.status === 'IN-PROGRESS' ? 'selected' : ''}>IN PROGRESS</option>
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
    });
}

function add_task(id) {
    const form = document.getElementById('taskForm');
    const formData = new FormData(form);
    formData.append('project_id', id);
    $.ajax({
        url: '/create-task',
        type: 'POST',
        data: formData,
        success: function(response){
            $('#addTaskModal').modal('hide');
            reload_project_task(response.project_id);
        },
    });
    // fetch('/create-task', {
    //     method: 'POST',
    //     body: formData,
    // })
    // .then(data => {
    //     response = data.json()
    //     alert(response["project_id"])
    // })
}