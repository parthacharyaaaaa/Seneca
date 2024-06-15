document.getElementById('confirm-purchase').addEventListener('click', function (event) {
    console.log("Processing payment")
    let billing_email
    try {
        billing_email = document.getElementById('billing-email').value
    } catch (error) {
        billing_email = document.getElementById('billing-email').innerHTML
    }
    fetch('/process-order', {
        headers: {
            "Content-type": 'application/json'
        },
        method: "POST",
        body: JSON.stringify({ validation: "True", billing_email: billing_email })
    })
        .then(response => response.json())
        .then(data => {
            if (data.alert) {
                alert("Alert: ", data.alert)
            }
            if (data.flag === "valid") {
                window.location.href = data.redirect_url
                return data
            }
        })
        //Sending the actual shit to the user

        .catch(error => console.log("Error: ", error))
})