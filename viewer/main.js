$(function () {
    const container   = $('.background-container');
    const scrollRight = $('.scroll-right');
    const scrollLeft  = $('.scroll-left');
    const step        = 10;
    const stepDelay   = 10;
    let isScrolling   = -1;


    function stepRight() {
        let pos      = container.scrollLeft() + step;
        if (pos >= container.width()) {
            pos = pos - container.width();
        }
        container.scrollLeft(pos);
    }

    function stepLeft() {
        let pos = container.scrollLeft() - step;
        if (pos <= 0) {
            pos = container.width() + pos;
        }
        container.scrollLeft(pos);
    }

    scrollRight.on('click', stepRight);

    scrollRight.on('mousedown', () => {
        if (isScrolling == -1) {
            isScrolling = setInterval(stepRight, stepDelay)
        }
    });

    scrollRight.on('mouseup', () => {
        if (isScrolling != -1) {
            clearInterval(isScrolling);
            isScrolling = -1;
        }
    });

    scrollLeft.on('click', stepLeft);

    scrollLeft.on('mousedown', () => {
        if (isScrolling == -1) {
            isScrolling = setInterval(stepLeft, stepDelay)
        }
    });

    scrollLeft.on('mouseup', () => {
        if (isScrolling != -1) {
            clearInterval(isScrolling);
            isScrolling = -1;
        }
    });


});