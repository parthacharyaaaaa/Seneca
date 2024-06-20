document.addEventListener("DOMContentLoaded", function (event) {
    var search = document.getElementById('search-field').value
    var sortOption = null
    fetch("/get-catalogue", {
        method: "GET"
    })
        .then(response => response.json())
        .then(data => {
            displayContent(data.books)
        })
        .catch(error => console.log("Error: ", error))


    var searchField = document.getElementById('search-field')
    searchField.addEventListener('keydown', function(event){
        if(event.key === "Enter"){
            console.log("Searching")
            document.getElementById("filter-form").reset()
            search = searchField.value.trim()
            fetch(`/get-catalogue?search=${search}`, {
                method : "GET",
                headers : {
                    "Content-Type" : "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                if((data.books).length === 0){
                    alert("empty")
                }
                else{
                    console.log(data.books)
                    displayContent(data.books)
                }
            })
        }
            
    })
    
    var sortButtons = document.querySelectorAll('[name="sort-option"]')
    sortButtons.forEach(sortButton =>
        sortButton.addEventListener('click', function(event){
            sortOption = sortButton.value
            fetch(`/get-catalogue?search=${search}&sort_by=${sortOption}`, {
                method : "GET",
                headers : {
                    "Content-Type" : "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                if((data.books).length === 0){
                    alert("empty")
                }
                else{
                    console.log(data.books)
                    displayContent(data.books)
                }
            })
        })
    )

    document.getElementById("filter-form").addEventListener('submit', function(event){
        event.preventDefault()
        const maxPrice = document.getElementById('max-price').value
        const minPrice = document.getElementById('min-price').value
        const maxPages = document.getElementById('max-pages').value
        const minPages = document.getElementById('min-pages').value

        if(isNaN(maxPages) || isNaN(minPages) || isNaN(maxPrice) || isNaN(minPrice)){
            alert("Improper Filter Option Entered (Non-Number)")
            this.reset()
        }
        fetch(`/get-catalogue?search=${search}&sort_by=${sortOption}&max-price=${maxPrice}&min-price=${minPrice}&max-pages=${maxPages}&min-pages=${minPages}`, {
            method : 'GET',
            headers : {
                "Content-Type" : "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            if((data.books).length === 0){
                alert("empty")
            }
            else{
                console.log(data.books)
                displayContent(data.books)
            }
        })
    })
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
                        <button class='view-button card-button' type='button' onclick='location.href = "/products?viewkey=${product.id}"'>View</button>
                        <button class='cart-button card-button' type='button' onclick='addToCart(${product.id})'>Add to cart</button>
                    </div>
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