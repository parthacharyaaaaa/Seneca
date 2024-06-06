document.getElementById('confirm-purchase').addEventListener('click', function(event){
    console.log("Processing payment")

    fetch('/process-order', {
        headers: {
            "Content-type" : 'application/json'
        },
        method : "POST",
        body : JSON.stringify({validation : "True", receipt_email : document.getElementById('receipt-email').value, billing_email : document.getElementById('billing-email').value})
    })
    .then(response => console.log(response))
    .catch(error => console.log("Error: ", error))
})