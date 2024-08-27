const div = document.querySelector("#app");
const url = "http://192.168.4.1/discoverDevice";
const controller = new AbortController();
// const timeoutId = setTimeout(() => controller.abort(), 5000);
const x = document.getElementById("demo");
var isConnectedtoDeviceAP = false;



// creating h1 and p elements
const label_status = document.createElement('h3');
const p = document.createElement('p');
const img = document.createElement('img');
label_status.textContent = "Status:";

div.appendChild(label_status);
div.appendChild(p);
div.appendChild(img);

const serv_info = {
    geo_id: document.getElementById('geo_id').value,
}

// Poll for device availibility
function onDeviceAvailable() {
    setTimeout(scanDevice, 0);

    function scanDevice() {

        var opts = {
            headers: {
                'mode': 'no-cors',
                'Content-Type': 'application/json'
            },
            method: 'POST',
            body: JSON.stringify(serv_info)
            // signal: controller.signal
        }

        // sending request
        fetch(url, opts).then((response) => {
            return response.json();  // converting byte data to json
        }).then(data => {

            isConnectedtoDeviceAP = true;
            const { status } = data;
            console.log(status);

        }).catch(err => {
            console.error(err);
            console.log('banana');
            isConnectedtoDeviceAP = false;
        });

        if (isConnectedtoDeviceAP) {
            console.log("Yay!");
            p.textContent = "Registering device connected."
            img.src = "static/img/connected.png";
            img.style = "width: 100px; height: 100px;";

            setTimeout(() => {window.location.replace("http://192.168.4.1/")}, 3000)

        }
        
        else {
            console.log("boo.");
            p.textContent = "Searching for connection";
            img.src = "static/img/loading.gif";
            setTimeout(scanDevice, 6000);
        }
    }
}

onDeviceAvailable();
