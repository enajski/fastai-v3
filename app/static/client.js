var el = x => document.getElementById(x);

function showPicker(inputId) { el('file-input').click(); }

function showPicked(input) {
    el('upload-label').innerHTML = input.files[0].name;
    var reader = new FileReader();
    reader.onload = function (e) {
        el('image-picked').src = e.target.result;
        el('image-picked').className = '';
    }
    reader.readAsDataURL(input.files[0]);
}

function analyze() {
    var uploadFiles = el('file-input').files;
    if (uploadFiles.length != 1) alert('Dej mie 1 plik!');

    el('analyze-button').innerHTML = 'Analizuja...';
    el('result-label').innerHTML = '';

    var xhr = new XMLHttpRequest();
    var loc = window.location
    xhr.open('POST', `${loc.protocol}//${loc.hostname}:${loc.port}/analyze`, true);
    xhr.onerror = function() {alert (xhr.responseText);}
    xhr.onload = function(e) {
        if (this.readyState === 4) {
            var response = JSON.parse(e.target.responseText);
            el('result-label').innerHTML = `To je ${response['result']}! <p><small>Sicher: Janusz/Mitia/Nie kot/Zbychu ${response['confidences']}</small></p>.`;
        }
        el('analyze-button').innerHTML = 'Analizuj';
    }

    var fileData = new FormData();
    var file = uploadFiles[0]
    var fileName = file.name
    fileData.append('file', file);
    fileData.append('name', fileName); 
    xhr.send(fileData);
}

