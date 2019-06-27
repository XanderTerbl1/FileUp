// =============== Auto Submit On Uploaded ========================//
if (document.getElementById("file-upload"))
    document.getElementById("file-upload").onchange = function () {
        document.getElementById("upload-form").submit();
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



// =============== Move Folder/File  ========================//
function move(from_id, to_id, is_folder) {
    console.log("move folder is called!"); // sanity check
    $.ajax({
        url: "/move/" + (is_folder ? "folder" : "file"), // the endpoint
        type: "POST", // http method
        data: { "csrfmiddlewaretoken": getCookie('csrftoken'), "from_id": from_id, "to_id": to_id }, // data sent with the post request

        success: function (response) {
            $('#' + (is_folder ? 'folder' : 'file') + '-' + from_id + '-row').remove();
            var msg = "Moved '" + response['from_name'] + "' to '" + response["to_name"] + "'";
            displayAlert(msg, "success");
        },

        error: function (xhr, errmsg, err) {
            displayAlert(xhr.responseJSON["msg"], "danger", 10 * 1000);
            $('#' + (is_folder ? 'folder' : 'file') + '-' + from_id).removeAttr("style");
        }
    });
};


// =============== Rename Folder ========================//
function renamePopup(id, is_folder) {
    file_type = is_folder ? "folder" : "file";
    cur_name = $("#" + file_type + "-" + id + "-name").html();
    $("#rename-cur-id").val(id)
    $("#rename-name").val(cur_name)
    $("#rename-type").val(file_type)
    $('#renameModal').modal('show')
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
            $('#renameModal').modal('hide')
        },
        // handle a non-successful response
        error: function (xhr, errmsg, err) {
            displayAlert(err + ": " + err, "danger", 10 * 1000)
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
    $.ajax({
        url: '/create_folder', // the endpoint
        type: "POST", // http method
        data: $("#folder-create-form").serialize(), // data sent with the post request

        // handle a successful response
        success: function (response) {
            folder_href = (response.shared ? "/shared/content/view/" : "/folders/")
            $("#file-view-body").prepend(`
        <tr id="folder-` + response.folder.pk + `-row" class="file-row">
            <td>
                <a href="` + folder_href + response.folder.pk + `" class="droppable draggable ui-draggable ui-draggable-handle ui-droppable" id="folder-` + response.folder.pk + `" style="position: relative;">
                     <i class="fas fa-folder"></i>
                    <span id="folder-` + response.folder.pk + `-name">` + response.folder.fields.name + `</span>
                </a>
            </td>
            <td>folder
            </td>
            <td>` + 'me' + `</td>
            <td>just now</td>
            <td>-</td>
            <td>
                <div class="dropleft">
                    <button type="button" class="btn float-right" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><i class="fas fa-ellipsis-v"></i></button>
                    <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">
                        <a class="dropdown-item" onclick="renamePopup('` + response.folder.pk + `',true)">Rename folder</a>
                        <a class="dropdown-item" onclick="remove('` + response.folder.pk + `', true)">Remove folder</a>
                        <div class="dropdown-divider"></div>
                        <a class="dropdown-item" onclick="sharePopup('` + response.folder.pk + `',true)">Share folder</a>
                        <a class="dropdown-item" onclick="publish('` + response.folder.pk + `', true)">Create Public Link</a>
                    </div>
                </div>
            </td>
        </tr>    
            `);

            $("#folder-create-form")[0].reset()
            $('#createFolderModel').modal('hide')
        },
        // handle a non-successful response
        error: function (xhr, errmsg, err) {
            displayAlert(err + ": " + err, "danger", 10 * 1000)
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
            var msg = "'" + file.name + "' moved to recycle bin";
            displayAlert(msg, "success", 5 * 1000);
        },

        error: function (xhr, errmsg, err) {
            displayAlert(err + ": " + err, "danger", 10 * 1000)
        }
    });
};

// =============== Publish Folder/File  ========================//
function publish(id, is_folder) {
    $.ajax({
        url: "/publish/" + (is_folder ? "folder" : "file"), // the endpoint
        type: "POST", // http method
        data: { "id": id, "csrfmiddlewaretoken": getCookie('csrftoken') }, // data sent with the post request

        success: function (response) {
            // $('#' +  + '-' + file.id + '-row').remove();            
            var msg = (is_folder ? 'Folder' : 'File') + " public view link: <a href='" + response.rel_path + "'>" + response.access_link + "</a>";
            displayAlert(msg, "success", 20 * 1000);
        },

        error: function (xhr, errmsg, err) {
            displayAlert(err + ": " + err, "danger", 10 * 1000)
        }
    });
};


// =============== Share File/Folder ========================//
function sharePopup(id, is_folder) {
    file_type = is_folder ? "folder" : "file";
    $("#share-cur-id").val(id)
    $("#share-type").val(file_type)

    // Get the users/group that the file is already shared with
    getSharedUsers(id, file_type, function (response) {
        user_participants = response.users;
        group_participants = response.groups;

        // Get all the other users as well
        getUserViewableList(function (response) {
            var users = response.users
            var share_users = $("#share-user-list");
            share_users.html("")
            var user;
            for (var i = 0; i < users.length; i++) {
                user = users[i];

                //Is the file already shared with the user.
                var checked = "";
                for (var j = 0; j < user_participants.length; j++) {
                    if (user_participants[j].id == user.id) {
                        checked = "checked";
                        break;
                    }
                }

                share_users.append(`            
                    <div class="checkbox">
                        <label><input ` + checked + ` type="checkbox" name='user_ids[]' value="` + user.id + `">` + user.first_name + ' ' + user.last_name + '  (' + user.email + `)</label>
                    </div>
                `);
            }
            if (user.length == 0) {
                share_users.html('<p>No users to share folder with</p>');
            }

            //Get all the other groups 
            getGroupViewableList(function (response) {
                var groups = response.groups
                var share_groups = $("#share-group-list");
                share_groups.html("")
                var group;

                for (var i = 0; i < groups.length; i++) {
                    group = groups[i];

                    //Is the file already shared with the group.
                    var checked = "";
                    for (var j = 0; j < group_participants.length; j++) {
                        if (group_participants[j].name == group.name) {
                            checked = "checked";
                            break;
                        }
                    }

                    share_groups.append(`            
                    <div class="checkbox">
                        <label><input ` + checked + ` type="checkbox" name='group_ids[]' value="` + group.name + `">` + group.name + `</label>
                    </div>
                    `);
                    //Show the populated popup after group and user items where fetched.
                }
                if (groups.length == 0) {
                    share_groups.html('<p>You are not part of any groups</p>');
                }
                $('#shareModal').modal()
            });
        });
    });
}

$('#share-form').on('submit', function (event) {
    event.preventDefault();
    share();
});

function share() {
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
            $('#shareModal').modal('hide')
        },
        // handle a non-successful response
        error: function (xhr, errmsg, err) {
            displayAlert(err + ": " + err, "danger", 10 * 1000)
        }
    });
}
