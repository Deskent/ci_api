(function isWebP() {
    function testWebP(callback) {
        let webP = new Image();
        webP.onload = webP.onerror = function () {
            callback(webP.height == 2);
        };
        webP.src = "data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA";
    }

    testWebP(function (support) {

        if (support == true) {
            document.querySelector('html').classList.add('webp');
        } else {
            document.querySelector('html').classList.add('no-webp');
        }
    });
})()

function activeInputs() {
    const registrationLabels = document.querySelectorAll('.registration__label');
    if (registrationLabels.length > 0) {
        registrationLabels.forEach(label => {
            label.addEventListener("click", () => {
                registrationLabels.forEach(item => {
                    item.classList.remove("active")
                    const input = item.querySelector("input")
                    if (input.value) {
                        item.classList.add("filled")
                    } else {
                        item.classList.remove("filled")
                    }
                })
                label.classList.add("active")
            })
        })
    }
}

// было registration__input_password_btn

function showPassword() {
    const viewPasswordBtn = document.querySelectorAll('.password__show')
    viewPasswordBtn.forEach((item) => {
        if (item) {
            item.addEventListener("click", (evt) => {
                const input = evt.target.parentNode.querySelector('input');
                if (input.type == 'password') {
                    input.type = "text"
                } else {
                    input.type = "password"
                }
            })
        }
    })
}

function makeBurgerMenu() {
    const burger = document.querySelector('.profile-header__burger');
    const menu = document.querySelector('.header-menu')
    const body = document.querySelector('body')
    const cover = document.querySelector('.profile-header__cover')
    if (burger && menu && cover) {
        function addBurgerClasses() {
            burger.classList.toggle("active")
            menu.classList.toggle("active")
            cover.classList.toggle("active")
            // body.classList.toggle("lock")
        }

        burger.addEventListener("click", () => {
            addBurgerClasses()
        })
        cover.addEventListener("click", () => {
            addBurgerClasses()
        })
    }
}

activeInputs()
showPassword()
makeBurgerMenu()


// Popup
// const popupLinks = document.querySelectorAll(".modal__link");
// const body = document.querySelector("body");
// const lockPadding = document.querySelectorAll(".lock-padding");
// const popupCloseIcon = document.querySelectorAll(".modal__close");

// let unlock = true;

// const timeout = 500;

// if (popupLinks.length > 0) {
//     for (let index = 0; index < popupLinks.length; index++) {
//         const popupLink = popupLinks[index];
//         popupLink.addEventListener("click", function (e) {
//             const popupName = popupLink.getAttribute('href').replace('#', '');
//             const curentPopup = document.getElementById(popupName);
//             popupOpen(curentPopup);
//             e.preventDefault();
//         });
//     }
// }

// if (popupCloseIcon.length > 0) {
//     for (let index = 0; index < popupCloseIcon.length; index++) {
//         const el = popupCloseIcon[index];
//         el.addEventListener("click", function (e) {
//             popupClose(el.closest(".modal"));
//             e.preventDefault();
//         });
//     }
// }

// function popupOpen(curentPopup) {
//     if (curentPopup && unlock) {
//         const popupActive = document.querySelector(".modal.open");
//         if (popupActive) {
//             popupClose(popupActive, false);
//         } else {
//             bodyLock();
//         }
//         curentPopup.classList.add("open");
//         curentPopup.addEventListener("click", function (e) {
//             if (!e.target.closest(".modal__content")) {
//                 popupClose(e.target.closest(".modal"));
//             }
//         })
//     }
// }

// function popupClose(popupActive, doUnlock = true) {
//     if (unlock) {
//         popupActive.classList.remove("open");
//         if (doUnlock) {
//             bodyUnLock();
//         }
//     }
// }

// function bodyLock() {
//     const lockPaddingValue = "17px";

//     if (lockPadding.length > 0) {
//         for (let index = 0; index < lockPadding.length; index++) {
//             const el = lockPadding[index];
//             el.style.paddingRight = lockPaddingValue;
//         }
//     }
//     body.style.paddingRight = lockPaddingValue;
//     body.classList.add("lock");


//     unlock = false;
//     setTimeout(function () {
//         unlock = true;
//     }, timeout);
// }

// function bodyUnLock() {
//     setTimeout(function () {
//         if (lockPadding.length > 0) {
//             for (let index; index < lockPadding.length; index++) {
//                 const el = lockPadding[index];
//                 el.style.paddingRight = "0px";
//             }
//         }
//         body.style.paddingRight = "0px";
//         body.classList.remove("lock");
//     }, timeout);

//     unlock = false;
//     setTimeout(function () {
//         unlock = true;
//     }, timeout)
// }

document.addEventListener("keydown", function (e) {
    if (e.which === 27) {
        const popupActive = document.querySelector(".modal.open");
        popupClose(popupActive);
    }
})















































//videos_list/{номер комплекса}











// Инициализируем слайдер для упражнений
   let swiper = new Swiper(".mySwiper", {
      slidesPerView: 3,
      // centeredSlides: true,
      spaceBetween: 60,
      speed: 400,
      grabCursor: true,
      autoHeight: true,
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




const urlPath = window.location.pathname;
const modalVideos = document.querySelectorAll('.slide');
const modalVideoBox = document.querySelector(".swiper-wrapper");
const modalNewLevel = document.querySelector('.new-level-box');
const swiperButtonPrev = document.querySelector(".swiper-button-prev")
const swiperButtonNext = document.querySelector(".swiper-button-next")



function modalVideoControls() {

      modalVideoBox?.addEventListener("click", (evt) => {
         if(evt.target.dataset.disabled) {
            evt.preventDefault();
         } else {

         let targetVideoId = evt.target.dataset.id;
         let videoId = document.getElementById(targetVideoId);

         let modalVideoWrapperId = videoId?.closest(".slide__card-wrapper");
         let modalVideoPlay = modalVideoWrapperId?.querySelector('.slide__play');
         let modalVideoPause = modalVideoWrapperId?.querySelector('.slide__pause');
         let modalVideoViewed = modalVideoWrapperId?.querySelector('.slide__viewed');
         let modalVideoTime = modalVideoWrapperId?.querySelector('.slide__time');
         let modalVideoTitle = modalVideoWrapperId?.querySelector('.slide__title');
         let modalVideoDescription = modalVideoWrapperId?.querySelector('.slide__description');


        if (modalVideoPause?.classList.contains('hidden')) {
            modalVideoPlay?.classList.add("hidden");
            videoId?.play();
            if(videoId?.classList.contains('viewed')) {
               videoId?.classList.remove("viewed");
            }
            modalVideoPause?.classList.remove("hidden");
            modalVideoViewed?.classList.add("hidden");
            modalVideoTime?.classList.add("hidden");
            modalVideoTitle?.classList.add("hidden");
            modalVideoDescription?.classList.add("hidden");

        } else {
            modalVideoPlay?.classList.remove("hidden");
            videoId?.pause();
            modalVideoPause?.classList.add("hidden");
            modalVideoViewed?.classList.remove("hidden");
            modalVideoTime?.classList.remove("hidden");
            modalVideoViewed?.classList.add("hidden");

         }
      }
   })
}

modalVideoControls();





// меняет стили на "видео просмотрено"

function changesStylesViewed(evt) {
   let targetModalVideoEnded = evt.target.dataset.id;

   let videoIdEnded = document.getElementById(targetModalVideoEnded);
   let modalVideoWrapperId = videoIdEnded.closest(".slide__card-wrapper");

   let modalVideoPlay = modalVideoWrapperId.querySelector('.slide__play');
   let modalVideoPause = modalVideoWrapperId.querySelector('.slide__pause');
   let modalVideoViewedHidden = modalVideoWrapperId.querySelector('.slide__viewed');
   let modalVideoTitle = modalVideoWrapperId.querySelector('.slide__title');
   let modalVideoDescription = modalVideoWrapperId.querySelector('.slide__description');
   let modalVideoTime = modalVideoWrapperId.querySelector('.slide__time');

   modalVideoTime.classList.remove("hidden");
   modalVideoViewedHidden.classList.remove("hidden");


   let viewedTag = modalVideoViewedHidden.querySelector(".slide__viewed-text");
   viewedTag.textContent = "Упражнение выполнено";
   viewedTag.style.fontSize = "17px";
   modalVideoViewedHidden.querySelector(".slide__viewed-img").src = "/static/img/icons/plus.svg";






   videoIdEnded.classList.add("viewed");
   modalVideoPlay.classList.remove("hidden");
   modalVideoPause.classList.add("hidden");
   modalVideoTitle.classList.remove("hidden");
   modalVideoDescription.classList.remove("hidden");
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

   video.play();

   let videoNextWrapper = video.closest(".slide__card-wrapper");
   let modalVideoDisabled = videoNextWrapper.querySelector(".slide__disabled");
   if(modalVideoDisabled.classList.contains("slide__disabled")) {
      modalVideoDisabled.style.display = "none";
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
   videoViewed.classList.add("hidden");
   videoTime.classList.add("hidden");
   videoTitle.classList.add("hidden");
   videoDescription.classList.add("hidden");
}



// Слушаем закончилось ли видео?
function modalVideoEnded() {

   modalVideos.forEach((video, index, arr) => {
      // у первого видео сняли блокировку
      if(index == 0 ) {
         video.classList.remove("lock");
         let modalVideoWrapper = video.closest(".slide__card-wrapper");
         let modalVideoDisabled = modalVideoWrapper.querySelector(".slide__disabled");
         let modalVideoViewed = modalVideoWrapper.querySelector(".slide__viewed");
         modalVideoViewed.classList.add("hidden");
         modalVideoDisabled.style.display = "none";
         modalVideoDisabled.removeAttribute("data-disabled")
      }

        video.addEventListener("ended", async (evt) => {


         changesStylesViewed(evt); // поменяли стили на "видео просмотрено"

         const lengthArrVideo = modalVideos.length - 1;

         if(index < lengthArrVideo) {
            // имитируем клик по кнопке для переключения слайда после того, как видео закорнчилось
            swiperButtonNext.click();

            // нашли следующее видео для воспроизведения в массиве и нашли id
            let nextVideo = modalVideos[index + 1];
            let nextVideoId = nextVideo.getAttribute("data-id");

            changeStylesToOn(nextVideoId); // поменяли стили на "видео включено"
         }


         // Если закончилось последнее видео показываем модальное окно
         if(index === lengthArrVideo) {
            if(modalNewLevel.classList.contains('hidden')) {
               modalNewLevel.classList.remove('hidden');
            }

            // Отправляем запрос после просмотра последнего видео

            const complex_id = Array.from(urlPath).pop();

            // TODO: https://energy.qidoctor.ru/api/v1/web/complex_viewed/' + complex_id запрос на сервере отправлять сюда
            // TODO: для разработки на http://127.0.0.1:8000/api/v1/web/complex_viewed/' + complex_id

                // if(complex_id === Number) {
            // const response = await fetch('http://127.0.0.1:8000/api/v1/web/complex_viewed/' + complex_id, {
                   const response = await fetch('https://energy.qidoctor.ru/api/v1/web/complex_viewed/' + complex_id, {
                    method: 'GET',
                    headers: {
                    'Content-Type': 'application/json;charset=utf-8',
                    },
                });

                let result = await response.json();
                console.log(result);

                let levelUpForModal = result.new_level;
                let levelUp = result.level_up;

                console.log(levelUpForModal);
            // }

            // Слушаем модальное окно new-level
            let close = modalNewLevel?.querySelector(".new-level__close");
            let repeatViewingBtn = modalNewLevel?.querySelector(".new-level__repeat-btn");
            let newLevelHeaderLevel = modalNewLevel?.querySelector(".new-level_header-level");
            let newLevelHeader = modalNewLevel?.querySelector(".new-level_header");

            if(levelUp === true) {
               newLevelHeaderLevel.textContent = levelUpForModal;
            } else {
               newLevelHeader.textContent = "Просмотрено повторно";
            }


            function closeModalNewLevelHandler () {
               modalNewLevel.classList.add("hidden");

               for(let i = 0; i < modalVideos.length; i++) {
                  swiperButtonPrev.click();
               }
               close.removeEventListener("click", closeModalNewLevelHandler);
               repeatViewingBtn.removeEventListener("click", closeModalNewLevelHandler);
            }

            close?.addEventListener("click", closeModalNewLevelHandler);
            repeatViewingBtn?.addEventListener("click", closeModalNewLevelHandler);
         }
      });
   })
}

modalVideoEnded();








































//complexes_list



// Слушаем модальное окно new-level для комплекс лист
let close = modalNewLevel?.querySelector(".new-level__close");

function closeModalNewLevelHandler () {
   modalNewLevel.classList.add("hidden");
}

close?.addEventListener("click", closeModalNewLevelHandler);


// Отправляем запрос после загрузки страницы complexes_list

const complexesList = urlPath;



// TODO: https://energy.qidoctor.ru/api/v1/web/complex/list запрос на сервере отправлять сюда
// TODO: для разработки на http://127.0.0.1:8000/api/v1/web/complex/list

if(complexesList.includes("complexes_list")) {
    document.addEventListener("DOMContentLoaded", async (evt) => {
        // const response = await fetch('http://127.0.0.1:8000/api/v1/web/complex/list', {
        const response = await fetch('https://energy.qidoctor.ru/api/v1/web/complex/list', {
           method: 'GET',
           headers: {
           'Content-Type': 'application/json;charset=utf-8',
           },
        });

        let result = await response.json();
        console.log(result);

        const levelUser = await result.user.level;
      //   const notViewedComplexes = result.not_viewed_complexes;
        const todayComplex = result.today_complex;
        const viewedComplexes = await result.viewed_complexes;

      let complexesListSlide = document.querySelectorAll(".complexes-list__wrapper");
      let complexesListSlideArr = Array.from(complexesListSlide);
      console.log(complexesListSlideArr);






      for(let i = 0; i <= complexesListSlideArr.length-1; i++) {

         // let idViewedComplexes = viewedComplexesArr[i];
         let item = complexesListSlideArr[i];

         console.log(item);


         if(i < levelUser) {
               item.querySelector('.complexes-list-slide__lock').style.display = "none";
               item.querySelector('.complexes-list-slide__btn-box').style.display = "flex";
               item.querySelector('.complexes-list-image').classList.remove('lock');
         }
         if(i < viewedComplexes.length) {
            item.querySelector('.complexes-list-slide__btn-text').textContent = "Просмотрено";
            complexesListSlideArr[i+1].querySelector(".complexes-list-slide__btn-box").classList.add("active-btn");
            // complexesListSlideArr[i+1].querySelector('.complexes-list-slide__btn-text').classList.add("active-btn");

         }
         if(i == todayComplex.length) {
            item.querySelector('.complexes-list-slide__btn-text').textContent = "Посмотреть";
         }

      }



      let btns = document.querySelectorAll(".complexes-list-slide__btn-box");
      const btnsArr = Array.from(btns);

      let modal = document.querySelector(".new-level-box");

      btnsArr.forEach((el, index) => {
        let next = Object.keys(todayComplex).length;
         el.addEventListener("click", (evt) => {
            if((el.classList.contains("active-btn") && next === 0) ) {
               evt.preventDefault();
               evt.stopPropagation();
               modal.classList.remove("hidden");
            }
         })

      })
    })
}






// Инициализируем слайдер для комплексов
let swiper1 = new Swiper(".mySwiperComplex", {
    slidesPerView: 3,
    spaceBetween: 30,
    speed: 400,
    grabCursor: true,
    autoHeight: true,
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

// let forgetFormInput = document.querySelectorAll(".forget-form__input");
// // console.log(forgetFormInput);

// forgetFormInput.forEach((item, index) => {
//    item.addEventListener("keydown", (evt) => {
//       // evt.preventDefault();
//       if (item.value == Number) {
//          console.log(item.value);
//          item[index + 1].focus();
//       }
//     });
// })



// Отправляем форму после того как input изменился
let formAvatar = document.querySelector(".user-profile__img-form");
let formAvatarInput = formAvatar.querySelector(".user-profile__img-input");
let formAvatarBtn =  formAvatar.querySelector(".user-profile__img-submit");

formAvatarInput.addEventListener("change" , (env) => {
   formAvatarBtn.click();
})





