// var serverUrl = 'http://127.0.0.1:8000/api/v1'
// var serverUrl = 'https://energy.qidoctor.ru/api/v1'
var serverUrl = '/api/v1'

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
        }

        burger.addEventListener("click", () => {
            addBurgerClasses()
        })
        cover.addEventListener("click", () => {
            addBurgerClasses()
        })
    }
}

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

// document.addEventListener("keydown", function (e) {
//     if (e.which === 27) {
//         const popupActive = document.querySelector(".modal.open");
//         popupClose(popupActive);
//     }
// })


//videos_list/{номер комплекса}


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


const urlPath = window.location.pathname;
const modalVideos = document.querySelectorAll('.slide');
const modalVideoBox = document.querySelector(".swiper-wrapper");
const modalNewLevel = document.querySelector('.new-level-box');
const swiperButtonPrev = document.querySelector(".swiper-button-prev")
const swiperButtonNext = document.querySelector(".swiper-button-next")


function modalVideoControls() {

    modalVideoBox?.addEventListener("click", (evt) => {
        if (evt.target.dataset.disabled) {
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
                if (videoId?.classList.contains('viewed')) {
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
    if (modalVideoDisabled.classList.contains("slide__disabled")) {
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
        if (index == 0) {
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

            if (index < lengthArrVideo) {
                // имитируем клик по кнопке для переключения слайда после того, как видео закорнчилось
                swiperButtonNext.click();

                // нашли следующее видео для воспроизведения в массиве и нашли id
                let nextVideo = modalVideos[index + 1];
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
                console.log(result);

                let levelUpForModal = result.new_level;
                let levelUp = result.level_up;

                console.log(levelUpForModal);

                // Слушаем модальное окно new-level
                let close = modalNewLevel?.querySelector(".new-level__close");
                let repeatViewingBtn = modalNewLevel?.querySelector(".new-level__repeat-btn");
                let newLevelHeaderLevel = modalNewLevel?.querySelector(".new-level_header-level");
                let newLevelHeader = modalNewLevel?.querySelector(".new-level_header");
                let bigred = modalNewLevel?.querySelector(".bigred");

                if (levelUp === true) {
                    newLevelHeaderLevel.textContent = levelUpForModal;
                    bigred.textContent = levelUpForModal;
                } else {
                    newLevelHeader.textContent = "Просмотрено повторно";
                }


                function closeModalNewLevelHandler() {
                    modalNewLevel.classList.add("hidden");

                    for (let i = 0; i < modalVideos.length; i++) {
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












