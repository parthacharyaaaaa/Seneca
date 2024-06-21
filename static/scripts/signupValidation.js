import { checkForm } from "./formFunctions.js";

document.getElementById('signupForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const logout_time = new Date();
    const formattedDateTime = logout_time.toLocaleString();
    console.log(formattedDateTime);

    var formData = new FormData(this);
    
    if(checkForm('signup', formData)){
        formData.append("formattedDateTime", formattedDateTime)
        fetch('/signup', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if(data.alert != ""){
                alert(data.alert)
            }
            if(data.redirect_url){
                window.location.href = data.redirect_url
            }
        })
        
        
        .catch(error => console.error('Error:', error));
    }
});