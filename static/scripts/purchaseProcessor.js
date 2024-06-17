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
        body: JSON.stringify({ validation: "True", billing_email: billing_email, action : "download"})
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
        .catch(error => console.log("Error: ", error))
})

document.getElementById("mail-button").addEventListener("click", function(event){
    console.log("SENDING MAIL")
    let billing_email
    try {
        billing_email = document.getElementById('billing-email').value
    } catch (error) {
        billing_email = document.getElementById('billing-email').innerHTML
    }
    const email = document.getElementById("mail-id").value
    const confirmEmail = document.getElementById("confirm-mail-id").value
    let message
    try {
        message = document.getElementById("gift-message").value
    } catch (error) {
        message = ""
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if(!emailRegex.test(email)){
        alert("Invalid email address provided")
        return false
    }
    else if(email != confirmEmail){
        alert("Email addresses don't match, Please enter recipient address properly")
        return false
    }

    fetch("/process-order", {
        method : "POST",
        headers : {
            "Content-Type" : "application/json"
        },
        body : JSON.stringify({validation : "True", billing_email : billing_email, action : "mail", recipient : email, message : message})
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
    .catch(error => console.log("Error: ", error))
})