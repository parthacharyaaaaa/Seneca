document.addEventListener("DOMContentLoaded", function(event) {
    console.log("Creating bill")

    fetch("/get-cart", {
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
        <div>Cover</div>
        <div>Title</div>
        <div>Author</div>
        <div>Price ($)</div>
        <div>File Type</div>
        <div>Discount</div>
    </div>
    `
    let total = 0.0;
    Object.keys(products).forEach(key => {
        const product = products[key];
        const productCard = document.createElement('div');
        productCard.classList.add('bill-card');
        let rating = parseFloat(product.rating).toFixed(1);
        // You can customize the HTML structure for your product card here
        productCard.innerHTML = `
        <div class="product-image">
            <img src="${product.cover}" alt="${product.title}">
        </div>
            <div>${product.title}</div>
            <div>${product.author}</div>
            <div>${product.price}</div>
            <div>${product.file_format}</div>
            <div>${product.discount}</div>
        `;
        total = total + product.price - product.discount;
        console.log(total)
    
        container.appendChild(productCard);
    });
    
    try {
        document.getElementById('total-items').innerHTML = "Total Items: " + Object.keys(products).length;
        document.getElementById('total-bill').innerHTML = "Total Price: $" + total.toFixed(2);
    } catch (error) {
        return false;
    }
}