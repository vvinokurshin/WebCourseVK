$(".like").on("click", function () {
    const request = new Request(
        'http://127.0.0.1:8000/like/',
        {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
            },
            body: "essence=" + $(this).data('essence') + "&id=" + $(this).data("id"),

        }
    )

    fetch(request).then(
        response_raw => response_raw.json().then(
            response_json => {
                $(this).parent().find("button.dislike").attr("data-count", response_json.raiting);
                toastr.options = {
                    "closeButton": true, "debug": false, "newestOnTop": true,
                    "progressBar": true, "positionClass": "toast-bottom-right", "preventDuplicates": true,
                    "onclick": null, "showDuration": "300", "hideDuration": "1000", "timeOut": "5000",
                    "extendedTimeOut": "1000", "showEasing": "swing", "hideEasing": "linear",
                    "showMethod": "fadeIn", "hideMethod": "fadeOut"
                };
                response_json.messages.forEach(msg => toastr.info(msg));
            }

        )
    );
})

$(".dislike").on("click", function () {
    const request = new Request(
        'http://127.0.0.1:8000/dislike/',
        {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
            },
            body: "essence=" + $(this).data('essence') + "&id=" + $(this).data("id"),

        }
    )

    fetch(request).then(
        response_raw => response_raw.json().then(
            response_json => {
                $(this).attr("data-count", response_json.raiting);
                toastr.options = {
                    "closeButton": true, "debug": false, "newestOnTop": true,
                    "progressBar": true, "positionClass": "toast-bottom-right", "preventDuplicates": true,
                    "onclick": null, "showDuration": "300", "hideDuration": "1000", "timeOut": "5000",
                    "extendedTimeOut": "1000", "showEasing": "swing", "hideEasing": "linear",
                    "showMethod": "fadeIn", "hideMethod": "fadeOut"
                };
                response_json.messages.forEach(msg => toastr.info(msg));
            }

        )
    );
})

$(".form-check-input").on("click", function () {
    const request = new Request(
        'http://127.0.0.1:8000/correct_answer/',
        {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
            },
            body: "answer_id=" + $(this).data("answer_id")
        }
    )

    fetch(request).then(
        response_raw => response_raw.json().then(
            response_json => {
                if (response_json.status == 'true') {
                    $(this).attr("checked", "checked");
                    $(this).prop("checked", true);
                } else {
                    $(this).prop("checked", false);
                    $(this).removeAttr("checked");
                }

                var prev = $("div").find("#" + response_json.prev_correct).find(".form-check-input");
                prev.removeAttr("checked");
                prev.prop("checked", false);

                toastr.options = {
                    "closeButton": true, "debug": false, "newestOnTop": true,
                    "progressBar": true, "positionClass": "toast-bottom-right", "preventDuplicates": true,
                    "onclick": null, "showDuration": "300", "hideDuration": "1000", "timeOut": "5000",
                    "extendedTimeOut": "1000", "showEasing": "swing", "hideEasing": "linear",
                    "showMethod": "fadeIn", "hideMethod": "fadeOut"
                };
                response_json.messages.forEach(msg => toastr.info(msg));
            }

        )
    );
})