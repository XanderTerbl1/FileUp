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

