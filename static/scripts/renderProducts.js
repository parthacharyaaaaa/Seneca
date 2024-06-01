document.addEventListener("DOMContentLoaded", function(event) {
    console.log("Called")

    fetch("/render-products", {
        method : "GET"
    })
    .then(response => response.json())
    .then(data =>{
        console.log(data)
        displayContent(data)
    })
    .catch(error => console.log("Error: ", error))
})

function displayContent(products) {
    const container = document.querySelector('.product-container');
    container.innerHTML = ''; // Clear the container
    products.forEach(product => {
        const productCard = document.createElement('div');
        productCard.classList.add('product-card');

        // You can customize the HTML structure for your product card here
        productCard.innerHTML = `
            <div class="product-image">
                <img src="${product.image1}" alt="${product.title}">
            </div>
            <div class="product-details">
                <h2>${product.title}</h2>
                <p>${product.summary}</p>
                <p>Price: $${product.price}</p>
                <p>Rating: ${product.rating}</p>
            </div>
        `;

        container.appendChild(productCard);
    });
}