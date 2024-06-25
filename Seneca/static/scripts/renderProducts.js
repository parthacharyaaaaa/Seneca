document.addEventListener("DOMContentLoaded", function (event) {
    let page = 1;
    var sortOption
    var maxPrice, minPrice, maxPages, minPages

    const url = new URL(window.location.href)
    const searchParams = new URLSearchParams(url.search)
    let x = searchParams.get('search')
    if(x != "" || x != null){
        searchParams.delete('search');
        url.search = searchParams.toString();
        window.history.replaceState({}, document.title, url.toString());
    }
    var search
    if(["romance", 'fiction', 'dystopian'].includes(x)){
        search = x
    }


    function fetchCatalogue() {
        let url = `/get-catalogue?page=${page}`;
        if (search) url += `&search=${search}`;
        if (sortOption) url += `&sort_by=${sortOption}`;
        if (maxPrice) url += `&max-price=${maxPrice}`;
        if (minPrice) url += `&min-price=${minPrice}`;
        if (maxPages) url += `&max-pages=${maxPages}`;
        if (minPages) url += `&min-pages=${minPages}`;
        console.log(maxPrice, minPrice, maxPages, minPages)
        
        fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.books.length === 0) {
                alert("empty");
            } else {
                console.log(data.books);
                displayContent(data);
                updatePagination(data);
            }
        })
        .catch(error => console.log("Error: ", error));
    }

    function updatePagination(data) {
        const paginationContainer = document.querySelector('.pagination');
        paginationContainer.innerHTML = '';

        if (data.has_prev) {
            const prevButton = document.createElement('button');
            prevButton.textContent = 'Previous';
            prevButton.classList.add("card-button")
            prevButton.addEventListener('click', function() {
                page = data.prev_page;
                fetchCatalogue();
            });
            paginationContainer.appendChild(prevButton);
        }

        if (data.has_next) {
            const nextButton = document.createElement('button');
            nextButton.classList.add("card-button")
            nextButton.textContent = 'Next';
            nextButton.addEventListener('click', function() {
                page = data.next_page;
                fetchCatalogue();
            });
            paginationContainer.appendChild(nextButton);
        }
    }

    fetchCatalogue();

    var searchField = document.getElementById('search-field');
    searchField.addEventListener('keydown', function(event){
        if(event.key === "Enter"){
            console.log("Searching");
            document.getElementById("filter-form").reset();
            minPrice = null, maxPrice = null, minPages = null, maxPages = null
            search = searchField.value.trim();
            page = 1;
            fetchCatalogue();
        }
    });

    var sortButtons = document.querySelectorAll('[name="sort-option"]');
    sortButtons.forEach(sortButton =>
        sortButton.addEventListener('click', function(event){
            sortOption = sortButton.value;
            if(sortOption < 1 || sortOption > 10){
                alert("Invalid sorting logic applied")
                return false
            }
            page = 1;
            fetchCatalogue();
        })
    );

    document.getElementById("filter-form").addEventListener('submit', function(event){
        event.preventDefault();
        maxPrice = document.getElementById('max-price').value;
        minPrice = document.getElementById('min-price').value;
        maxPages = document.getElementById('max-pages').value;
        minPages = document.getElementById('min-pages').value;

        if (isNaN(maxPages) || isNaN(minPages) || isNaN(maxPrice) || isNaN(minPrice)) {
            alert("Improper Filter Option Entered (Non-Number)");
            this.reset();
        } else {
            page = 1;
            fetchCatalogue();
        }
    });
});

//Function to display the books
function displayContent(products) {
    console.log(products)
    const container = document.querySelector('.product-container');
    container.innerHTML = '';
    (products.books).forEach(product => {
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
                        <button class='cart-button card-button' type='button' name='${product.id}'>Add to cart</button>
                    </div>
                        <button class='fav-button card-button' type='button' id='${product.id}'><3</button>
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