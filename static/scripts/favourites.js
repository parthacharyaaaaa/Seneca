document.addEventListener('contentLoaded', function (event) {
    console.log("fav called")
    const hearts = document.querySelectorAll('.fav-button')

    if (hearts.length === 0) {
        console.log("No fav buttons found");
    }
    hearts.forEach(icon => {
        icon.addEventListener('click', function (event) {
            console.log("Doki Doki")

            const productID = event.target.id
            console.log(productID)
            fetch('/add-favourite', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id: productID })
            })
                .then(response => response.json())
                .then(data => {
                    if(data.alert){
                        alert(data.alert)
                    }
                })
                .catch(error => alert(error))

        })
    })
})