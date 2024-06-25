document.addEventListener("DOMContentLoaded", function(event){
    genreButtons = document.querySelectorAll(".redirect-catalogue")
    genreButtons.forEach(button => {
        button.addEventListener('click', function(event){
            window.location.href = `/catalogue?search=${button.getAttribute('id')}`
            console.log("test")
        })
    })
})