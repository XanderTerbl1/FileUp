$(document).ready(function () {
    setAlertTimeOut();
    loadQuotaInfo();
});


function handleRequestError(xhr, errmsg, err) {
    var msg = ""
    if ('msg' in xhr.responseJSON) {
        msg = xhr.responseJSON['msg']
    }
    msg += "\n(" + err + " (" + errmsg + "))"
    displayAlert(msg, "danger", 1000 * 10)
}


//=============== Alerts ==============================
var cur_alert;
function displayAlert(text, type, time = 3000) {
    /*
    The alert will be appended to #page-content-wrapper
    Which is defined in the base.html
     */
    var alert = `
    <div id="message" class="container fixed-top">
        <div class="alert alert-${type}" alert-dismissible role="alert">
            <button class="close" type="button" data-dismiss="alert"><span aria-hidden="true">&times;</span></button>
            <strong>
                ${text}
            </strong>
        </div>
    </div>
    `
    $("#page-content-wrapper").append(alert);
    setAlertTimeOut(time);
}

function setAlertTimeOut(time = 3000) {
    clearTimeout(cur_alert);
    cur_alert = setTimeout(function () {
        $('#message').fadeOut('slow');
    }, time);
}


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

function loadQuotaInfo() {
    $.ajax({
        url: "/accounts/quota_info", // the endpoint
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
        error: handleRequestError
    });
}

/*
Gets a list of all users. 
Would be used when attempting to share folders/files

This approach would never work/be practical in a bigger setting than CS Staff group.
But since that is the scale of the assignment this would be a valid approach
*/
function getUserViewableList(callback) {
    $.ajax({
        url: "/accounts/users/all", // the endpoint
        type: "GET", // http method

        // handle a successful response
        success: function (response) {
            callback(response);
        },
        // handle a non-successful response
        error: handleRequestError
    });
}
function getGroupViewableList(callback) {
    $.ajax({
        url: "/accounts/groups/all", // the endpoint
        type: "GET", // http method

        // handle a successful response
        success: function (response) {
            callback(response);
        },
        // handle a non-successful response
        error: handleRequestError
    });
}

//Gets a list of all the users that a certain file/folder
//has been shared with
function getSharedUsers(file_id, file_type, callback) {
    $.ajax({
        url: "/shared/participants/" + file_id,
        type: "POST", // http method
        data: {
            "file_type": file_type,
            "csrfmiddlewaretoken": getCookie('csrftoken')
        },

        // handle a successful response
        success: function (response) {
            console.log(response)
            callback(response);
        },
        // handle a non-successful response
        error: handleRequestError
    });
}