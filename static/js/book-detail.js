$(document).on('confirmation', '.remodal', function () {
    var book_id = $('#isbn').attr('b_id')
    $.ajax({
        url: "/book/checkbook/" + book_id,
        type: "GET",
        success: function (data) {
            if (data["status"] === 200) {
                $("#operation_info").html(data['msg']).css("color", "red")
                window.location.href = "/book/addgift/" + book_id
            } else if (data["status"] === 400) {
                $("#operation_info").html(data['msg']).css("color", "green")
            } else if (data["status"] === 401) {
                window.location.href = "/user/login/"
            }
        }
    })
});