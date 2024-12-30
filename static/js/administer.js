fetch_vendors();

function addVendor(){
    $('#addVendorModal').modal('show');
    $('#addVendorModalForm').on('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(this);
        loading()
        $.ajax({
            type: "POST",
            url: "/administer/add-vendor",
            data: {
                vendor_name: formData.get('vendor-name'),
                vendor_email: formData.get('vendor-email'),
                vendor_contact: formData.get('vendor-contact'),
                vendor_password: formData.get('vendor-password'),
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
            },
            success: function(response) {
                window.location.reload();
            }
        });
    })
    $('#createLeadModal').modal('hide');
}

function load_vendors(vendors){
    const vendorsTableBody = $(".vendors_table");
    vendorsTableBody.empty();
    vendors.forEach((vendor, index) => {
        setTimeout(function () {
            let vendorActions;
            if (vendor.status) {
                vendorActions = `
                    <i class="fas fa-user-slash text-warning ms-1" onclick="disable_vendor(${vendor.id})" style="cursor: pointer;" title="Disable"></i>
                `;
            } else{
                vendorActions = `
                    <i class="fas fa-user-check text-success ms-1" onclick="enable_vendor(${vendor.id})" style="cursor: pointer;" title="Enable"></i>
                    <i class="fas fa-trash-alt text-danger ms-1" onclick="delete_vendor(${vendor.id})" style="cursor: pointer;" title="Delete"></i>
                `;
            }
                    
            vendorsTableBody.append(
                `<tr>
                    <td>${vendor.name}</td>
                    <td>${vendor.email}</td>
                    <td>${vendor.phone}</td>
                    <td>Change Password <i class="fas fa-file-alt text-primary me-3 px-1" onclick="view_vendor_password('${vendor.id}')" style="cursor: pointer;" title="View Password"></i></td>
                    <td>${vendorActions}</td>
                </tr>`
            );
        }, 0);
    });
}

function fetch_vendors(){
    $.ajax({
        url: '/administer/get-vendors',
        type: 'GET',
        success: function(response){
            load_vendors(response.vendors);
        },
    });
}

function disable_vendor(vendor_id){
    if(!confirm("Are you sure you want to disable this vendor?")) return;
    $.ajax({
        url: `/administer/disable-vendor`,
        type: 'POST',
        data: {
            vendor_id: vendor_id,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function(response){
            fetch_vendors();
        },
    });
}

function delete_vendor(vendor_id){
    $.ajax({
        url: `/administer/delete-vendor`,
        type: 'POST',
        data: {
            vendor_id: vendor_id,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function(response){
            fetch_vendors();
        },
    });
}

function enable_vendor(vendor_id){
    if(!confirm("Are you sure you want to enable this vendor?")) return;
    $.ajax({
        url: `/administer/enable-vendor`,
        type: 'POST',
        data: {
            vendor_id: vendor_id,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function(response){
            fetch_vendors();
        },
    });
}

function view_vendor_password(vendor_id){
    $('#resetVendorPasswordModal').modal('show');
    $('#resetVendorPasswordModalForm').on('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(this);
        loading()
        $.ajax({
            type: "POST",
            url: "/administer/get-vendor-password",
            data: {
                admin_username: formData.get('admin-username'),
                admin_password: formData.get('admin-password'),
                vendor_id: vendor_id,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
            },
            success: function(response) {
                if(response.status_code == 200){
                    $('#resetVendorPasswordModal').modal('hide');
                    $('#vendorPasswordModal').modal('show');
                    $('#vendorPasswordModalForm').on('submit', function(event) {
                        event.preventDefault();
                        const formData = new FormData(this);
                        if(formData.get('vendor-new-password') != formData.get('vendor-confirm-password')){
                            $('#vendorPasswordModal').modal('hide');
                            $('#alertModal').modal('show');
                            $('#alert-modal-message').text('Passwords do not match');
                            return;
                        }
                        loading()
                        $.ajax({
                            type: "POST",
                            url: "/administer/change-vendor-password",
                            data: {
                                vendor_id: vendor_id,
                                vendor_password: formData.get('vendor-new-password'),
                                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
                            },
                            success: function(response) {
                                loaded()
                                window.location.reload();
                            }
                        });
                    });
                }else{
                    loaded()
                    window.location.reload()
                }
                loaded()
            }
        });
    })
    $('#resetVendorPasswordModal').modal('hide');
}