const close_anchors = document.querySelectorAll('.close');

if (close_anchors.length > 0) {
    close_anchors.forEach(function (close_anchor) {
        close_anchor.addEventListener('click', function () {
            close_anchor.parentElement.remove()
        })
    })
}