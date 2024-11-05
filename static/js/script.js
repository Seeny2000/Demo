const track = document.querySelector('.carousel-track');
const slides = Array.from(track.children);
const prevButton = document.querySelector('.prev');
const nextButton = document.querySelector('.next');
const slideCount = slides.length;

let currentIndex = 0;

function moveToSlide(index) {
    const slideWidth = slides[index].getBoundingClientRect().width;
    track.style.transform = `translateX(-${slideWidth * index}px)`;
}

function autoplay() {
    currentIndex = (currentIndex + 1) % slideCount;
    moveToSlide(currentIndex);
}

function goToPrevSlide() {
    currentIndex = (currentIndex - 1 + slideCount) % slideCount;
    moveToSlide(currentIndex);
}

function goToNextSlide() {
    currentIndex = (currentIndex + 1) % slideCount;
    moveToSlide(currentIndex);
}

prevButton.addEventListener('click', () => {
    goToPrevSlide();
    resetAutoplay();
});

nextButton.addEventListener('click', () => {
    goToNextSlide();
    resetAutoplay();
});

let autoplayInterval = setInterval(autoplay, 3000); // Change slide every 3 seconds

function resetAutoplay() {
    clearInterval(autoplayInterval);
    autoplayInterval = setInterval(autoplay, 3000); // Restart autoplay
}
