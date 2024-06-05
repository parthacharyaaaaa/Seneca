document.getElementById('gift-button').addEventListener('click', function(event){
    console.log("clicked")
    fetch("/gift",{
        method : 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body : JSON.stringify({giftEmail : document.getElementById('gift-id').value})
    })
    .then(response => console.log(response))
    // .then(data => console.log(data.message))
    .catch(error => console.log("Error: ", error))
})