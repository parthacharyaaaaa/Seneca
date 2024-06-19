document.addEventListener("DOMContentLoaded", function (event) {
    fetch("/get-catalogue", {
        method: "GET"
    })
        .then(response => response.json())
        .then(data => {
            displayContent(data.books)
        })
        .catch(error => console.log("Error: ", error))
})

document.getElementById('search-field').addEventListener('keydown', function(event){
    if(event.key === "Enter")
        alert("penis")
})
document.getElementById('filter-form').addEventListener('submit', function (event) {
    event.preventDefault()
    searchQuery = document.getElementById("search-field").value

    console.log("Filter called")
    var filterOptions = new FormData(this)
    filterOptions.append("search", searchQuery)
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
function displayContent(products) {
    const container = document.querySelector('.product-container');
    container.innerHTML = '';
    products.forEach(product => {
        const productCard = document.createElement('div');
        productCard.classList.add('product-card');
        let rating = parseFloat(product.rating).toFixed(1)
        productCard.innerHTML = `
            <div class="product-image">
            <div class = "backdrop"></div>
                <img class = 'product-image-image' src="${product.cover}" alt="${product.title}"/>
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
                        <button class='view-button card-button' type='button' onclick='location.href = "/products/id=${product.id}"'>View</button>
                        <button class='cart-button card-button' type='button' onclick='addToCart(${product.id})'>Add to cart</button>
                    </div
                    <div>
                        <button class='fav-button card-button' type='button' id='${product.id}'><3</button>
                    </div>
                </div>
                </div>
        `;
        container.appendChild(productCard);
        const imageContainer = productCard.querySelector('.backdrop')
        imageContainer.style.backgroundImage = `url(${product.cover})`
        imageContainer.style.backgroundSize = 'cover';
        imageContainer.style.filter = 'blur(50px)';
        productCard.querySelector('.product-image-image').style.filter = 'blur(0px)';
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