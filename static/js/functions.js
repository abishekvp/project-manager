$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^http:.*/.test(settings.url) && !/^https:.*/.test(settings.url)) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

function getCookie(name) {
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

function get_peers() {
    $.ajax({
        type: "POST",
        url: "/get-peers",
        data: {
            peer_name: $('#peer_name').val(),
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            console.log(response['users'])
        },
    });
};

function get_projects() {
    $.ajax({
        type: "GET",
        url: "/get-projects",
        success: function (response) {
            $(".projects_table_data").empty();
            response["projects"].forEach(project => {
                $(".projects_table_data").append(`
                    <tr>
                        <td>${project.id}</td>
                        <td>${project.name}</td>
                        <td>${project.description}</td>
                        <td>${project.created}</td>
                        <td>${project.started}</td>
                        <td>${project.updated}</td>
                        <td>${project.due}</td>
                        <td><span class="badge bg-${STATUS_COLOR[project.status]}">${project.status}</span></td>
                        <td>
                            <i class="fa-solid fa-up-right-from-square text-info px-1" onclick="view_project(${project.id})" style="cursor: pointer;" title="View"></i>
                        </td>
                    </tr>
                `);
            });
        },
        error: function (xhr, status, error) {
            alert("Failed to retrieve projects. Please try again.");
        }
    });
};

function get_tasks(id) {
    const projectId = id; // Get the project ID from your template
    $.ajax({
        type: "GET",
        url: `/get-task-list`, // Assuming your backend supports this URL pattern
        success: function (response) {
            const tasksTableBody = $(".tasks_table_data"); // Assuming you have a table body with this class
            tasksTableBody.empty(); // Clear any existing tasks

            // Loop through the tasks and append them to the table
            response.tasks.forEach((task, index) => {
                let taskActions;
                if (task.assigned) {
                    taskActions = `
                        <i class="fas fa-trash-alt text-danger me-3 px-1" onclick="delete_task(${id}, ${task.id})" style="cursor: pointer;" title="Delete"></i>
                        <span class="text-success">${task.assigned}</span>
                        <i class="fas fa-user-slash text-warning ms-2" onclick="remove_assigned_peer(${task.id})" style="cursor: pointer;" title="Remove User"></i>
                    `;
                } else {
                    taskActions = `
                        <i class="fas fa-trash-alt text-danger me-3 px-1" onclick="delete_task(${id}, ${task.id})" style="cursor: pointer;" title="Delete"></i>
                        <i class="fa-solid fa-user text-primary me-3 px-1" onclick="open_assign_task_form(${task.id})" style="cursor: pointer;" title="Assign"></i>
                    `;
                }

                // Create a select element for task status with dynamic class
                const statusOptions = `
                    <select onchange="updateTaskStatus(${task.id}, this.value)" class="form-select task-status" id="${task.id}" style="${TASK_STATUS_COLORS[task.status]}">
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
        },
        error: function (error) {
            console.error("Error fetching tasks:", error);
        }
    });
}

function sortTaskByStatus(status){
    $.ajax({
        type: "GET",
        url: `/sort-tasks-by-status/${status}`,
        success: function (response) {
            $(".tasks_table_data").empty();
            response["tasks"].forEach((task, index) => {
                setTimeout(function () {
                    $(".tasks_table_data").append(`
                        <tr>
                            <td>${task.id}</td>
                            <td>${task.name} <i class="fas fa-file-alt text-primary me-3 px-1" onclick="view_task_description('${task.description}')" style="cursor: pointer;" title="Description"></i></td>
                            <td>${task.project}</td>
                            <td>${task.created}</td>
                            <td>${task.started}</td>
                            <td>${task.updated}</td>
                            <td>${task.due}</td>
                            <td><span class="px-2 py-1 rounded" style="${TASK_STATUS_COLORS[task.status]}">${task.status}</span></td>
                            <td>${task.assigned}</td>
                        </tr>
                    `);
                }, index * 50);
            });
        },
    });
}

// Function to remove the assigned user
function remove_assigned_peer(taskId) {
    var remove = confirm("Are you sure you want to remove the assigned user?");
    if (!remove) {
        return;
    }
    $.ajax({
        type: "POST",
        url: `/lead/remove-assigned-peer`,
        data: {
            taskid: taskId,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            get_tasks(response.project_id); // Refresh the tasks list after unassignment
        },
        error: function (error) {
            console.error("Error removing assigned user:", error);
        }
    });
}

function updateTaskStatus(taskId, newStatus) {
    $.ajax({
        type: "POST",
        url: `/update-task-status`, // Assuming your backend supports this URL pattern
        data: {
            status: newStatus,
            taskid: taskId,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            setTaskStatusBadge(taskId, newStatus)
            get_tasks(response.projectid);
        },
    });
};

function delete_project(id) {
    const confirmation = confirm("Are you sure you want to delete this project?");
    if (confirmation) {
        window.location.href = "/lead/delete-project/" + id
    };
};

function delete_task(pid, tid) {
    const confirmation = confirm("Are you sure you want to delete this task?");
    if (confirmation) {
        window.location.href = "/lead/delete-task/" + pid +"/"+ tid
    };
}

function convertUrlsToLinks(text) {
    const urlPattern = /(https?:\/\/[^\s]+)/g;
    return text
        .replace(urlPattern, '<a href="$1" target="_blank">$1</a>')
        .replace(/\n/g, '<br>');
}

function view_task_details(taskid) {
    $.ajax({
        type: "GET",
        url: `/task-detail/`,
        data: { taskid: taskid },
        success: function (response) {
            var myModal = new bootstrap.Modal(document.getElementById('detailTaskModal'));
            myModal.show();
            document.getElementById('detailTaskModalDescription').innerHTML = convertUrlsToLinks(response.task.description);
        },
        error: function (error) {
            console.error("Error searching users:", error);
        }
    });
}

function view_project(id) {
    $.ajax({
        type: "POST",
        url: `/view-project`,
        data: {
            projectid: id,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            window.location.href = response.url;
        },
    });
}

$('#user-search-input').on('keyup', function() {
    const query = $(this).val();
    if (query.length > 2) {  // Trigger search when input has more than 2 characters
        $.ajax({
            type: "GET",
            url: `/search-users/`,
            data: { query: query },
            success: function (response) {
                const searchResults = $('#user-search-results');
                searchResults.empty();  // Clear previous search results

                response.users.forEach(user => {
                    searchResults.append(
                        `<li class="list-group-item" onclick="selectUser(${user.id}, '${user.username}')">
                            ${user.username}
                        </li>`
                    );
                });
            },
            error: function (error) {
                console.error("Error searching users:", error);
            }
        });
    }
});

function selectUser(userId, username) {
    $('#assignTaskForm input[name="user_id"]').val(userId);
    $('#user-search-input').val(username);
    $('#user-search-results').empty();
}

function create_task(id) {
    const form = document.getElementById('taskForm');
    
    // Gather the form data
    const formData = new FormData(form);
    formData.append('project_id', id); // Append the project ID if needed

    // Submit the form data via AJAX
    fetch('/manager/create-task', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        window.location.reload()
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function changeProjectStatus(projectId) {
    const selectedStatus = document.getElementById("project-status-select").value;
    $.ajax({
        type: "POST",
        url: `/lead/change-project-status/${projectId}/`,
        data: {
            'status': selectedStatus,
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

function assign_task() {
    const form = document.getElementById('assignTaskForm');
    const formData = new FormData(form);
    $.ajax({
        type: "POST",
        url: "/assign-task",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            get_tasks(response.project_id);
            $('#assignTaskModal').modal('hide');
        },
        error: function (error) {
            console.error("Error assigning task:", error);
        }
    });
}

function assign_project() {
    const form = document.getElementById('assignProjectForm');
    const formData = new FormData(form);
    $.ajax({
        type: "POST",
        url: "/lead/assign-project",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            get_tasks(response.project_id);
            $('#assignProjectModal').modal('hide');
        },
        error: function (error) {
            console.error("Error assigning task:", error);
        }
    });
}

function remove_project_manager(projectid){
    const confirmation = confirm("Are you sure you want to remove the project manager?");
    if (confirmation) {
        $.ajax({
            type: "POST",
            url: `/lead/remove-project-manager`,
            data: {
                projectid: projectid,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function (response) {
                location.reload();
            },
        });
    }
}

$('#manager-search-input').on('keyup', function() {
    const query = $(this).val();
    if (query.length > 2) {  // Trigger search when input has more than 2 characters
        $.ajax({
            type: "GET",
            url: `/lead/search-manager/`,
            data: { query: query },
            success: function (response) {
                const searchResults = $('#manager-search-results');
                searchResults.empty();
                response.managers.forEach(manager => {
                    searchResults.append(
                        `<li class="list-group-item" onclick="selectManager(${manager.id}, '${manager.username}')">
                            ${manager.username}
                        </li>`
                    );
                });
            },
            error: function (error) {
                console.error("Error searching users:", error);
            }
        });
    }
});

function selectManager(managerid, username) {
    $('#assignProjectForm input[name="manager_id"]').val(managerid);
    $('#manager-search-input').val(username);
    $('#manager-search-results').empty();
}

function view_tasks() {
    $.ajax({
        type: "GET",
        url: "/get-task-list",
        success: function (response) {
            $(".tasks_table_data").empty();
            response["tasks"].forEach((task, index) => {
                setTimeout(function () {
                    $(".tasks_table_data").append(`
                        <tr>
                            <td>${task.id}</td>
                            <td>${task.name} <i class="fas fa-file-alt text-primary me-3 px-1" onclick="view_task_description('${task.description}')" style="cursor: pointer;" title="Description"></i></td>
                            <td>${task.project}</td>
                            <td>${task.created}</td>
                            <td>${task.started}</td>
                            <td>${task.updated}</td>
                            <td>${task.due}</td>
                            <td><span class="px-2 py-1 rounded" style="${TASK_STATUS_COLORS[task.status]}">${task.status}</span></td>
                            <td>${task.assigned}</td>
                        </tr>
                    `);
                }, index * 50);
            });
        },
    });
};

function load_members() {
    $.ajax({
        type: "GET",
        url: "/lead/view-members",
        success: function (response) {
            // Clear the inactive users table and populate it
            $(".inactives_table_data").empty();
            response["inactives"].forEach((user, index) => {
                setTimeout(function () {
                    $(".inactives_table_data").append(`
                        <tr>
                            <td>${user.id}</td>
                            <td style="text-transform: capitalize;">${user.username}</td>
                            <td>${user.email}</td>
                            <td>${user.role}</td>
                            <td>
                                <i class="fas fa-check-circle text-success me-3 px-1" onclick="approve_user(${user.id})" style="cursor: pointer;" title="Approve"></i>
                                <i class="fas fa-trash-alt text-danger px-1" onclick="delete_user(${user.id})" style="cursor: pointer;" title="Remove"></i>
                            </td>
                        </tr>
                    `);
                }, index * 50);
            });
            // Clear the leads table and populate it
            $(".leads_table_data").empty();
            response["leads"].forEach((user, index) => {
                setTimeout(function () {
                    $(".leads_table_data").append(`
                        <tr>
                            <td>${user.id}</td>
                            <td style="text-transform: capitalize;">${user.username}</td>
                            <td>${user.email}</td>
                            <td>
                                <i class="fas fa-user-alt-slash text-danger me-3 px-1" onclick="inactive_user(${user.id})" style="cursor: pointer;" title="Delete"></i>
                            </td>
                        </tr>
                    `);
                }, index * 50);
            });
            $(".managers_table_data").empty();
            response["managers"].forEach((user, index) => {
                setTimeout(function () {
                    $(".managers_table_data").append(`
                        <tr>
                            <td>${user.id}</td>
                            <td style="text-transform: capitalize;">${user.username}</td>
                            <td>${user.email}</td>
                            <td>
                                <i class="fas fa-user-alt-slash text-danger me-3 px-1" onclick="inactive_user(${user.id})" style="cursor: pointer;" title="Delete"></i>
                            </td>
                        </tr>
                    `);
                }, index * 50);
            });
            // Clear the peers table and populate it
            $(".peers_table_data").empty();
            response["peers"].forEach((user, index) => {
                setTimeout(function () {
                    $(".peers_table_data").append(`
                        <tr>
                            <td>${user.id}</td>
                            <td style="text-transform: capitalize;">${user.username}</td>
                            <td>${user.email}</td>
                            <td>
                                <i class="fas fa-user-alt-slash text-danger me-3 px-1" onclick="inactive_user(${user.id})" style="cursor: pointer;" title="Delete"></i>
                            </td>
                        </tr>
                    `);
                }, index * 50);
            });
        },
    });
}

function get_peer_projects() {
    $.ajax({
        type: "GET",
        url: "/peer/view-projects",
        success: function (response) {
            $(".projects_table_data").empty();
            response["projects"].forEach(project => {
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
            });
        },
    });
}

function peer_view_project(id) {
    window.localStorage.setItem('project_id', id);
    window.location.href = '/peer/view-project/' + id
}

function peer_view_tasks() {
    $.ajax({
        type: "GET",
        url: "/peer/peer-tasks",
        success: function (response) {
            $(".peer_tasks_table_data").empty();
            response["tasks"].forEach((task, index) => {
                setTimeout(function () {
                    const statusOptions = `
                        <select onchange="updatePeerTaskStatus(${task.id}, this.value)" class="form-select task-status" id="${task.id}" style="${TASK_STATUS_COLORS[task.status]}">
                            <option value="TODO" ${task.status === 'TODO' ? 'selected' : ''}>TODO</option>
                            <option value="IN-PROGRESS" ${task.status === 'IN-PROGRESS' ? 'selected' : ''}>IN PROGRESS</option>
                            <option value="VERIFY" ${task.status === 'VERIFY' ? 'selected' : ''}>VERIFY</option>
                            <option value="CORRECTION" ${task.status === 'CORRECTION' ? 'selected' : ''}>CORRECTION</option>
                            <option value="HOLD" ${task.status === 'HOLD' ? 'selected' : ''}>HOLD</option>
                            <option value="COMPLETE" ${task.status === 'COMPLETE' ? 'selected' : ''}>COMPLETE</option>
                        </select>
                    `;
                    $(".peer_tasks_table_data").append(`
                        <tr>
                            <td>${task.id}</td>
                            <td>${task.name} <i class="fas fa-file-alt text-primary me-3 px-1" onclick="view_task_description('${task.description}')" style="cursor: pointer;" title="Description"></i></td>
                            <td>${task.project}</td>
                            <td>${task.created}</td>
                            <td>${task.started}</td>
                            <td>${task.updated}</td>
                            <td>${task.due}</td>
                            <td>${statusOptions}</td>
                        </tr>
                    `);
                }, index * 50); // Delay each task by 200ms (adjust as needed)
            });
        },
    });
}

function updatePeerTaskStatus(taskId, newStatus) {
    $.ajax({
        type: "POST",
        url: `/peer/update-task-status`,
        data: {
            status: newStatus,
            taskid: taskId,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            setTaskStatusBadge(taskId, newStatus)
            peer_view_tasks();
        },
    });
};

function test_mail_server() {
    var formData = new FormData(document.getElementById('mail-server-form'));
    if (formData.get('to_mail') === '') {
        alert("Please enter a valid email address to test the mail server.");
        return;
    }
    $.ajax({
        type: "POST",
        url: "/lead/test-mail-server",
        data: {
            'smtp_server': formData.get('smtp_server'),
            'smtp_port': formData.get('smtp_port'),
            'username': formData.get('username'),
            'password': formData.get('password'),
            'from_mail': formData.get('from_mail'),
            'to_mail': formData.get('to_mail'),
            'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            alert(response.message)
        },
        error: function (error) {
            alert(error.responseJSON.message)
        }
    });
};

function delete_user(id) {
    confirm("Are you sure you want to delete this user?");
    if (!confirm) {
        return;
    }
    $.ajax({
        type: "POST",
        url: `/lead/delete-user`,
        data: {
            userid: id,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            load_members()
        },
    });
}

function inactive_user(id) {
    confirm("Are you sure you want to inactive this user?");
    if (!confirm) {
        return;
    }
    $.ajax({
        type: "POST",
        url: `/lead/inactive-user`,
        data: {
            userid: id,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            load_members()
        },
    });
}

function approve_user(id) {
    $.ajax({
        type: "POST",
        url: `/lead/approve-user`,
        data: {
            userid: id,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            load_members()
        },
    });
}