document.addEventListener('contentLoaded', function (event) {
    const path = window.location.pathname;
    const id = ((path.split('/'))[2].split("="))[1]


    document.getElementById('add-to-cart').addEventListener('click', function (event) {
        console.log("Caught request for: ", id);
        var formData = new FormData
        formData.append('id', id)
        fetch('/addToCart', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                alert(data.message)
            })

            .catch(error => console.error('Error: ', error));

    });

    document.getElementById('fav-button').addEventListener('click', function (event) {
        fetch('/toggle-favourites', {
            method: "POST",
            headers : {
                "Content-Type" : "application/json"
            },
            body: JSON.stringify({id:id})
        })
        .then(response => response.json())
        .then(data => {
            console.log("Response data: ", data)
            if(data.action === 'add'){
                console.log("Added")
                this.style.backgroundColor = 'red'
            }
            else{
                console.log('removed')
                this.style.backgroundColor = 'black'
            }
        })
    })
})