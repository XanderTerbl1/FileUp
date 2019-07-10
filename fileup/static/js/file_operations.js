// =============== Auto Submit On Uploaded ========================//
if (document.getElementById("file-upload"))
    document.getElementById("file-upload").onchange = function () {
        document.getElementById("upload-form").submit();
    };

//Drag to upload 
function drag_drop(event) {
    event.preventDefault();
    document.querySelector('#file-upload').files = event.dataTransfer.files;
    document.getElementById("upload-form").submit();
}


//================== Search Submit =================================/

$("#search-submit").click(function () {
    $("#search-form").submit();
});

// =============== Draggable/Droppable Logic  ========================//
$(".draggable").draggable({
    revert: 'invalid',
});

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
    $.ajax({
        url: "/move/" + (is_folder ? "folder" : "file"),
        type: "POST",
        data: {
            "csrfmiddlewaretoken": getCookie('csrftoken'),
            "from_id": from_id,
            "to_id": to_id
        },

        success: function (response) {
            // Remove Item and Display Success message
            $('#' + (is_folder ? 'folder' : 'file') + '-' + from_id + '-row').remove();
            var msg = "Moved '" + response['from_name'] + "' to '" + response["to_name"] + "'";
            displayAlert(msg, "success");
        },

        error: function (xhr, errmsg, err) {
            handleRequestError(xhr, errmsg, err);
            //Reset the moved item's position
            $('#' + (is_folder ? 'folder' : 'file') + '-' + from_id).removeAttr("style");
        }
    });
};


// =============== Rename Folder ========================//
function renamePopup(id, is_folder) {
    file_type = is_folder ? "folder" : "file";
    cur_name = $("#" + file_type + "-" + id + "-name").html();
    // Set relevant fields
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
    $.ajax({
        url: "/rename/" + file_type,
        type: "POST",
        data: $("#rename-form").serialize(),


        success: function (file) {
            //Rename File/Folder 
            $("#" + file_type + "-" + file.id + "-name").html(file.name);

            $("#rename-form")[0].reset()
            $('#renameModal').modal('hide')
        },

        error: handleRequestError
    });
}

// =============== Ajax Folder Creation  ========================//
// $('#folder-create-form').on('submit', function (event) {
//     event.preventDefault();
//     create_folder();
// });

// function create_folder() {
//     $.ajax({
//         url: '/create_folder',
//         type: "POST",
//         data: $("#folder-create-form").serialize(),


//         success: function (response) {
//             //Create the folder and populate html. 
//             folder_href = (response.shared ? "/shared/content/view/" : "/folders/")
//             $("#file-view-body").prepend(`
//         <tr id="folder-` + response.folder.pk + `-row" class="file-row">
//             <td>
//                 <a href="` + folder_href + response.folder.pk + `" class="droppable draggable ui-draggable ui-draggable-handle ui-droppable" id="folder-` + response.folder.pk + `" style="position: relative;">
//                      <i class="fas fa-folder"></i>
//                     <span id="folder-` + response.folder.pk + `-name">` + response.folder.fields.name + `</span>
//                 </a>
//             </td>
//             <td>folder
//             </td>
//             <td>` + 'me' + `</td>
//             <td>just now</td>
//             <td>-</td>
//             <td>
//                 <div class="dropleft">
//                     <button type="button" class="btn float-right" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><i class="fas fa-ellipsis-v"></i></button>
//                     <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">
//                         <a class="dropdown-item" onclick="renamePopup('` + response.folder.pk + `',true)">Rename folder</a>
//                         <a class="dropdown-item" onclick="remove('` + response.folder.pk + `', true)">Remove folder</a>
//                         <div class="dropdown-divider"></div>
//                         <a class="dropdown-item" onclick="sharePopup('` + response.folder.pk + `',true)">Share folder</a>
//                         <a class="dropdown-item" onclick="publish('` + response.folder.pk + `', true)">Create Public Link</a>
//                     </div>
//                 </div>
//             </td>
//         </tr>    
//             `);

//             $("#folder-create-form")[0].reset()
//             $('#createFolderModel').modal('hide')
//         },

//         error: handleRequestError
//     });
// };


// =============== Remove Folder/File  ========================//
function remove(id, is_folder) {
    $.ajax({
        url: "/remove/" + (is_folder ? "folder" : "file"),
        type: "POST",
        data: {
            "id": id,
            "csrfmiddlewaretoken": getCookie('csrftoken')
        },

        success: function (file) {
            // Remove From Html as well
            $('#' + (is_folder ? 'folder' : 'file') + '-' + file.id + '-row').remove();
            //Display success msg
            var msg = "'" + file.name + "' moved to recycle bin";
            displayAlert(msg, "success", 5 * 1000);
        },

        error: handleRequestError
    });
};

// =============== Publish Folder/File  ========================//
function publish(id, is_folder) {
    $.ajax({
        url: "/publish/" + (is_folder ? "folder" : "file"),
        type: "POST",
        data: {
            "id": id,
            "csrfmiddlewaretoken": getCookie('csrftoken')
        },

        success: function (response) {
            var msg = (is_folder ? 'Folder' : 'File') + " public view link: <a href='" + response.rel_path + "'>" + response.access_link + "</a>";
            displayAlert(msg, "success", 20 * 1000);
        },

        error: handleRequestError
    });
};

function unpublish(id, is_folder) {
    $.ajax({
        url: "/unpublish/" + (is_folder ? "folder" : "file"),
        type: "POST",
        data: {
            "id": id,
            "csrfmiddlewaretoken": getCookie('csrftoken')
        },

        success: function (response) {
            var msg = (is_folder ? 'Folder' : 'File') + " public link removed.";
            displayAlert(msg, "success", 20 * 1000);
        },

        error: handleRequestError
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

                //Add the user to the list 
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

                    //Add the group to the list 
                    share_groups.append(`            
                    <div class="checkbox">
                        <label><input ` + checked + ` type="checkbox" name='group_ids[]' value="` + group.name + `">` + group.name + `</label>
                    </div>
                    `);
                }
                if (groups.length == 0) {
                    share_groups.html('<p>You are not part of any groups</p>');
                }

                // Show populated popup
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
    console.log("share is working!");
    $.ajax({
        url: "/share",
        type: "POST",
        data: $("#share-form").serialize(),


        success: function (response) {
            console.log(response)
            $("#share-user-list").html("");
            $("#share-form")[0].reset()
            $('#shareModal').modal('hide')
        },

        error: handleRequestError
    });
}
