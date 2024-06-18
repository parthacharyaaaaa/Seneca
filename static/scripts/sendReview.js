document.addEventListener("DOMContentLoaded", function(event){
    var offset = 0
    const path = window.location.pathname;
    const id = ((path.split('/'))[2].split("="))[1]

    document.getElementById("review-form").addEventListener('submit', function(event){
        event.preventDefault()
        console.log("Send pp")
        var formData = new FormData(this)
        formData.append("id", id)

        fetch("/add-review", {
            method : "POST",
            body : formData
        })
        .then(response => response.json())
        .then(data => {
            alert(data.alert)
            document.getElementById("review-form").reset()
        })
    })

    const reviewContainer = document.querySelector(".review-section")
    reviewContainer.innerHTML = ''
    console.log("Reviews called")
    fetch("/get-reviews", {
        method : "POST",
        headers : {
            "Content-Type" : "application/json"
        },
        body : JSON.stringify({ id : id , offset : offset})
    })
    .then(response => response.json())
    .then(data => {
        if(data.isEmpty === 1){
            reviewContainer.innerHTML = "Woah, sure is empty around here"
            return false
        }
        else{
            loadReviews(data)
        }
    })

    function loadReviews(data){
        console.log(data.reviews, data.hasMore)
        const reviewContainer = document.querySelector(".review-section")
        data.reviews.forEach(review => {
            const reviewObj = document.createElement('div');
            reviewObj.classList.add('review-item');
            
            reviewObj.innerHTML = `
            <div class = "review-item">
                <span class = "review-title"> ${review.title} </span>
                <span class = "review-credentials">${review.user} at ${review.time}</span> 
                <div class = "review-body"> ${review.body} </div>
            </div>
            `;
            reviewContainer.appendChild(reviewObj);
        });
        if(data.hasMore === 1){
            const button = document.createElement("button")
            button.classList.add('hover-button')
            button.classList.add('load-button')
            button.innerHTML = `Load More`
            reviewContainer.append(button)
            document.querySelector('.load-button').addEventListener('click', function(event){
                offset += 1
                this.remove();
                fetch("/get-reviews", {
                    method : "POST",
                    headers : {
                        "Content-Type" : "application/json"
                    },
                    body : JSON.stringify({ id : id , offset : offset})
                })
                .then(response => response.json())
                .then(data => {
                    loadReviews(data)
                })
            })
        }
    }
})