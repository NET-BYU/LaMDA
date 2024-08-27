var geo_id;

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else {
        x.innerHTML = "Geolocation is not supported by this browser.";
    }
}

function showPosition(position) {
    var banana = "(" + position.coords.latitude + ", " + position.coords.longitude + ")";

    console.log(document.getElementById('loc').value);
    document.getElementById('loc').value = banana;

}

// var btn = document.getElementById("sendInfo");
// btn.addEventListener("click", alertMe);
// btn.addEventListener("click", hideReg);
const url = "<Put wss addr here>";

function hideReg() {
    document.getElementById('register').style.display = 'none';
    document.getElementById('connecting').style.display = 'block';
}

var donesky;

function alertMe() {

    let formData = new FormData();
    formData.append('userEmail', document.getElementById('userEmail').value);
    formData.append('uuid', document.getElementById('uuid').value);
    formData.append('location', document.getElementById('loc').value);

    var opts = {
        method: 'POST',
        body: formData,
        // signal: controller.signal
    }

    // sending request
    fetch(url, opts).then((response) => response.json())
        .then(data => {
            console.log(data['geo_id']);

            var isConnectedtoDeviceAP = false;

            const serv_info = {
                geo_id: data['geo_id'],
            }

            donesky = data['geo_id'];

        }).catch(err => {
            console.error(err);
            console.log('banana');
        });

}

$(document).ready(function () {
    var socket = io.connect();
    var register_socket = io("<Put wss addr here>"')

    $('#sendInfo').on('click', function () {
        var email = $('#userEmail').val();
        var dev_id = $('#uuid').val();
        var loc = $('#loc').val();
        hideReg();

        register_socket.emit('reg', { 'email': email, 'dev_id': dev_id, 'loc': loc });
    });

    $('#testInfo').on('click', function () {
        socket.emit('ping_measure');
    });

    socket.on('pong_measure', function (msg) {
        console.log("banana: ", msg);
        socket.emit('ping_measure');
    });

    // register_socket.on('pong_measure', function (msg) {
    //     console.log("banana: ", msg);
    //     register_socket.emit('ping_measure', "Yo wassa?");
    // });

    register_socket.on('id', function (msg) {
        geo_id = msg;
    });

});

getLocation();
