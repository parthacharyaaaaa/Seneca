document.addEventListener("DOMContentLoaded", function (event) {
    const csrfToken = document.getElementById('csrf_token').value;

    document.getElementById('confirm-purchase').addEventListener('click', function (event) {
        event.preventDefault()
        console.log("Processing payment")
        var formData = new FormData(document.getElementById('checkout-form'))
        formData.append("flag", "download")
        formData.append("validation", 1)
        
        let billing_email
        try {
            billing_email = document.getElementById('billing-email').value
            formData.append("billing_email", billing_email)
        } catch (error) {
            console.log("User logged in, billing email set")
        }

        fetch('/process-order', {
            method: "POST",
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                console.log(data.alert)
                if (data.alert) {
                    alert(data.alert)
                }
                if (data.flag === "valid") {
                    window.location.href = data.redirect_url
                    return data
                }
            })
            .catch(error => console.log("Error: ", error))
    })

    document.getElementById("mail-button").addEventListener("click", function (event) {
        event.preventDefault()
        console.log("SENDING MAIL")
        var formData = new FormData(document.getElementById('checkout-form'))
        formData.append("flag", "mail")
        formData.append("validation", 1)
        
        let billing_email
        try {
            billing_email = document.getElementById('billing-email').value
            formData.append("billing_email", billing_email)
        } catch (error) {
            console.log("User logged in, billing email set")
        }

        fetch("/process-order", {
            method: "POST",
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.alert) {
                    console.log(data.alert)
                    alert("Alert: " + data.alert)
                }
                if (data.flag === "valid") {
                    window.location.href = data.redirect_url
                    return data
                }
            })
            .catch(error => console.log("Error: ", error))
    })
})

