// =============== Auto Submit On Uploaded ========================//
document.getElementById("file-upload").onchange = function () {
    document.getElementById("upload-form").submit();
    console.log("Something happened");
};


// =============== Folder Creation AJAX ========================//
$('#folder-create-form').on('submit', function (event) {
    event.preventDefault();
    console.log("form submitted!")  // sanity check
    create_folder();
});

function create_folder() {
    console.log("create folder is working!") // sanity check
    $.ajax({
        url: "create_folder", // the endpoint
        type: "POST", // http method
        data: $("#folder-create-form").serialize(), // data sent with the post request

        // handle a successful response
        success: function (folder) {
            //Add the newly created file with the info you got from the request            
            $("#file-view-body").prepend(`
                <tr>
                <td>
                    <a href="index.html">
                        <i class="fas fa-folder"></i>
                        ` + folder.name + ` </a>
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