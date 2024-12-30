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

document.addEventListener("DOMContentLoaded", function() {
    var selectElement = document.getElementById("project-status-select");
    if (selectElement) {
        addOptionsToSelect(selectElement);
    }
});

function addOptionsToSelect(selectElement) {
    $.ajax({
        url: '/get-project-stages',
        type: 'GET',
        success: function(response){
            response.stages.forEach(function(optionText) {
              var option = document.createElement("option");
              option.id = "id-"+optionText;
              option.textContent = optionText;
              selectElement.appendChild(option);
            });
            set_selected_option()
        }
    });
}

function convertUrlsToLinks(text) {
    const urlPattern = /(https?:\/\/[^\s]+)/g;
    return text.replace(urlPattern, function (url) {
        // Extract the hostname from the URL for display
        let displayText = (new URL(url)).hostname;
        return `<a href="${url}" target="_blank">${displayText}</a>`;
    }).replace(/\n/g, '<br>');
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


// projects
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

function get_project_stages(selectid){
    $.ajax({
        type: "GET",
        url: "/get_project_stages",
        success: function (response) {
            $('#project-status').html(response);
        },
    });
}

function load_projects(projects){
    $(".projects_table_data").empty();
    projects.forEach((project, index) => {
        setTimeout(function () {
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
        }, 0);
    });
}

function get_projects() {
    $.ajax({
        type: "GET",
        url: "/get-projects",
        success: function (response) {
            load_projects(response.projects);
        },
        error: function (xhr, status, error) {
            alert("Failed to retrieve projects. Please try again.");
        }
    });
};

$('#search-projects-list').on('keyup', function() {
    const query = $(this).val();
    if (query) {
        $.ajax({
            type: "GET",
            url: `/search-projects-list/`,
            data: { query: query },
            success: function (response) {
                load_projects(response.projects);
            },
            error: function (error) {
                console.error("Error searching users:", error);
            }
        });
    }
    else{
        get_projects();
    }
});

function sort_project_by_status(status){
    $.ajax({
        type: "POST",
        url: `/sort-projects-by-status`,
        data: {
            status: status,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            load_projects(response.projects);
        },
    });
}