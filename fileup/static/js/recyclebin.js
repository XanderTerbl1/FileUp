
// =============== Folder Creation  ========================//
function restore(id, is_folder) {
    console.log("restore folder is working!"); // sanity check
    $.ajax({
        url: "/recyclebin/restore/" + (is_folder ? "folder" : "file"), // the endpoint
        type: "POST", // http method
        data: { "id": id, "csrfmiddlewaretoken": getCookie('csrftoken') }, // data sent with the post request

        // handle a successful response
        success: function (file) {
            //Add the newly created file with the info you got from the request   
            $('#' + (is_folder ? 'folder' : 'file') + '-' + file.id + '-row').remove();
            console.log(file)
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