function toggleDiff(e) {
    var onlyDiff = e.target.value === '1',
        exampleNumber = e.target.dataset.example,
        exampleEl = document.getElementById('markupexamples' + exampleNumber);
    if (onlyDiff) {
        exampleEl.classList.add('onlydiff');
    }
    else {
        exampleEl.classList.remove('onlydiff');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    var els = document.querySelectorAll('.switchdiff'),
        i = els.length;
    while (i--) {
        els[i].addEventListener('change', toggleDiff);
    }
});
