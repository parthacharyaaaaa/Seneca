import { checkForm } from "./formFunctions.js";
document.getElementById("contact-form").addEventListener('submit', function (event) {
    event.preventDefault();
    const formData = new FormData(this)
    // if (checkForm('feedback', formData)) {
        fetch("/contact", {
            method: "POST",
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.flag === 1) {
                    alert("Thank you for your feedback")
                    document.getElementById("contact-form").reset()
                }
                else {
                    alert("Alert processing feedback: ", data.alert)
                }
            })
            .catch(error => alert("Error: ", error))
    // }
})