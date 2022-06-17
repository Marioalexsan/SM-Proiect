async function tick() {
    await fetch('/info/temperature')
    .then(response => response.text())
    .then(data => document.getElementById('temp-display').innerHTML = data )
    .catch(reason => document.getElementById('temp-display').innerHTML = 'Error: ' + reason);

    await fetch('/info/humidity')
    .then(response => response.text())
    .then(data => {
        document.getElementById('humid-display').innerHTML = data;
    })
    .catch(reason => document.getElementById('temp-display').innerHTML = 'Error: ' + reason);

    setTimeout(tick, 5000);
}

window.addEventListener('load', event => {
    document.querySelector('#layout-header-navbutton').addEventListener('click', _event => {
        const nav = document.querySelector('nav');
        nav.classList.toggle('layout-nav-move');
    });

    setTimeout(tick, 0);
});