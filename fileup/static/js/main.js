// =============== MENU TOGGLE ========================//
$("#menu-toggle").click(function (e) {
    e.preventDefault();
    $("#wrapper").toggleClass("toggled");
});

// =============== Auto Submit On Uploaded ========================//
document.getElementById("file-upload").onchange = function() {
    document.getElementById("upload-form").submit();
    console.log("Something happened");
};