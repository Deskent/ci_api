// Инициализируем слайдер для упражнений
let swiper = new Swiper(".mySwiper", {
  slidesPerView: 3,
  // centeredSlides: true,
  spaceBetween: 60,
  speed: 400,
  grabCursor: true,
  // autoHeight: true,
  //отключение функционала если слайдов меньше чем нужно
  watchOverflow: true,

  device: {
      ios: true,
      android: true
  },

  pagination: {
      el: ".swiper-pagination",
      clickable: true,
  },
  navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
  },
  keyboard: {
      enabled: true,
      onlyInViewport: true,
  },
  breakpoints: {
      50: {
          slidesPerView: 1,
      },
      480: {
          slidesPerView: 2,
      },
      768: {
          slidesPerView: 3,
      }
  }
});


const slides = document?.querySelectorAll('.slide');
const slideBox = document?.querySelector(".swiper-wrapper");
const modalNewLevel = document?.querySelector('.new-level-box');
const swiperButtonPrev = document?.querySelector(".swiper-button-prev")
const swiperButtonNext = document?.querySelector(".swiper-button-next")


function slideControls() {

  slideBox?.addEventListener("click", (evt) => {
      if (evt.target.dataset.disabled) {
          evt.preventDefault();

      } else {

          let targetVideoId = evt.target.dataset.id;
          let videoId = document.getElementById(targetVideoId);

          let slideWrapperId = videoId?.closest(".slide__card-wrapper");
          let slidePlay = slideWrapperId?.querySelector('.slide__play');
          let slidePause = slideWrapperId?.querySelector('.slide__pause');
          let slideViewed = slideWrapperId?.querySelector('.slide__viewed');
          let slideTime = slideWrapperId?.querySelector('.slide__time');
          let slideTitle = slideWrapperId?.querySelector('.slide__title');
          let slideDescription = slideWrapperId?.querySelector('.slide__description');

          if (slidePause?.classList.contains('hidden')) {
              slidePlay?.classList.add("hidden");
              videoId?.play();
              if (videoId?.classList.contains('viewed')) {
                  videoId?.classList.remove("viewed");
              }
              if (videoId?.classList.contains('lock-video')) {
                  videoId?.classList.remove('lock-video');
              }
              slidePause?.classList.remove("hidden");
              slideViewed?.classList.add("hidden");
              slideTime?.classList.add("hidden");
              slideTitle?.classList.add("hidden");
              slideDescription?.classList.add("hidden");

          } else {
              slidePlay?.classList.remove("hidden");
              videoId?.pause();
              slidePause?.classList.add("hidden");
              slideViewed?.classList.remove("hidden");
              slideTime?.classList.remove("hidden");
              slideViewed?.classList.add("hidden");

          }
      }
  })
}

slideControls();


// меняет стили на "видео просмотрено"
function changesStylesViewed(evt) {
  let targetSlideEnded = evt.target.dataset.id;

  let videoIdEnded = document.getElementById(targetSlideEnded);
  let slideWrapperId = videoIdEnded.closest(".slide__card-wrapper");

  let slidePlay = slideWrapperId.querySelector('.slide__play');
  let slidePause = slideWrapperId.querySelector('.slide__pause');
  let slideViewedHidden = slideWrapperId.querySelector('.slide__viewed');
  let slideTitle = slideWrapperId.querySelector('.slide__title');
  let slideDescription = slideWrapperId.querySelector('.slide__description');
  let slideTime = slideWrapperId.querySelector('.slide__time');
  let slide = slideWrapperId?.querySelector('.slide');

  

  slideTime.classList.remove("hidden");
  slideViewedHidden.classList.remove("hidden");
  if(!slide.classList.contains("lock-video")) {
      slide?.classList.add("lock-video");
  }

  let viewedTag = slideViewedHidden.querySelector(".slide__viewed-text");
  viewedTag.textContent = "Упражнение выполнено";
  viewedTag.style.fontSize = "17px";
  slideViewedHidden.querySelector(".slide__viewed-img").src = "/static/img/icons/plus.svg";


  videoIdEnded.classList.add("viewed");
  slidePlay.classList.remove("hidden");
  slidePause.classList.add("hidden");
  slideTitle.classList.remove("hidden");
  slideDescription.classList.remove("hidden");
}

// менят стили на "видео включено" у следующего видео в массиве по id
function changeStylesToOn(nextVideoId) {
  let videoSlidesNodeList = document.querySelectorAll(".slide__card-wrapper");
  let videoSlidesArr = Array.from(videoSlidesNodeList);
  let indexVideo;
  videoSlidesArr.forEach((element, index) => {
      let attributeIdValue = element.getAttribute("data-id");
      if (attributeIdValue == nextVideoId) {
          indexVideo = index;
      }
  })

  let videoWrapper = videoSlidesArr[indexVideo];
  let video = videoWrapper.querySelector(".slide");

  if (video.classList.contains("lock-video")) {
      video.classList.remove("lock-video");
  }
  
  video.play();

  let videoNextWrapper = video.closest(".slide__card-wrapper");
  let slideDisabled = videoNextWrapper.querySelector(".slide__disabled");
  if (slideDisabled.classList.contains("slide__disabled")) {
      slideDisabled.style.display = "none";
  }

  let nextVideosPlay = videoNextWrapper.querySelector('.slide__play');
  let nextVideosPause = videoNextWrapper.querySelector('.slide__pause');
  let videoNextLock = videoNextWrapper.querySelector('.slide');
  let videoViewed = videoNextWrapper.querySelector('.slide__viewed');
  let videoTime = videoNextWrapper.querySelector('.slide__time');
  let videoTitle = videoNextWrapper.querySelector('.slide__title');
  let videoDescription = videoNextWrapper.querySelector('.slide__description');

  nextVideosPlay.classList.add("hidden");
  nextVideosPause.classList.remove("hidden");

  if (videoNextLock.classList.contains("lock")) {
      videoNextLock.classList.remove("lock");
  }
  if (videoNextLock.classList.contains("viewed")) {
      videoNextLock.classList.remove("viewed");
  }
  if (videoNextLock.classList.contains("lock-video")) {
      videoNextLock.classList.remove("lock-video");
  }
  videoViewed.classList.add("hidden");
  videoTime.classList.add("hidden");
  videoTitle.classList.add("hidden");
  videoDescription.classList.add("hidden");
}


// Слушаем закончилось ли видео?
function slideEnded() {

  slides.forEach((video, index, arr) => {
      // у первого видео сняли блокировку
      if (index == 0) {
          video.classList.remove("lock");
          let slideWrapper = video.closest(".slide__card-wrapper");
          let slideDisabled = slideWrapper.querySelector(".slide__disabled");
          let slideViewed = slideWrapper.querySelector(".slide__viewed");
          slideViewed.classList.add("hidden");
          slideDisabled.style.display = "none";
          slideDisabled.removeAttribute("data-disabled")
      }

      video.addEventListener("ended", async (evt) => {
          changesStylesViewed(evt); // поменяли стили на "видео просмотрено"

          const lengthArrVideo = slides.length - 1;

          if (index < lengthArrVideo) {
              // имитируем клик по кнопке для переключения слайда после того, как видео закорнчилось
              swiperButtonNext.click();

              // нашли следующее видео для воспроизведения в массиве по id
              let nextVideo = slides[index + 1];
              let nextVideoId = nextVideo.getAttribute("data-id");

              changeStylesToOn(nextVideoId); // поменяли стили на "видео включено"
          }

          // Если закончилось последнее видео показываем модальное окно
          if (index === lengthArrVideo) {
              if (modalNewLevel.classList.contains('hidden')) {
                  modalNewLevel.classList.remove('hidden');
              }

              // Отправляем запрос после просмотра последнего видео
              const complex_id = Array.from(urlPath).pop();
              const response = await fetch(serverUrl + '/web/complex_viewed/' + complex_id, {
                  method: 'GET',
                  headers: {
                      'Content-Type': 'application/json;charset=utf-8',
                  },
              });

              let result = await response.json();

              let levelUpForModal = result.new_level;
              let levelUp = result.level_up;


              // Слушаем модальное окно new-level
              let newLevelHeaderLevel = modalNewLevel?.querySelector(".new-level_header-level");
              let newLevelHeader = modalNewLevel?.querySelector(".new-level_header");
              let bigred = modalNewLevel?.querySelector(".bigred");
              let repeatViewingBtn = modalNewLevel?.querySelector(".new-level__repeat-btn");


              if (levelUp === true) {
                  newLevelHeaderLevel.textContent = levelUpForModal;
                  bigred.textContent = levelUpForModal;
              } else {
                  newLevelHeader.textContent = "Просмотрено повторно";
              }
              

              openModalNewLevelHandler();
              close?.addEventListener("click", closeModalNewLevelHandler);
              repeatViewingBtn?.addEventListener("click", closeModalNewLevelHandler);
          }
      });
  })
}

slideEnded();
