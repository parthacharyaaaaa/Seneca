document.getElementById('signupForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var form = this;
    var formData = new FormData(form);

    fetch('/signup', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.redirected) {
            alert('submitted');
            // form.removeEventListener('submit', arguments.callee);
            // form.submit();
            window.location.href = 'http://127.0.0.1:6900';
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
