document.addEventListener("DOMContentLoaded", function (event) {
    console.log("Called")

    fetch("/get-catalogue", {
        method: "GET"
    })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            displayContent(data.books, data.favourites)
        })
        .catch(error => console.log("Error: ", error))
})

document.getElementById('filter-form').addEventListener('submit', function (event) {
    event.preventDefault()

    console.log("Filter called")
    var filterOptions = new FormData(this)
    console.log(filterOptions)
    fetch("/get-catalogue", {
        method: "POST",
        body: filterOptions
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return false;
            }
            else {
                console.log(data)
                displayContent(data.books)
            }
        })
        .catch(error => console.log("Error: ", error))
})

//Function to display the books
function displayContent(products, favourites) {
    var current_favourites = favourites
    const container = document.querySelector('.product-container');
    container.innerHTML = '';
    console.log(typeof (products))
    products.forEach(product => {
        const productCard = document.createElement('div');
        productCard.classList.add('product-card');
        let rating = parseFloat(product.rating).toFixed(1)
        productCard.innerHTML = `
            <div class="product-image">
                <img src="${product.cover}" alt="${product.title}"/>
            </div>
            <div class="product-details">
                <div class = "book-credentials">
                    <section class='product-title'>${product.title}</section>
                    <section class='product-author'>${product.author}</section>
                    </div>
                    
                <div class="product-genre-rating">
                    <div class = 'product-genre-container'>
                        ${product.genre.map(genre => `<section class='product-genre ${genre}'>${genre}</section>`).join('')}
                    </div>
                    <section class='product-rating '>★ ${rating}</section>
                </div>
                <div class = "download-details">
                    <section class='product-file'>${product.file_format}</section>
                    <section class='product-price'>$${product.price}</section>
                </div>
                <div class='card-buttons'>
                <div>
                        <button class='view-button card-button' type='button' onclick='location.href = "/products/view/id=${product.id}"'>View</button>
                        <button class='cart-button card-button' type='button' onclick='addToCart(${product.id})'>Add to cart</button>
                    </div
                    <div>
                        <button class='fav-button card-button' type='button' id='${product.id}'><3</button>
                    </div>
                </div>
                </div>
        `;
        container.appendChild(productCard);
        const imageContainer = productCard.querySelector('.product-image')
        imageContainer.style.backgroundImage = `url(${product.image})`
        imageContainer.style.backgroundSize = 'cover';
        // imageContainer.style.filter = 'blur(5px)'
        // imageContainer.style.backgroundColor = 'red';
        var favButton = productCard.querySelector('.fav-button')
        if (favourites.includes(favButton.id)) {
            favButton.style.color = 'red'
        }
        favButton.addEventListener('click', function (event) {
            const productID = event.target.id
            console.log(productID)
            if (current_favourites.includes(favButton.id)) {
                var endpoint = '/remove-favourite'
            }
            else {
                var endpoint = '/add-favourite'
            }
            fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id: productID })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.alert) {
                        alert(data.alert)
                    }
                    if ((data.updated_favourites).length > current_favourites.length) {
                        favButton.style.color = 'red'
                    }
                    else {
                        favButton.style.color = 'white'
                    }

                    current_favourites = data.updated_favourites
                })
                .catch(error => alert(error))
        })

    });
    const event = new Event('contentLoaded');
    document.dispatchEvent(event)
}
function addToCart(id) {
    var formData = new FormData()
    formData.append('id', id);

    fetch("/addToCart", {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message)
            }
        })
        .catch(error => alert("Error: ", error))
}