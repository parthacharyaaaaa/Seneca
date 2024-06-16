document.addEventListener('DOMContentLoaded', function (event) {
    console.log("Loading product")
    const path = window.location.pathname;

    const id = ((path.split('/'))[2].split("="))[1]
    fetch("/get-product-details", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ id: id })
    })
        .then(response => response.json())
        .then(data => renderPage(data.product))
})

function renderPage(product) {
    console.log(product)
    const productContainer = document.querySelector('.product-container');
    productContainer.innerHTML = ''
    productContainer.innerHTML = `
        <div class="product-image">
            <div class = "backdrop">
            </div>
            <img src = "${product.cover}" alt = "${product.title}">
        </div>
        <div class="product-info">
            <h2>${product.title}</h2><hr style="margin-bottom: 0.5rem;">
            Product Details:
            <div class = "upper-specs">
            <span class = "id">Written By: ${product.author}</span>
            <span class = "file-format">Format: ${product.file_format}</span>
            </div>
            <div class = "lower-specs">
            <span class = "price">Original Price: ${product.price}</span>
            <span class = "discount">Discount: ${product.discount}</span>
            </div>
            <div class = "ratings">
            <span class = "rating">Rating: ${product.rating}</span>
            <span class = "reviews">Reviews: ${product.reviews}</span>
            </div>
            <span class = "sold">Sold: ${product.sold}</span>
            <hr>
            <p class = summary>${product.summary}</p>
            <hr>
            <div class = "icons">
            <div>
            <i class="fas fa-book icon"></i>
                <span class = "pp">Print Length</span>
            </div>
            <div>
            <i class="fas fa-calendar icon"></i>
                <span class = "pp">Publication Date</span>
            </div>
            <div>
            <i class="fas fa-print icon"></i>
                <span class = "pp">Publisher</span>
            </div>
            <div>
            <i class="fas fa-globe icon"></i>
                <span class = "pp">Language</span>
            </div>
                <span class = "pages">${product.pages}</span>
                <span class = "publish-date">${product.publication_date}</span>
                <span class = "publisher">${product.publisher}</span>
                <span class = "language">${product.language}</span>
            </div>
                <button id ="add-to-cart" class="hover-button" type="button">Add To Cart </button>
                <button id ="fav-button" class="hover-button" type="button">Add To Favourites</button>
        </div>
    `
    const imageContainer = productContainer.querySelector('.backdrop')
    imageContainer.style.backgroundImage = `url(${product.cover})`
    imageContainer.style.backgroundSize = 'cover';
    imageContainer.style.filter = 'blur(50px)';

    const event = new Event('contentLoaded');
    document.dispatchEvent(event)
}