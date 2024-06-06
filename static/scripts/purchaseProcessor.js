document.getElementById('confirm-purchase').addEventListener('click', function(event){
    console.log("Processing payment")

    try {
        billing_email = document.getElementById('billing-email').value
    } catch (error) {
        billing_email = null
    }
    fetch('/process-order', {
        headers: {
            "Content-type" : 'application/json'
        },
        method : "POST",
        body : JSON.stringify({validation : "True", receipt_email : document.getElementById('receipt-email').value, billing_email : billing_email})
    })
    .then(response => response.json())
    .then(data => {
        if(data.alert){
            alert(data.alert)
        }
        if(data.flag === "valid")
            window.location.href = data.redirect_url
    })
    .catch(error => console.log("Error: ", error)) 
})