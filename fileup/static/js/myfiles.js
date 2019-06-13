$('#folder-create-form').on('submit', function(event){
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
        success: function (json) {
            //Add the newly created file with the info you got from the request
            
            
            //Reset the form
            $("#folder-create-form")[0].reset()//[0] is workaround since reset() is not part of jquery

            //            
            console.log("Folder Created Successfully");
            console.log(json);
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