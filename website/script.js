function init() {
    console.log('Hello!');
    setInterval(getTemperature, 1000);
}

function getTemperature() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            document.querySelector('#temp').innerHTML = xhr.responseText;
        }
    };

    xhr.open('POST', '/get-temp', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(
        {
            "sensors": "all"
        }
    ));
}