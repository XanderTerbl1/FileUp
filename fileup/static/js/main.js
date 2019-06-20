// =============== MENU TOGGLE ========================//
$("#menu-toggle").click(function (e) {
    e.preventDefault();
    $("#wrapper").toggleClass("toggled");
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//Auto timeout for alerts - 5 seconds
setTimeout(function () {
    $('#message').fadeOut('slow');
}, 3000);

//Get Quota info displayed on sidenav
$.ajax({
    url: "/accounts/info", // the endpoint
    type: "GET", // http method

    // handle a successful response
    success: function (response) {
        var current_usage = response.quota.current_usage_mb;
        var max_usage = response.quota.max_usage_mb;
        var perc = (current_usage / max_usage) * 100;
        $('#quota-sidebar-progressbar').width(perc + "%");
        $('#quota-sidebar-progressbar').attr("aria-valuenow", perc);
        $("#quota-sidebar-info").html("Used <b>" + current_usage + "mb</b> of <b>" + max_usage + "mb</b>");
    },
    // handle a non-successful response
    error: function (xhr, errmsg, err) {
        // $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
        //     " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
        // console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        console.log("rename failed...")
    }
});