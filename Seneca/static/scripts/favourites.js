document.addEventListener('contentLoaded', function (event) {
    const hearts = document.querySelectorAll('.fav-button')
    var favourites
    console.log("Buttons: " + hearts.length)
    fetch('/get-favourites', {
        method: 'GET'
    })
        .then(response => response.json())
        .then(data => {
            if (data.isGuest === 1) {
                hearts.forEach(icon => {
                    icon.addEventListener('click', function (event) {
                        alert("You need a Seneca account to add favourite items")
                    })
                })
            }
            else {
                favourites = data.favs
                console.log(favourites)
                hearts.forEach(icon => {
                    console.log(icon)
                    if (favourites.includes(icon.id)) {
                        icon.style.backgroundColor = 'var(--BGCOLOR-BUTTONS-2)'
                    }
                    icon.addEventListener('click', function (event) {
                        fetch('/toggle-favourites', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                "X-CSRFToken": document.querySelector("meta[name='csrf-token']").getAttribute('content')
                            },
                            body: JSON.stringify({ id: icon.id })
                        })
                            .then(response => response.json())
                            .then(data => {
                                if (data.CSRFError) {
                                    alert(data.CSRFError)
                                    return false;
                                }
                                if (data.action === 'add') {
                                    console.log("Added")
                                    icon.style.backgroundColor = 'var(--BGCOLOR-BUTTONS-2)'
                                }
                                else {
                                    console.log('removed')
                                    icon.style.backgroundColor = 'black'
                                }
                            })
                    })
                })
            }
        })
        .catch(error => alert("Error: ", error))

    const addButtons = document.querySelectorAll('.cart-button')
    fetch('/get-cart?flag=id', {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            addButtons.forEach(addButton => {
                var id = addButton.getAttribute('name')
                if (data.includes(id)) {
                    addButton.innerHTML = "In Cart";
                }
                addButton.addEventListener('click', function (event) {
                    var formData = new FormData()
                    formData.append('id', id);
                    fetch("/addToCart", {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": document.querySelector("meta[name='csrf-token']").getAttribute('content')
                        },
                        body: formData
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data.CSRFError) {
                                alert(data.CSRFError)
                            }
                            if (data.added === 1) {
                                addButton.innerHTML = "In Cart"
                            }
                            if (data.message) {
                                alert(data.message)
                            }
                        })
                        .catch(error => alert("Error: ", error))
                })
            })

        })
})