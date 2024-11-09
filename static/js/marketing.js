function loads_maketing_leads(leads){
    console.log(leads)
    const leadsTableBody = $(".marketing_table_data");
    $(leadsTableBody).empty();
    leads.forEach((lead, index) => {
        const statusOptions = `
        <select onchange="update_lead_status('${encodeURIComponent(JSON.stringify(lead))}', this.value)" class="form-select lead-status" id="${lead.id}" style="${LEAD_STATUS_COLORS[lead.status]}">
            <option value="TODO" ${lead.status === 'TODO' ? 'selected' : ''}>TODO</option>
            <option value="IN-PROGRESS" ${lead.status === 'IN-PROGRESS' ? 'selected' : ''}>IN PROGRESS</option>
            <option value="VERIFY" ${lead.status === 'VERIFY' ? 'selected' : ''}>VERIFY</option>
            <option value="CORRECTION" ${lead.status === 'CORRECTION' ? 'selected' : ''}>CORRECTION</option>
            <option value="HOLD" ${lead.status === 'HOLD' ? 'selected' : ''}>HOLD</option>
            <option value="COMPLETE" ${lead.status === 'COMPLETE' ? 'selected' : ''}>COMPLETE</option>
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
}

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
        url: '/get-market-lead-status',
        type: 'GET',
        success: function(response){
            response.stages.forEach(function(optionText) {
                var option = document.createElement("option");
                option.id = "id-"+optionText;
                option.textContent = optionText;
                selectElement.appendChild(option);
            });
            // set_selected_option()
        }
    });
}