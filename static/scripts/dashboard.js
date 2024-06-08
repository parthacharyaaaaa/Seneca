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
        
    `;
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
            <span>Total Amount: $${orderDetails.total_amount}</span>
        </div>
        <div class="order-items">
            <div class = "item-container">
                ${orderDetails.items.map(item => `
                    <div class='item'>
                        <span>Title: ${item.product_title}</span><br>
                        <span>ID: ${item.product_id}</span>
                        <span>Price: $${item.product_price}</span>
                    </div>
                `).join('')}
                </div>
            </div>
        `;
        ordersContainer.appendChild(orderCard);
    }
}