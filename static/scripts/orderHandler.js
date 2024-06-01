document.getElementById('add-to-cart').addEventListener('click', function(event) {
    // Check if the user is signed in using a server-side templating language
    const signedIn = document.querySelector('meta[name="signed-in"]').getAttribute('content');
    const product_id = event.currentTarget.getAttribute('data-product-id');
    console.log(product_id)
    const amount = parseInt(document.getElementById('quantity').value)

    if(signedIn == "False"){
        alert("You must have a Haki account to use this feature");
        return false;
    }
    else{
        var formData = new FormData()
        formData.append('id', product_id);
        formData.append('quantity', amount);

        console.log("Caught request for: ", product_id);

        fetch('/addToCart', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message)
        })
        
        .catch(error => console.error('Error: ', error));
    }
});

document.getElementById('purchase').addEventListener('click', function(event) {
    const signedIn = document.querySelector('meta[name="signed-in"]').getAttribute('content');
    const product_id = event.currentTarget.getAttribute('data-product-id');
    console.log(product_id)
    const amount = parseInt(document.getElementById('quantity').value)

    var formData = new FormData()
    formData.append('id', product_id);
    formData.append('quantity', amount);

        fetch('/purchaseThenCheckout',{
            method : "POST",
            body : formData
        })
        .then(response => {
            console.log("Redirecting: API")
                window.location.href = response.url
        })
        .catch(error => console.log("Error: ", error))
})