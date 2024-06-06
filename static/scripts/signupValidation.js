document.getElementById('signupForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var form = this;
    var formData = new FormData(form);

    fetch('/signup', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if(response.redirected){ window.location.href = response.url;}
        else{
            return response.json();
        }
    })
    .then(data => {
        if (data.message != ""){
            document.getElementById('message').innerText = data.message;
        }
        if(data.alert != ""){
            alert(data.alert)
        }
        window.location.href = data.redirect_url;
    })
    
    .catch(error => console.error('Error:', error));
});