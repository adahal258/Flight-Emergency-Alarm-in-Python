document.querySelectorAll('.thumbnails img').forEach(thumbnail => {
    thumbnail.addEventListener('click', function() {
        document.querySelector('.main-image').src = this.src;
    });
});
