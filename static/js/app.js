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

function showPassword() {
    const viewPasswordBtn = document.querySelector('.registration__input_password_btn')
    if (viewPasswordBtn) {
        viewPasswordBtn.addEventListener("click", (e) => {
            const input = e.target.parentNode.querySelector('input');
            if (input.type == 'password') {
                input.type = "text"
            } else {
                input.type = "password"
            }
        })
    }
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
            body.classList.toggle("lock")
        }

        burger.addEventListener("click", () => {
            addBurgerClasses()
        })
        cover.addEventListener("click", () => {
            addBurgerClasses()
        })
    }
}


// slider
function slider1Work() {
    const chargingSlider1 = document.querySelector('.charging-slider')
    if (chargingSlider1) {
        $(document).ready(function () {
            $('.charging-slider').slick({
                slidesToShow: 3,
                slidesToScroll: 1,
                arrows: true,
                dots: true,
                // loop: false,
                infinite: false,
                responsive: [
                    {
                        breakpoint: 769,
                        settings: {
                            arrows: false,
                        }
                    },
                    {
                        breakpoint: 651,
                        settings: {
                            slidesToShow: 1,
                            arrows: false,
                        }
                    },
                ],
            });
        });
    }

}

// slider2
function slider2Work() {
    const chargingSlider2 = document.querySelector('.complexes-list-slider')
    if (chargingSlider2) {
        $(document).ready(function () {
            $('.complexes-list-slider').slick({
                slidesToShow: 3,
                slidesToScroll: 1,
                arrows: true,
                dots: true,
                // loop: false,
                infinite: false,
                responsive: [
                    {
                        breakpoint: 769,
                        settings: {
                            arrows: false,
                        }
                    },
                    {
                        breakpoint: 651,
                        settings: {
                            slidesToShow: 1,
                            arrows: false,
                        }
                    },
                ],
            });
        });
    }

}

// editUserName()
activeInputs()
showPassword()
makeBurgerMenu()
slider1Work()
slider2Work()


// Popup
const popupLinks = document.querySelectorAll(".modal__link");
const body = document.querySelector("body");
const lockPadding = document.querySelectorAll(".lock-padding");
const popupCloseIcon = document.querySelectorAll(".modal__close");

let unlock = true;

const timeout = 500;

if (popupLinks.length > 0) {
    for (let index = 0; index < popupLinks.length; index++) {
        const popupLink = popupLinks[index];
        popupLink.addEventListener("click", function (e) {
            const popupName = popupLink.getAttribute('href').replace('#', '');
            const curentPopup = document.getElementById(popupName);
            popupOpen(curentPopup);
            e.preventDefault();
        });
    }
}


if (popupCloseIcon.length > 0) {
    for (let index = 0; index < popupCloseIcon.length; index++) {
        const el = popupCloseIcon[index];
        el.addEventListener("click", function (e) {
            popupClose(el.closest(".modal"));
            e.preventDefault();
        });
    }
}


function popupOpen(curentPopup) {
    if (curentPopup && unlock) {
        const popupActive = document.querySelector(".modal.open");
        if (popupActive) {
            popupClose(popupActive, false);
        } else {
            bodyLock();
        }
        curentPopup.classList.add("open");
        curentPopup.addEventListener("click", function (e) {
            if (!e.target.closest(".modal__content")) {
                popupClose(e.target.closest(".modal"));
            }
        })
    }
}

function popupClose(popupActive, doUnlock = true) {
    if (unlock) {
        popupActive.classList.remove("open");
        if (doUnlock) {
            bodyUnLock();
        }
    }
}

function bodyLock() {
    const lockPaddingValue = "17px";

    if (lockPadding.length > 0) {
        for (let index = 0; index < lockPadding.length; index++) {
            const el = lockPadding[index];
            el.style.paddingRight = lockPaddingValue;
        }
    }
    body.style.paddingRight = lockPaddingValue;
    body.classList.add("lock");


    unlock = false;
    setTimeout(function () {
        unlock = true;
    }, timeout);
}

function bodyUnLock() {
    setTimeout(function () {
        if (lockPadding.length > 0) {
            for (let index; index < lockPadding.length; index++) {
                const el = lockPadding[index];
                el.style.paddingRight = "0px";
            }
        }
        body.style.paddingRight = "0px";
        body.classList.remove("lock");
    }, timeout);

    unlock = false;
    setTimeout(function () {
        unlock = true;
    }, timeout)
}


document.addEventListener("keydown", function (e) {
    if (e.which === 27) {
        const popupActive = document.querySelector(".modal.open");
        popupClose(popupActive);
    }
})


// Сториз рилз


function modalVideoControls() {
    const modalVideoBox = document.querySelector('.modal-video__box');

    modalVideoBox.addEventListener("click", (evt) => {

        let targetVideoId = evt.target.dataset.id;

        let videoId = document.getElementById(targetVideoId);
        console.log(videoId);


        let modalVideoWrapperId = videoId.closest(".modal-video__card-wrapper");
        let modalVideoPlay = modalVideoWrapperId.querySelector('.modal-video__play');
        let modalVideoPause = modalVideoWrapperId.querySelector('.modal-video__pause');
        let modalVideoViewed = modalVideoWrapperId.querySelector('.modal-video__viewed');
        let modalVideoTime = modalVideoWrapperId.querySelector('.modal-video__time');
        let modalVideoTitle = modalVideoWrapperId.querySelector('.modal-video__title');
        let modalVideoDescription = modalVideoWrapperId.querySelector('.modal-video__description');


        if (modalVideoPause.classList.contains('hidden')) {
            modalVideoPlay.classList.add("hidden");
            if (videoId.classList.contains('viewed')) {
                videoId.classList.remove("viewed");
            }
            videoId.play();
            modalVideoPause.classList.remove("hidden");
            modalVideoViewed.classList.add("hidden");
            modalVideoTime.classList.add("hidden");
            modalVideoTitle.classList.add("hidden");
            modalVideoDescription.classList.add("hidden");

        } else {
            modalVideoPlay.classList.remove("hidden");
            videoId.pause();
            modalVideoPause.classList.add("hidden");
            modalVideoViewed.classList.remove("hidden");
            modalVideoTime.classList.remove("hidden");

        }
    })
}

modalVideoControls();


// Закончилось ли видео?
function modalVideoEnded() {
    const modalVideos = document.querySelectorAll('.modal-video');

    modalVideos.forEach((video, index, arr) => {

        if (index == 0) {
            video.classList.remove("lock");
        }

        video.addEventListener("ended", async (evt) => {

            const video_id = Number(evt.target.dataset.id);
            let userPhone = document.querySelector('.header-user__phone');
            const user_tel = userPhone.textContent;
            const phone = user_tel.replace(/\s/g, '');

            const response = await fetch('https://energy.qidoctor.ru/api/v1/videos/viewed', {
                method: 'POST',
                body: JSON.stringify({
                    "phone": phone,
                    "video_id": video_id
                }),
                headers: {
                    'Content-Type': 'application/json;charset=utf-8'
                },
            });

            let result = await response.json();

            const lengthArrVideo = modalVideos.length - 1;

            //нашли следующее видео для воспроизведения
            if (index < lengthArrVideo) {
                const modalNextVideos = document.getElementById(result.next_video_id);
                modalNextVideos.play();
                let modalVideoNextWrapperId = modalNextVideos.closest(".modal-video__card-wrapper");
                let modalNextVideosPlay = modalVideoNextWrapperId.querySelector('.modal-video__play');
                let modalNextVideosPause = modalVideoNextWrapperId.querySelector('.modal-video__pause');
                let modalVideoNextLock = modalVideoNextWrapperId.querySelector('.modal-video.lock');
                let modalVideoViewed = modalVideoNextWrapperId.querySelector('.modal-video__viewed');
                let modalVideoTime = modalVideoNextWrapperId.querySelector('.modal-video__time');

                modalNextVideosPlay.classList.add("hidden");
                modalNextVideosPause.classList.remove("hidden");
                modalVideoNextLock.classList.remove("lock");
                modalVideoViewed.classList.add("hidden");
                modalVideoTime.classList.add("hidden");
            }

            const modalNewLevel = document.querySelector('.new-level-box');


            if (index === lengthArrVideo) {
                if (modalNewLevel.classList.contains('hidden')) {
                    modalNewLevel.classList.remove('hidden');
                }
            }

            // поменяли стили на "видео просмотрено"
            let targetModalVideoEnded = evt.target.dataset.id;
            console.log("Видео " + targetModalVideoEnded + " просмотрено!");

            let videoIdEnded = document.getElementById(targetModalVideoEnded);
            let modalVideoWrapperId = videoIdEnded.closest(".modal-video__card-wrapper");

            let modalVideoPlay = modalVideoWrapperId.querySelector('.modal-video__play');
            let modalVideoPause = modalVideoWrapperId.querySelector('.modal-video__pause');
            let modalVideoViewedHidden = modalVideoWrapperId.querySelector('.modal-video__viewed');
            let modalVideoTitle = modalVideoWrapperId.querySelector('.modal-video__title');
            let modalVideoDescription = modalVideoWrapperId.querySelector('.modal-video__description');
            let modalVideoTime = modalVideoWrapperId.querySelector('.modal-video__time');

            modalVideoTime.classList.remove("hidden");
            modalVideoViewedHidden.classList.remove("hidden");
            modalVideoViewedHidden.textContent = "Просмотрено"
            videoIdEnded.classList.add("viewed");
            modalVideoPlay.classList.remove("hidden");
            modalVideoPause.classList.add("hidden");
            modalVideoTitle.classList.remove("hidden");
            modalVideoDescription.classList.remove("hidden");

        });
    })
}

modalVideoEnded();
