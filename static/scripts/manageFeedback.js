document.getElementById("contact-form").addEventListener('submit', function(event){
    event.preventDefault();

    const email = document.getElementById("email").value
    const title = document.getElementById("title").value
    const description = document.getElementById("query").value
    const flag = document.getElementById("flag").value
    console.log(flag)

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const validFlags = ["support", "bug", "query", "order", "legal", "api"];

    if(emailRegex.test(email) === false){
        alert("Invalid email address provided")
        return false
    }
    else if(title.length < 6 || description.length < 6){
        alert("Title and description must have atleast 6 characters")
        return false
    }
    else if(!validFlags.includes(flag)){
        alert("Invalid Flag")
        return false;
    }
    else{
        const formData = new FormData(this)
        fetch("/send-feedback", {
            method : "POST",
            body : formData
        })
        .then(response => response.json())
        .then(data => {
            if(data.flag === 1){
                alert("Thank you for your feedback")
                document.getElementById("contact-form").reset()
            }
            else{
                alert("Alert processing feedback: ", data.alert)
            }
        })
        .catch(error => alert("Error: ", error))
    }
    
})