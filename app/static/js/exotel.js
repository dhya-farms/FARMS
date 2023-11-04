function trigger_call(submission_type, post_id, call_from, call_to, caller_id, call_in_progress_api, exotel_call_endpoint){
    var exotel_call_button = document.getElementById('exotel_call_button');
    exotel_call_button.disabled = true;
    exotel_call_button.innerHTML = "Calling...";
    var original_color = exotel_call_button.style.background;
    exotel_call_button.style.background = "red";
    django.jQuery.ajax({
        type: "GET",
        url: call_in_progress_api,
        success: function (call_in_progress) {
            console.log(call_in_progress);
            if(!call_in_progress){
                django.jQuery.ajax({
                    type: "GET",
                    url: exotel_call_endpoint +"?submission_type="+submission_type+"&post_id="+post_id+"&from="+call_from+"&to="+call_to+"&caller_id="+caller_id,
                    success: function (data) {
                        console.log(data);
                        response = JSON.parse(data);
                        console.log(response["Call"]["Status"]);
                        exotel_call_button.style.background = "green";
                        exotel_call_button.innerHTML = response["Call"]["Status"];
                    },
                    error: function (xhr, status, error) {
                        console.log(xhr);
                        alert(xhr['responseText']);
                        console.log(status);
                        console.log(error);
                        exotel_call_button.style.background = original_color;
                        exotel_call_button.innerHTML = "Retry calling";
                        exotel_call_button.disabled = false;
                    },
                    complete: function(){
                        console.log("Complete calls");
                    }
                });
            }else{
                alert("Your another call in progress. Please complete it before calling.");
                exotel_call_button.style.background = original_color;
                exotel_call_button.innerHTML = "Retry calling";
                exotel_call_button.disabled = false;
            }
        },
        error: function (xhr, status, error) {
            console.log(xhr);
            alert(xhr['responseText']);
            console.log(status);
            console.log(error);
            exotel_call_button.style.background = original_color;
            exotel_call_button.innerHTML = "Retry calling";
            exotel_call_button.disabled = false;
        },
        complete: function(){
            console.log("Complete calls");
        }
    });

}


function refresh_exotel_status(endpoint, submission_type, post_id, call_from, call_to, caller_id, call_in_progress_api,
                                exotel_call_endpoint){
    console.log("refresh_exotel_status");
    var refresh_exotel_status_button = document.getElementById('refresh_exotel_status_button');
    refresh_exotel_status_button.disabled = true;
    refresh_exotel_status_button.innerHTML = "Refreshing...";
    django.jQuery.ajax({
        type: "GET",
        url: endpoint,
        success: function (data) {
            console.log(data);
            for(var key in data) {
                document.getElementsByClassName("field-"+key)[0].getElementsByTagName("div")[1].innerHTML = data[key];
                if(key === "exotel_last_call_status"){
                    if(!(data[key] === "IN_PROGRESS")){
                        document.getElementsByClassName("field-call_via_exotel")[0].getElementsByTagName("div")[1].innerHTML =
                        '<button id="exotel_call_button" class="button" '+
                        'onclick="trigger_call('+submission_type+', '+post_id+', \''+call_from+'\',\''+call_to+'\',\''+caller_id+'\',\''+call_in_progress_api+'\',\''+exotel_call_endpoint+'\');"'+
                        'target="_blank">Call the client</button>';
                    }
                }
            }
        },
        error: function (xhr, status, error) {
            alert("Error in Refresh");
            console.log(xhr);
            console.log(status);
            console.log(error);
        },
        complete: function(){
            refresh_exotel_status_button.innerHTML = "Refresh";
            refresh_exotel_status_button.disabled = false;
        }
    });
}
