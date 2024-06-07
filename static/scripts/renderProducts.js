document.addEventListener("DOMContentLoaded", function (event) {
    console.log("Called")

    fetch("/get-catalogue", {
        method: "GET"
    })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            displayContent(data)
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
                displayContent(data)
            }
        })
        .catch(error => console.log("Error: ", error))
})

//Function to display the books
function displayContent(products) {
    const container = document.querySelector('.product-container');
    container.innerHTML = ''; // Clear the container
    products.forEach(product => {
        const productCard = document.createElement('div');
        productCard.classList.add('product-card');
        let rating = parseFloat(product.rating).toFixed(1)
        // You can customize the HTML structure for your product card here
        productCard.innerHTML = `
            <div class="product-image">
                <img src="${product.cover}" alt="${product.title}"/>
            </div>
            <div class="product-details">
                <section class='product-title'>${product.title}</section>
                <section class='product-author'>${product.author}</section>
                <div class="product-genre-rating">
                    <section class='product-genre ${product.genre['category']}'>${product.genre['category']}</section>
                    <section class='product-rating '>${rating}</section>
                </div>
                <section class='product-file'>${product.file_format}</section>
                <section class='product-price'>$${product.price}</section>
                <hr>
                <div class='product-card-buttons'>
                <button class='view-button card-button' type='button' onclick='location.href = "/products/view/id=${product.id}"'>View</button>
                <button class='cart-button card-button' type='button' onclick='addToCart(${product.id})'>Add to cart</button>
                </div>
            </div>
        `;
        container.appendChild(productCard);
    });
}

function addToCart(id){
    var formData = new FormData()
    formData.append('id', id);

    fetch("/addToCart", {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if(data.message){
            alert(data.message)
        }
    })
    .catch(error => alert("Error: ", error))
}