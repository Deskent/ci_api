// Слушаем модальное окно new-level для комплекс лист

const helloVideo = document?.querySelector('.hello-video');
 
function closeModalNewLevelHandler() {
  modal.classList.add("hidden");

  if(slides) {
    for (let i = 0; i < slides.length; i++) {
      swiperButtonPrev.click();
    }
  }

  if(helloVideo) {
    helloVideo.remove();
  }
}

document.addEventListener("keydown", function (evt) {
  if (evt.keyCode === 27) {
      modal.classList.add("hidden");
  }
})


function openModalNewLevelHandler() {
  modal.classList.remove("hidden");
}







