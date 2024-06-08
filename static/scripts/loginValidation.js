document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var form = this;
    var formData = new FormData(form);

    fetch('/login', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if(data.alert != ""){
            alert(data.alert)
        }
        if(data.redirect_url){
            window.location.href = data.redirect_url
        }
    })
    
    .catch(error => console.error('Error:', error));
});