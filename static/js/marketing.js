function loads_maketing_leads(leads){
    const leadsTableBody = $(".marketing_table_data");
    $(leadsTableBody).empty();
    leads.forEach((lead, index) => {
        setTimeout(function () {
            const statusOptions = `
                <select onchange="update_lead_status('${encodeURIComponent(JSON.stringify(lead.id))}', this.value)" class="form-select lead-status" id="${lead.id}" style="${LEAD_STATUS_COLORS[lead.status]}">
                <option value="ACTIVE" ${lead.status === 'ACTIVE' ? 'selected' : ''}>ACTIVE</option>
                <option value="HOT" ${lead.status === 'HOT' ? 'selected' : ''}>HOT</option>
                <option value="COLD" ${lead.status === 'COLD' ? 'selected' : ''}>COLD</option>
                <option value="CLIENT" ${lead.status === 'CLIENT' ? 'selected' : ''}>CLIENT</option>
                <option value="INACTIVE" ${lead.status === 'INACTIVE' ? 'selected' : ''}>INACTIVE</option>
            </select>`;
            
            leadsTableBody.append(
                `<tr>
                    <td>${lead.id}</td>
                    <td>${lead.client_name} <i class="fas fa-file-alt text-primary me-3 px-1" onclick="lead_details('${lead.id}')" style="cursor: pointer;" title="Description"></i></td>
                    <td>${lead.client_email}</td>
                    <td>${lead.client_contact}</td>
                    <td>${lead.created}</td>
                    <td>${lead.updated}</td>
                    <td>${statusOptions}</td>
                </tr>`
            );
        }, 0);
    });   
}

function update_lead_status(lead, status){
    $.ajax({
        type: "POST",
        url: "/marketing/update-lead-status",
        data: {
            lead: lead,
            status: status,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
        },
        success: function(response) {
            window.location.reload();
        }
    });
}

function create_market_lead(){
    $('#createLeadModal').modal('show');
    $('#createLeadModalForm').on('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(this);
        loading()
        $.ajax({
            type: "POST",
            url: "/marketing/create-market-leads",
            data: {
                client_name: formData.get('client-name'),
                client_email: formData.get('client-email'),
                client_contact: formData.get('client-contact'),
                notes: formData.get('notes'),
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
            },
            success: function(response) {
                loaded()
                window.location.reload();
            }
        });
    })
    $('#createLeadModal').modal('hide');
}

function get_marketing_leads(){
    $.ajax({
        type: "GET",
        url: "/marketing/view-market-leads",
        success: function(response) {
            loads_maketing_leads(response.leads)
        }
    });
    
}

function sort_leads_by_status(status){
    $.ajax({
        type: "GET",
        url: "/marketing/sort-market-leads",
        data: {
            status: status
        },
        success: function(response) {
            loads_maketing_leads(response.leads)
        }
    });
}

$('#search-market-leads').on('keyup', function() {
    const term = $(this).val();
    if (term) {
        $.ajax({
            type: "GET",
            url: `/marketing/search-market-leads/`,
            data: { term: term },
            success: function (response) {
                loads_maketing_leads(response.leads);
            },
        });
    }
    else{
        get_marketing_leads();
    }
});

function lead_details(lead_id){
    $.ajax({
        type: "GET",
        url: `/marketing/get-market-lead`,
        data: {
            lead_id: lead_id
        },
        success: function(response) {
            $('#leadDetailsModal').modal('show');
            $('#leadDetailsModalForm input[name="client-name"]').val(response.lead.client_name);
            $('#leadDetailsModalForm input[name="client-email"]').val(response.lead.client_email);
            $('#leadDetailsModalForm input[name="client-email"]').val(response.lead.client_email);
            $('#leadDetailsModalForm input[name="client-contact"]').val(response.lead.client_contact);
            $('#leadDetailsModalForm textarea[name="notes"]').val(response.lead.notes);
            $('#createLeadModalForm').on('submit', function(event) {
                event.preventDefault();
                const formData = new FormData(this);
                loading()
                $.ajax({
                    type: "POST",
                    url: "/marketing/update-market-lead",
                    data: formData,
                    success: function(response) {
                        loaded()
                        window.location.reload();
                    }
                });
            })
        }
    });
}

document.addEventListener("DOMContentLoaded", function() {
    var selectElement = document.getElementById("market-lead-status-select");
    if (selectElement) {
        add_lead_status_option(selectElement);
    }
});

function add_lead_status_option(selectElement) {
    $.ajax({
        url: '/marketing/get-market-lead-status',
        type: 'GET',
        success: function(response){
            response.status.forEach(function(optionText) {
                var option = document.createElement("option");
                option.id = "id-"+optionText;
                option.textContent = optionText;
                selectElement.appendChild(option);
            });
            // set_selected_option()
        }
    });
}