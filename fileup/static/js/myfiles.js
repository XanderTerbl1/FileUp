// =============== Auto Submit On Uploaded ========================//
document.getElementById("file-upload").onchange = function () {
    document.getElementById("upload-form").submit();
    console.log("Something happened");
};

// =============== Rename Folder ========================//
function renamePopup(id, is_folder) {
    file_type = is_folder ? "folder" : "file";
    cur_name = $("#" + file_type + "-" + id + "-name").html();
    $("#rename-cur-id").val(id)
    $("#rename-name").val(cur_name)
    $("#rename-type").val(file_type)
    $('#renameModal').modal()
}

$('#rename-form').on('submit', function (event) {
    event.preventDefault();
    file_type = $("#rename-type").val()
    rename(file_type);
});

function rename(file_type) {
    console.log("rename is working!"); // sanity check
    $.ajax({
        url: "/rename/" + file_type, // the endpoint
        type: "POST", // http method
        data: $("#rename-form").serialize(), // data sent with the post request

        // handle a successful response
        success: function (file) {
            //Check if file or folder - assuming folder now.
            $("#" + file_type + "-" + file.id + "-name").html(file.name);
            $("#rename-form")[0].reset()
        },
        // handle a non-successful response
        error: function (xhr, errmsg, err) {
            // $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
            //     " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            // console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            console.log("rename failed...")
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

// =============== Remove Folder/File  ========================//
function remove(id, is_folder) {
    console.log("delete folder is called!"); // sanity check
    $.ajax({
        url: "/remove/" + (is_folder ? "folder" : "file"), // the endpoint
        type: "POST", // http method
        data: { "id": id, "csrfmiddlewaretoken": getCookie('csrftoken') }, // data sent with the post request

        success: function (file) {
            $('#' + (is_folder ? 'folder' : 'file') + '-' + file.id + '-row').remove();
            console.log(file)
        },

        error: function (xhr, errmsg, err) {
            console.log("folder deletion failed...")
        }
    });
};

// =============== Publish Folder/File  ========================//
function publish(id, is_folder) {
    console.log("delete folder is called!"); // sanity check
    $.ajax({
        url: "/publish/" + (is_folder ? "folder" : "file"), // the endpoint
        type: "POST", // http method
        data: { "id": id, "csrfmiddlewaretoken": getCookie('csrftoken') }, // data sent with the post request

        success: function (response) {
            // $('#' + (is_folder ? 'folder' : 'file') + '-' + file.id + '-row').remove();
            alert("Public view at " + response.access_link)
        },

        error: function (xhr, errmsg, err) {
            console.log("folder deletion failed...")
        }
    });
};