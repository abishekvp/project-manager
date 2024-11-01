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

// Function to remove the assigned user
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
                get_project_tasks(response.project_id);
            },
        });
    })
}

function delete_project(id) {
    $('#confirmDeleteProject').modal('show');
    $("#confirmDeleteProjectBtn").click(function(){
        $.ajax({
            type: "POST",
            url: `/delete-project`,
            data: {
                project_id: id,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function (response) {
                $('#confirmDeleteProject').modal('hide');
                window.location.href = "/lead/projects";
            },
        });
    })
};

function convertUrlsToLinks(text) {
    const urlPattern = /(https?:\/\/[^\s]+)/g;
    return text.replace(urlPattern, function (url) {
        // Extract the hostname from the URL for display
        let displayText = (new URL(url)).hostname;
        return `<a href="${url}" target="_blank">${displayText}</a>`;
    }).replace(/\n/g, '<br>');
}

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

$('#search-project-input').on('keyup', function() {
    const query = $(this).val();
    if (query.length > 2) {  // Trigger search when input has more than 2 characters
        $.ajax({
            type: "GET",
            url: `/search-projects/`,
            data: { query: query },
            success: function (response) {
                const searchResults = $('#search-project-results');
                searchResults.empty();  // Clear previous search results

                response.projects.forEach(project => {
                    searchResults.append(
                        `<li class="list-group-item" id="${project.id}" onclick="selectProjectForCreateTask(${project.id}, '${project.name}')">
                            ${project.name}
                        </li>`
                    );
                });
            },
            error: function (error) {
                console.error("Error searching users:", error);
            }
        });
    }
})

function selectProjectForCreateTask(project_id, project_name){
    $('#projectCreateTask').val(project_id);
    $('#search-project-input').val(project_name);
    $('#search-project-results').empty();
}

$('#search-user-input').on('keyup', function() {
    const query = $(this).val();
    if (query.length > 2) {  // Trigger search when input has more than 2 characters
        $.ajax({
            type: "GET",
            url: `/search-users/`,
            data: { query: query },
            success: function (response) {
                const searchResults = $('#search-user-results');
                searchResults.empty();  // Clear previous search results

                response.users.forEach(user => {
                    searchResults.append(
                        `<li class="list-group-item" onclick="selectUserForCreateTask(${user.id}, '${user.username}')">
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
})

function selectUserForCreateTask(userid, username){
    $('#userCreateTask').val(userid);
    $('#search-user-input').val(username);
    $('#search-user-results').empty();
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