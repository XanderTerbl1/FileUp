
// =============== Auto Submit On Uploaded ========================//
if (document.getElementById("file-upload"))
    document.getElementById("file-upload").onchange = function () {
        document.getElementById("upload-form").submit();
        console.log("Something happened");
    };

$("#search-submit").click(function () {
    $("#search-form").submit();
});

// =============== Draggable/Droppable Logic  ========================//

$(".draggable").draggable({
    revert: 'invalid',
});

//This class will be added to the 
//droppable class once a valid option has been added
// hoverClass: "drop-hover",

$(".droppable").droppable({
    accept: '.draggable',
    drop: function (event, ui) {
        var is_folder;
        var from_id = ui.draggable[0].id;

        if (from_id.includes("folder")) {
            from_id = from_id.replace("folder-", "");
            is_folder = true;
        } else {
            from_id = from_id.replace("file-", "");
            is_folder = false;
        }
        var to_id = event.target.id;
        to_id = to_id.replace("folder-", "");

        move(from_id, to_id, is_folder);
    }
});


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


// =============== Move Folder/File  ========================//
function move(from_id, to_id, is_folder) {
    console.log("move folder is called!"); // sanity check
    $.ajax({
        url: "/move/" + (is_folder ? "folder" : "file"), // the endpoint
        type: "POST", // http method
        data: { "csrfmiddlewaretoken": getCookie('csrftoken'), "from_id": from_id, "to_id": to_id }, // data sent with the post request

        success: function (response) {
            $('#' + (is_folder ? 'folder' : 'file') + '-' + from_id + '-row').remove();
            console.log(response)
        },

        error: function (xhr, errmsg, err) {
            console.log("folder moving failed...")
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


// =============== Share File/Folder ========================//
function sharePopup(id, is_folder) {
    file_type = is_folder ? "folder" : "file";
    $("#share-cur-id").val(id)
    $("#share-type").val(file_type)

    getUserViewableList(function (response) {
        var users = response.users
        var share_users = $("#share-user-list");
        var user;
        for (var i = 0; i < users.length; i++) {
            user = users[i];
            share_users.append(`            
                <div class="checkbox">
                    <label><input type="checkbox" name='user_ids' value="` + user.id + `">` + user.first_name + ' ' + user.last_name + '  (' + user.email + `)</label>
                </div>
            `);
        }
        getGroupViewableList(function (response) {
            console.log(response);
            $('#shareModal').modal()
        });
    });
}

$('#share-form').on('submit', function (event) {
    event.preventDefault();
    file_type = $("#share-type").val()

    //Get People you should share with
    //Get all groups you should share with

    share(file_type);
});

function share(file_type) {
    console.log("share is working!"); // sanity check
    $.ajax({
        url: "/share", // the endpoint
        type: "POST", // http method
        data: $("#share-form").serialize(), // data sent with the post request

        // handle a successful response
        success: function (response) {
            console.log(response)
            $("#share-user-list").html("");
            $("#share-form")[0].reset()
        },
        // handle a non-successful response
        error: function (xhr, errmsg, err) {
            // $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
            //     " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            // console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            console.log("share failed...")
        }
    });
}
