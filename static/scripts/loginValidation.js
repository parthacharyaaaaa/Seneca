document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var form = this;
    var formData = new FormData(form);

    fetch('/login', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.redirected) {
            console.log("Called")
            // alert('submitted');
            // form.removeEventListener('submit', arguments.callee);
            // form.submit();
            window.location.href = response.url;
        } else {
            return response.json();
        }
    })
    .then(data => {
        if (data && !data.authenticated) {
            alert('False');
            document.getElementById('message').innerText = data.message; 
        }
    })
    .catch(error => console.error('Error:', error));
});