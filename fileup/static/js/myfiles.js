// =============== Auto Submit On Uploaded ========================//
document.getElementById("file-upload").onchange = function () {
    document.getElementById("upload-form").submit();
    console.log("Something happened");
};

// =============== Rename Folder ========================//
function renamePopup(folder_id) {
    $("#rename-cur-folder-id").val(folder_id)
    $('#renameFolderModel').modal()
}

$('#folder-rename-form').on('submit', function (event) {
    event.preventDefault();
    rename_folder();
});

function rename_folder() {
    console.log("rename folder is working!"); // sanity check
    $.ajax({
        url: $('#folder-rename-form').attr('action'), // the endpoint
        type: "POST", // http method
        data: $("#folder-rename-form").serialize(), // data sent with the post request

        // handle a successful response
        success: function (file) {
            //Check if file or folder - assuming folder now.
            $("#folder-" + file.id + "-name").html(file.name);
            $("#folder-rename-form")[0].reset()
        },
        // handle a non-successful response
        error: function (xhr, errmsg, err) {
            // $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
            //     " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            // console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            console.log("folder rename failed...")
        }
    });
}

// =============== Folder Creation  ========================//
$('#folder-create-form').on('submit', function (event) {
    event.preventDefault();
    console.log("form submitted!")  // sanity check
    create_folder();
});

function create_folder() {
    console.log("create folder is working!"); // sanity check
    console.log($('#folder-create-form').attr('action')); // sanity check
    $.ajax({
        url: $('#folder-create-form').attr('action'), // the endpoint
        type: "POST", // http method
        data: $("#folder-create-form").serialize(), // data sent with the post request

        // handle a successful response
        success: function (folder) {
            //Add the newly created file with the info you got from the request    
            console.log(folder)
            $("#file-view-body").prepend(`
                <tr>s
                <td>
                    <a href="/folders/` + folder.pk + `">
                        <i class="fas fa-folder"></i>
                        ` + folder.fields.name + ` </a>
                </td>
                <td>folder</td>
                <td>me</td>
                <td>just now</td>
                <td> - </td>
                <td> <i class="fas fa-ellipsis-v"></i></td>
            </tr>`
            );

            $("#folder-create-form")[0].reset()
        },
        // handle a non-successful response
        error: function (xhr, errmsg, err) {
            // $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
            //     " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            // console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            console.log("folder creation failed...")
        }
    });
};

// =============== Delete Folder  ========================//
function delete_folder(folder_id) {
    console.log("delete folder is called!"); // sanity check
    $.ajax({
        url: "/delete_folder", // the endpoint
        type: "POST", // http method
        data: { "id": folder_id }, // data sent with the post request

        success: function (folder) {
            console.log(folder)
        },

        error: function (xhr, errmsg, err) {
            console.log("folder creation failed...")
        }
    });
};