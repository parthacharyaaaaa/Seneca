document.addEventListener("DOMContentLoaded", function(event) {
    console.log("Creating bill")

    fetch("/get-bill", {
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
    container.innerHTML = `
        <div class="product-header">
        <p>Title</p>
        <p>Author</p>
        <p>Price ($)</p>
        <p>File Type</p>
        <p>Discount</p>
        </div>
    `
    let total = 0.0;
    products.forEach(product => {
        const productCard = document.createElement('div');
        productCard.classList.add('product-card');
        let rating = parseFloat(product.rating).toFixed(1)
        // You can customize the HTML structure for your product card here
        productCard.innerHTML = `
            <div class="product-image">
                <img src="${product.image1}" alt="${product.title}">
            </div>
            <div class="product-details">
                <p>${product.title}</p>
                <p>${product.author}</p>
                <p>${product.price}</p>
                <p>${product['file format']}</p>
                <p>${product.discount}</p>
            </div>
        `;
        total += product.price

        container.appendChild(productCard);
    });

    document.getElementById('total-bill').innerHTML = total.toFixed(2);
}