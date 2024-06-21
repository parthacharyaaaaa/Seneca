export function checkForm(flag, formDetails) {
    console.log("Called")
    //Checking for empty inputs
    for (let [field, value] in formDetails.entries()) {
        if (!value || value === undefined || value === '') {
            alert("Please fill in all fields in the form");
            return false;
        }
    }
    if (flag === 'signup') {
        console.log("signup")
        const firstName = formDetails.get('first_name'), lastName = formDetails.get('last_name'), age = formDetails.get('age'), emailID = formDetails.get('email_id'), phoneNumber = formDetails.get('phone_number'), password = formDetails.get('password'), cPassword = formDetails.get('confirm_password');

        //Check name
        const alphabets = /^[A-Za-z]+$/
        if (!alphabets.test(firstName) || !alphabets.test(lastName)) {
            alert("Name must be strictly alphabetical")
            return false;
        }

        //Check Age
        if (isNaN(age)) {
            alert("Invalid Age");
            return false;
        }
        else if (age > 100) {
            alert("Come on dude, you are NOT that old")
            return false;
        }
        else if (age < 12) {
            alert("googoogaagaa")
            return false;
        }

        //Check Email
        const email = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email.test(emailID)) {
            alert("Invalid email address entered")
            return false;
        }

        //Check Passwords
        if (password.length < 8 || password.length > 32) {
            alert("Password length must be between 8 and 32 characters")
            return false;
        }
        else if (password != cPassword) {
            alert("Passwords do not match")
            return false;
        }
        //All checks out, send to endpoint
        console.log("All good")

        return true;
    }

    else if (flag === 'login') {
        const identity = formDetails.get('emailPhone'), password = formDetails.get('password')
        const email = /^[^\s@]+@[^\s@]+\.[^\s@]+$/, phoneNumberRegex = /^(\+?\d{2}[- .]?)?\d{10}$/;

        //Check email/phone
        if (!email.test(identity) && !phoneNumberRegex.test(identity)) {
            alert("Invalid email address/phone number")
            return false;
        }
        return true;
    }

    else if (flag === 'feedback') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const validFlags = ["support", "bug", "query", "order", "legal", "api"];
        const emailID = formDetails.get('email'), title = formDetails.get('title'),
        flag = formDetails.get('flag'), query = formDetails.get('query')

        if(emailRegex.test(emailID) === false){
            alert("Invalid email address provided")
            return false
        }
        else if(title.length < 6 || query.length < 6){
            alert("Title and description must have atleast 6 characters")
            return false
        }
        else if(!validFlags.includes(flag)){
            alert("Invalid Flag")
            return false;
        }

        return true;
    }
    else if (flag === 'review'){
        const title = formDetails.get('review-title'), rating = formDetails.get('rating3'),
        body = formDetails.get('review-body')

        if(title.length < 6 || body.length < 32){
            alert("Title length must be atleast 6, body length must be atleast 32")
            return false;
        }

        if(rating < 1 || rating > 5 || isNaN(rating)){
            alert("Invalid rating provided")
            return false;
        }
        return true;
    }
    
}