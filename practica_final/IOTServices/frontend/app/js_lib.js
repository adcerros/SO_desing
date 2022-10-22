/*
 * Javascript file to implement client side usability for 
 * Operating Systems Desing exercises.
 */
 var api_server_address = "http://34.141.35.215:5001/"
 var ROOMS_NUMBER = 40
 var rooms_state = new Array(ROOMS_NUMBER)

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

 var get_current_sensor_data = function(){
    $.getJSON( api_server_address+"device_state", function( data ) {
        $.each(data, function( index, item ) {
          $("#"+item.room).data(item.type, item.value)
            if (item.type == "room-state"){
                if (item.value == "1" || item.value== 1){
                    if (item.room.length < 6){
                    rooms_state[item.room.slice(item.room.length - 1)] = "1"
                    }
                    else{
                        rooms_state[item.room.slice(item.room.length - 2)] = "1"
                    }
                }
                else{
                    if (item.room.length < 6){
                    rooms_state[item.room.slice(item.room.length - 1)] = "0"
                    }
                    else{
                        rooms_state[item.room.slice(item.room.length - 2)] = "0"
                    }
                }
            }
        });
    });
}


var draw_rooms = function(){
    $("#rooms").empty()
    var room_index = 1;
    for (var i = 0; i < 8; i++) {
        $("#rooms").append("<tr id='floor"+i+"'></tr>")
        for (var j = 0; j < 5; j++) {
                $("#floor"+i).append("\
                <td \
                data-bs-toggle='modal' \
                data-bs-target='#room_modal' \
                class='room_cell'\
                id='Room"+room_index+"'\
                > \
                Room "+room_index+"\
                </td>"
                )
            room_index++
        }
    }
}


function updateRooms (){
    $("#rooms").empty()
    var room_index = 1;
    for (var i = 0; i < 8; i++) {
        $("#rooms").append("<tr id='floor"+i+"'></tr>")
        for (var j = 0; j < 5; j++) {
            if (rooms_state[room_index] == "1"){
                $("#floor"+i).append("\
                <td \
                data-bs-toggle='modal' \
                data-bs-target='#room_modal' \
                class=''\
                style='background-color: yellowgreen' \
                id='Room"+room_index+"'\
                > \
                Room "+room_index+"\
                </td>"
                )
            }
            else{
                $("#floor"+i).append("\
                <td \
                data-bs-toggle='modal' \
                data-bs-target='#room_modal' \
                class='room_cell'\
                id='Room"+room_index+"'\
                > \
                Room "+room_index+"\
                </td>"
                )
            }
            room_index++
        }
    }
}

$("#air_conditioner_mode").change(function(){
    var value = $(this).val()
    $.ajax({
        type: "POST",
        url: api_server_address+"device_state",
        data: JSON.stringify({
            "room":$("#room_id").text(),
            "type":"air-conditioner-mode",
            "value":value,
        }),
        contentType: 'application/json'
    });
})

$("#indoor_light_active").change(function(){
    var value = $(this).val()
    $.ajax({
        type: "POST",
        url: api_server_address+"device_state",
        data: JSON.stringify({
            "room":$("#room_id").text(),
            "type":"indoor-light-active",
            "value":value,
        }),
        contentType: 'application/json'
    });
})

$("#indoor_light_level").change(function(){
    var value = $(this).val()
    $.ajax({
        type: "POST",
        url: api_server_address+"device_state",
        data: JSON.stringify({
            "room":$("#room_id").text(),
            "type":"indoor-light-level",
            "value":value,
        }),
        contentType: 'application/json'
    });
})

$("#outside_light_active").change(function(){
    var value = $(this).val()
    $.ajax({
        type: "POST",
        url: api_server_address+"device_state",
        data: JSON.stringify({
            "room":$("#room_id").text(),
            "type":"outside-light-active",
            "value":value,
        }),
        contentType: 'application/json'
    });
})

$("#outside_light_level").change(function(){
    var value = $(this).val()
    $.ajax({
        type: "POST",
        url: api_server_address+"device_state",
        data: JSON.stringify({
            "room":$("#room_id").text(),
            "type":"outside-light-level",
            "value":value,
        }),
        contentType: 'application/json'
    });
})


$("#blind_active").change(function(){
    var value = $(this).val()
    $.ajax({
        type: "POST",
        url: api_server_address+"device_state",
        data: JSON.stringify({
            "room":$("#room_id").text(),
            "type":"blind-active",
            "value":value,
        }),
        contentType: 'application/json'
    });
})

$("#blind_level").change(function(){
    var value = $(this).val()
    $.ajax({
        type: "POST",
        url: api_server_address+"device_state",
        data: JSON.stringify({
            "room":$("#room_id").text(),
            "type":"blind-level",
            "value":value,
        }),
        contentType: 'application/json'
    });
})

function recolor(rooms_ilumination){
   $("#rooms").empty()
    var room_index = 1;
    for (var i = 0; i < 8; i++) {
        $("#rooms").append("<tr id='floor"+i+"'></tr>")
        for (var j = 0; j < 5; j++) {
            if (rooms_ilumination[room_index] == "1"){
                $("#floor"+i).append("\
                <td \
                data-bs-toggle='modal' \
                data-bs-target='#room_modal' \
                class=''\
                style='background-color: yellowgreen' \
                id='Room"+room_index+"'\
                > \
                Room "+room_index+"\
                </td>"
                )
            }
            else{
                $("#floor"+i).append("\
                <td \
                data-bs-toggle='modal' \
                data-bs-target='#room_modal' \
                class='room_cell'\
                id='Room"+room_index+"'\
                > \
                Room "+room_index+"\
                </td>"
                )
            }
            room_index++
        }
    }
    sleep(100)
}

$("#rooms_layout_btn").click(function(){
    var value = $("#rooms_layout").val()
    var rooms_ilumination = new Array(40)
    for(let i = 0; i < 40; i++){
        rooms_ilumination[i] = "0"
    }
    if (value == "a" || value == "A") {
        rooms_ilumination[13] = "1"
        rooms_ilumination[17] = "1"
        rooms_ilumination[21] = "1"
        rooms_ilumination[26] = "1"
        rooms_ilumination[31] = "1"
        rooms_ilumination[22] = "1"
        rooms_ilumination[23] = "1"
        rooms_ilumination[24] = "1"
        rooms_ilumination[25] = "1"
        rooms_ilumination[19] = "1"
        rooms_ilumination[30] = "1"
        rooms_ilumination[35] = "1"
    } else if (value == "e" || value == "E") {
        rooms_ilumination[11] = "1"
        rooms_ilumination[12] = "1"
        rooms_ilumination[13] = "1"
        rooms_ilumination[14] = "1"
        rooms_ilumination[15] = "1"
        rooms_ilumination[16] = "1"
        rooms_ilumination[21] = "1"
        rooms_ilumination[26] = "1"
        rooms_ilumination[31] = "1"
        rooms_ilumination[32] = "1"
        rooms_ilumination[33] = "1"
        rooms_ilumination[34] = "1"
        rooms_ilumination[35] = "1"
        rooms_ilumination[22] = "1"
        rooms_ilumination[23] = "1"
        rooms_ilumination[24] = "1"
        rooms_ilumination[25] = "1"
    } else if (value == "i" || value == "I") {
        rooms_ilumination[11] = "1"
        rooms_ilumination[12] = "1"
        rooms_ilumination[13] = "1"
        rooms_ilumination[14] = "1"
        rooms_ilumination[15] = "1"
        rooms_ilumination[18] = "1"
        rooms_ilumination[23] = "1"
        rooms_ilumination[28] = "1"
        rooms_ilumination[33] = "1"
        rooms_ilumination[31] = "1"
        rooms_ilumination[32] = "1"
        rooms_ilumination[34] = "1"
        rooms_ilumination[35] = "1"
    } else if (value == "o" || value == "O") {
        rooms_ilumination[12] = "1"
        rooms_ilumination[13] = "1"
        rooms_ilumination[14] = "1"
        rooms_ilumination[19] = "1"
        rooms_ilumination[16] = "1"
        rooms_ilumination[17] = "1"
        rooms_ilumination[21] = "1"
        rooms_ilumination[26] = "1"
        rooms_ilumination[27] = "1"
        rooms_ilumination[32] = "1"
        rooms_ilumination[33] = "1"
        rooms_ilumination[34] = "1"
        rooms_ilumination[29] = "1"
        rooms_ilumination[20] = "1"
        rooms_ilumination[25] = "1"
        rooms_ilumination[30] = "1"
    } else if (value == "u" || value == "U") {
        rooms_ilumination[11] = "1"
        rooms_ilumination[15] = "1"
        rooms_ilumination[16] = "1"
        rooms_ilumination[21] = "1"
        rooms_ilumination[26] = "1"
        rooms_ilumination[27] = "1"
        rooms_ilumination[32] = "1"
        rooms_ilumination[33] = "1"
        rooms_ilumination[34] = "1"
        rooms_ilumination[29] = "1"
        rooms_ilumination[20] = "1"
        rooms_ilumination[25] = "1"
        rooms_ilumination[30] = "1"
    } else if (value == "d" || value == "D") {
        rooms_ilumination[11] = "1"
        rooms_ilumination[12] = "1"
        rooms_ilumination[13] = "1"
        rooms_ilumination[14] = "1"
        rooms_ilumination[19] = "1"
        rooms_ilumination[16] = "1"
        rooms_ilumination[21] = "1"
        rooms_ilumination[26] = "1"
        rooms_ilumination[31] = "1"
        rooms_ilumination[32] = "1"
        rooms_ilumination[33] = "1"
        rooms_ilumination[34] = "1"
        rooms_ilumination[29] = "1"
        rooms_ilumination[20] = "1"
        rooms_ilumination[25] = "1"
        rooms_ilumination[30] = "1"
    } else if (value == "c" || value == "C") {
        rooms_ilumination[12] = "1"
        rooms_ilumination[13] = "1"
        rooms_ilumination[14] = "1"
        rooms_ilumination[15] = "1"
        rooms_ilumination[16] = "1"
        rooms_ilumination[17] = "1"
        rooms_ilumination[21] = "1"
        rooms_ilumination[26] = "1"
        rooms_ilumination[27] = "1"
        rooms_ilumination[32] = "1"
        rooms_ilumination[33] = "1"
        rooms_ilumination[34] = "1"
        rooms_ilumination[35] = "1"
    } else if (value == "p" || value == "P") {
        rooms_ilumination[11] = "1"
        rooms_ilumination[12] = "1"
        rooms_ilumination[13] = "1"
        rooms_ilumination[14] = "1"
        rooms_ilumination[15] = "1"
        rooms_ilumination[16] = "1"
        rooms_ilumination[21] = "1"
        rooms_ilumination[26] = "1"
        rooms_ilumination[31] = "1"
        rooms_ilumination[20] = "1"
        rooms_ilumination[25] = "1"
        rooms_ilumination[24] = "1"
        rooms_ilumination[23] = "1"
        rooms_ilumination[22] = "1"
        rooms_ilumination[28] = "1"
        rooms_ilumination[34] = "1"
    } else if (value == "j" || value == "J") {
        rooms_ilumination[11] = "1"
        rooms_ilumination[12] = "1"
        rooms_ilumination[13] = "1"
        rooms_ilumination[14] = "1"
        rooms_ilumination[15] = "1"
        rooms_ilumination[18] = "1"
        rooms_ilumination[23] = "1"
        rooms_ilumination[28] = "1"
        rooms_ilumination[32] = "1"
        rooms_ilumination[26] = "1"
    } else if (value == "r" || value == "R") {
        rooms_ilumination[11] = "1"
        rooms_ilumination[12] = "1"
        rooms_ilumination[13] = "1"
        rooms_ilumination[14] = "1"
        rooms_ilumination[15] = "1"
        rooms_ilumination[16] = "1"
        rooms_ilumination[21] = "1"
        rooms_ilumination[26] = "1"
        rooms_ilumination[31] = "1"
        rooms_ilumination[20] = "1"
        rooms_ilumination[25] = "1"
        rooms_ilumination[24] = "1"
        rooms_ilumination[23] = "1"
        rooms_ilumination[22] = "1"
    } else if (value == "l" || value == "L") {
        rooms_ilumination[11] = "1"
        rooms_ilumination[16] = "1"
        rooms_ilumination[21] = "1"
        rooms_ilumination[26] = "1"
        rooms_ilumination[31] = "1"
        rooms_ilumination[32] = "1"
        rooms_ilumination[33] = "1"
        rooms_ilumination[34] = "1"
        rooms_ilumination[35] = "1"
    } else if (value == "n" || value == "N") {
        rooms_ilumination[11] = "1"
        rooms_ilumination[16] = "1"
        rooms_ilumination[21] = "1"
        rooms_ilumination[26] = "1"
        rooms_ilumination[31] = "1"
        rooms_ilumination[17] = "1"
        rooms_ilumination[23] = "1"
        rooms_ilumination[29] = "1"
        rooms_ilumination[35] = "1"
        rooms_ilumination[30] = "1"
        rooms_ilumination[25] = "1"
        rooms_ilumination[20] = "1"
        rooms_ilumination[15] = "1"
    } else if (value == "s" || value == "S") {
        rooms_ilumination[11] = "1"
        rooms_ilumination[16] = "1"
        rooms_ilumination[21] = "1"
        rooms_ilumination[22] = "1"
        rooms_ilumination[23] = "1"
        rooms_ilumination[24] = "1"
        rooms_ilumination[25] = "1"
        rooms_ilumination[30] = "1"
        rooms_ilumination[35] = "1"
        rooms_ilumination[34] = "1"
        rooms_ilumination[33] = "1"
        rooms_ilumination[32] = "1"
        rooms_ilumination[31] = "1"
        rooms_ilumination[12] = "1"
        rooms_ilumination[13] = "1"
        rooms_ilumination[14] = "1"
        rooms_ilumination[15] = "1"
    } else if (value == "t" || value == "T") {
        rooms_ilumination[11] = "1"
        rooms_ilumination[12] = "1"
        rooms_ilumination[13] = "1"
        rooms_ilumination[14] = "1"
        rooms_ilumination[15] = "1"
        rooms_ilumination[18] = "1"
        rooms_ilumination[23] = "1"
        rooms_ilumination[28] = "1"
        rooms_ilumination[33] = "1"
    } else if (value == "v" || value == "V") {
        rooms_ilumination[11] = "1"
        rooms_ilumination[16] = "1"
        rooms_ilumination[21] = "1"
        rooms_ilumination[27] = "1"
        rooms_ilumination[33] = "1"
        rooms_ilumination[29] = "1"
        rooms_ilumination[25] = "1"
        rooms_ilumination[20] = "1"
        rooms_ilumination[15] = "1"
    }
    recolor(rooms_ilumination)
   $("#rooms_layout").val("")
})


$("#rooms").on("click", "td", function() {
    $("#room_id").text($( this ).attr("id") || "");
    $("#temperature_value").text($( this ).data("temperature") || "");
    $("#presence_value").text($( this ).data("presence") || "0");
    $("#air_conditioner_value").text($( this ).data("air-level") || "");
    $("#air_conditioner_mode").val($( this ).data("air-mode"));
    $("#indoor_light_active").val($( this ).data("indoor-pw"));
    $("#indoor_light_level").val($( this ).data("indoor-light"));
    $("#outside_light_active").val($( this ).data("outside-pw"));
    $("#outside_light_level").val($( this ).data("outside-light"));
    $("#blind_active").val($( this ).data("blind-pw"));
    $("#blind_level").val($( this ).data("blind"));
});
get_current_sensor_data()
draw_rooms()
setInterval(get_current_sensor_data,1000)
setInterval(updateRooms,2000)

