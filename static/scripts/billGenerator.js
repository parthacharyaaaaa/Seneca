document.addEventListener("DOMContentLoaded", function (event) {
    console.log("Creating bill")

    fetch("/get-cart", {
        method: "GET"
    })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            displayContent(data)
        })
        .catch(error => console.log("Error: ", error))
})

function displayContent(products) {
    const container = document.querySelector('.product-container');
    container.innerHTML = '';
    container.innerHTML = `
    <div class="product-header">
        <div>Cover</div>
        <div>Title</div>
        <div>Author</div>
        <div>Price ($)</div>
        <div>File Type</div>
        <div>Discount</div>
        <div>Remove</div>
    </div>
    `
    let total = 0.0;
    Object.keys(products).forEach(key => {
        const product = products[key];
        const productCard = document.createElement('div');
        productCard.classList.add('bill-card');
        productCard.innerHTML = `
        <div class="product-image">
            <img src="${product.cover}" alt="${product.title}">
        </div>
            <div>${product.title}</div>
            <div>${product.author}</div>
            <div>${product.price}</div>
            <div>${product.file_format}</div>
            <div>${product.discount}</div>
            <button class = "subtract-icon" id="${product.id}" type='button' value='-'>-</button>
        `;
        total = total + product.price - product.discount;
        console.log(total)

        container.appendChild(productCard);
        var removeButton = productCard.querySelector('.subtract-icon');
        
        removeButton.addEventListener('click', function(event){
            console.log("subtraction called: " + this.id)

            fetch("/remove-from-cart", {
                method : "POST",
                headers : {
                    "Content-Type" : "application/json"
                },
                body : JSON.stringify({id : this.id})
            })
            .then(response => response.json())
            .then(data => {
                if(data.valid == 0){
                    alert("Error: Cart removal")
                }
                else{
                    productCard.remove()

                    let totalItems = document.getElementById('total-items').innerHTML
                    document.getElementById('total-items').innerHTML = --totalItems
                    if(totalItems == 0){
                        window.location.href = '/cart'
                    }

                    document.getElementById('total-bill').innerHTML -= data.new_total
                }
            })
        })
    }); 

    try {
        document.getElementById('total-items').innerHTML = Object.keys(products).length;
        document.getElementById('total-bill').innerHTML = total.toFixed(2);
    } catch (error) {
        return false;
    }
}