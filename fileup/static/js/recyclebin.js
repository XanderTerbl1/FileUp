
// =============== File Restoration  ========================//
function restore(id, is_folder) {
    $.ajax({
        url: "/recyclebin/restore/" + (is_folder ? "folder" : "file"),
        type: "POST",
        data: { "id": id, "csrfmiddlewaretoken": getCookie('csrftoken') },

        success: function (file) {
            $('#' + (is_folder ? 'folder' : 'file') + '-' + file.id + '-row').remove();
        },
        error: handleRequestError
    });
};

// =============== Permanent Deletion ========================//
function perm_delete(id, is_folder) {
    $.ajax({
        url: "/recyclebin/perm_delete/" + (is_folder ? "folder" : "file"),
        type: "POST",
        data: { "id": id, "csrfmiddlewaretoken": getCookie('csrftoken') },

        success: function (response) {
            $('#' + (is_folder ? 'folder' : 'file') + '-' + response.id + '-row').remove();
            loadQuotaInfo();
        },
        error: handleRequestError
    });
};
