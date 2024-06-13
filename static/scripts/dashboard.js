document.addEventListener("DOMContentLoaded", function (event) {
    console.log("Loading dashboard")

    fetch("/get-user-info", {
        method: "GET",
        headers: {
            "Accept": "application/json"
        }
    })
        .then(response => response.json())
        .then(data => {
            console.log(data.user_info)
            renderDashboard(data)
        })
        .catch(error => console.log("Error: ", error))
})

function renderDashboard(data) {
    renderUserInfo(data.user_info);
    renderFavourites(data.fav_info);
    renderOrders(data.order_info);
}

function renderUserInfo(userInfo) {
    const userCard = document.querySelector('.user-card');
    userCard.innerHTML = `
        <h2>User Information</h2>
        <p><b>Name</b>: ${userInfo.first_name + ' ' + userInfo.last_name}</p>
        <p><b>Email</b>: ${userInfo.email_id}</p>
        <p><b>Phone Number</b>: ${userInfo.phone_number}</p>
        <button type="button" id='logout' class="hover-button">Logout</button>
    `;

    document.getElementById('logout').addEventListener('click', function(event){
        console.log("logging out")
        const logout_time = new Date();
        const formattedDateTime = logout_time.toLocaleString();
        console.log(formattedDateTime);
        fetch('/logout', {
            method : 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ formattedDateTime: formattedDateTime })
        })
        .then(response => response.json())
        .then(data => {
            if(data.alert){
                alert(data.alert)
            }
            if(data.redirect_url){
                window.location.href = data.redirect_url
            }
        })
        .catch(error => alert("Error: ", error))
    })
}

function renderFavourites(favInfo) {
    const favsContainer = document.querySelector('.favs');
    if (Object.keys(favInfo).length === 0) {
        favsContainer.innerHTML = `
        <div class='message' id='empty-fav'>
            Playing hard to get?
        </div>`;
    }
    else {
        console.log(favInfo)
        for (const productId in favInfo) {
            if (favInfo.hasOwnProperty(productId)) {
                const favItem = document.createElement('div');
                favItem.classList.add('product-card');
                favItem.innerHTML = `
                    <div class="product-image">
                        <img src="${favInfo[productId].cover}" alt="${favInfo[productId].title}"/>
                    </div>
                    <div class="product-details">
                        <div class="book-credentials">
                            <section class="product-title">${favInfo[productId].title}</section>
                            <section class="product-author">${favInfo[productId].author}</section>
                        </div>
                        <div class="product-genre-rating">
                            <div class="product-genre-container">
                                ${favInfo[productId].genre.map(genre => `<section class="product-genre ${genre}">${genre}</section>`).join('')}
                            </div>
                        </div>
                        <div class="download-details">
                            <section class="product-file">${favInfo[productId].file_format}</section>
                            <section class="product-price">$${favInfo[productId].price}</section>
                        </div>
                        <div class="card-buttons">
                            <div>
                                <button class="view-button card-button" type="button" onclick='location.href="/products/view/id=${favInfo[productId].id}"'>View</button>
                                <button class="cart-button card-button" type="button" onclick='addToCart(${favInfo[productId].id})'>Add to cart</button>
                            </div>
                            <div>
                                <button class="fav-button card-button" type="button" id="${favInfo[productId].id}">x</button>
                            </div>
                        </div>
                    </div>
                `;
                favsContainer.appendChild(favItem); // Append each product card to the body or another container element
                favButton = favItem.querySelector('.fav-button')
                favButton.addEventListener('click', function(event){
                    fetch('/toggle-favourites', {
                        method : 'POST',
                        headers : {
                            'Content-Type' : 'application/json'
                        },
                        body : JSON.stringify({id : this.id})
                    })
                    .then(response => response.json())
                    .then(data =>{
                        if(data.error){
                            alert(data.error)
                        }
                        else{
                            favItem.remove()
                        }
                    })
                })
            }
        }
    }
}

function renderOrders(orderInfo) {
    console.log("Order Info: ", orderInfo)
    const ordersContainer = document.querySelector('.orders-container');
    ordersContainer.innerHTML = '<h2>Order History</h2> <hr>';
    for (const [orderId, orderDetails] of Object.entries(orderInfo)) {
        const orderCard = document.createElement('div');
        orderCard.classList.add('order-card');
        orderCard.innerHTML = `
        <div class = "item-header">
            <span>Order ID: ${orderDetails.order_id}</span>
            <span id='order-time'>Time of Purchase: ${orderDetails.time_of_purchase}</span>
            <span>Total Items: ${orderDetails.total_items}</span>
            <span>Total Amount: $${(orderDetails.total_amount).toFixed(2)}</span>
        </div>
        <div class="order-items">
            <div class = "item-container">
            ${orderDetails.items.map(item => `
                    <div class='item'>
                        <span>ID: ${item.product_id}</span><br>
                        <span>Title: ${item.title}</span><br>
                        <span>Author: ${item.author}</span><br>
                        <span>ISBN: ${item.isbn}</span><br>
                        <span>Price: $${(item.price).toFixed(2)}</span>
                        <hr>
                    </div>
                `).join('')}
                </div>
            </div>
        `;
        ordersContainer.appendChild(orderCard);
    }
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