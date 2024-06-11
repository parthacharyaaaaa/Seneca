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
                favItem.classList.add('fav-card');
                favItem.innerHTML = `
            <div class="fav-image">
                <img src="${favInfo[productId].cover}" alt="${favInfo[productId].title}"/>
            </div>
            <div class="fav-details">
                <section class='fav-title'>${favInfo[productId].title}</section>
                <section class='fav-author'>${favInfo[productId].author}</section>
                <div class="fav-genre-rating">
                    <section class='fav-genre ${favInfo[productId].genre['category']}'>${favInfo[productId].genre['category']}</section>
                </div>
                <section class='fav-file'>${favInfo[productId].file_format}</section>
                <section class='fav-price'>$${favInfo[productId].price}</section>
                <hr>
                <div class='fav-card-buttons'>
                <button class='view-button card-button' type='button' onclick='location.href = "/products/view/id=${favInfo[productId].id}"'>View</button>
                <button class='cart-button card-button' type='button' onclick='addToCart(${favInfo[productId].id})'>Add to cart</button>
                <button class='fav-button card-button' type='button' id='${favInfo[productId].id}'>Remove</button>
                </div>
            </div>
        `;
                favsContainer.appendChild(favItem);

                var removeButton = favItem.querySelector('.fav-button');
                removeButton.addEventListener('click', function(event){
                    console.log("Removing faavourite: " + this.id);

                    fetch("/remove-fav", {
                        method : 'POST',
                        headers : {
                            "Content-Type" : "application/json"
                        },
                        body : JSON.stringify({id : this.id})
                    })
                    .then(response => response.json())
                    .then(data => {
                        if(data.valid === 0){
                            alert(data.alert);
                        }
                        else{
                            favItem.remove()
                            alert("Removed item from favourites")
                        }
                    })
                    .catch(error => console.log("Error: ", error))
                })
            };
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
            <span>Time of Purchase: ${orderDetails.time_of_purchase}</span>
            <span>Total Items: ${orderDetails.total_items}</span>
            <span>Total Amount: $${(orderDetails.total_amount).toFixed(2)}</span>
        </div>
        <div class="order-items">
            <div class = "item-container">
            ${orderDetails.items.map(item => `
                    <div class='item'>
                        <span>ID: ${item.product_id}</span>
                        <span>Title: ${item.title}</span><br>
                        <span>Author: ${item.author}</span>
                        <span>ISBN: ${item.isbn}</span><br>
                        <span>Price: $${(item.price).toFixed(2)}</span>
                    </div>
                `).join('')}
                </div>
            </div>
        `;
        ordersContainer.appendChild(orderCard);
    }
}