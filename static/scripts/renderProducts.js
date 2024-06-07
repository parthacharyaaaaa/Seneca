document.addEventListener("DOMContentLoaded", function(event) {
    console.log("Called")

    fetch("/get-catalogue", {
        method : "GET"
    })
    .then(response => response.json())
    .then(data =>{
        console.log(data)
        displayContent(data)
    })
    .catch(error => console.log("Error: ", error))
})

document.getElementById('filter-form').addEventListener('submit', function(event){
    event.preventDefault()

    console.log("Filter called")
    var filterOptions = new FormData(this)
    console.log(filterOptions)
    fetch("/get-catalogue", {
        method : "POST",
        body : filterOptions
    })
    .then(response => response.json())
    .then(data =>{
        if(data.error){
            alert(data.error);
            return false;
        }
        else{
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
    container.innerHTML = `
        <div class="product-header">
        <p>Title</p>
        <p>Author</p>
        <p>Price ($)</p>
        <p>Rating</p>
        <p>File Type</p>
        </div>
    `
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
                <p>${rating}</p>
                <p>${product.rating}</p>
                <p>${product.file_format}</p>
            </div>
        `;
        container.appendChild(productCard);
    });
}