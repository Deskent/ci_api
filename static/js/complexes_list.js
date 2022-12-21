const urlPath = window.location.pathname;

let complexesListNumberComplex = document?.querySelector(".complexes-list__number-complex");

let complexesListSlide = document?.querySelectorAll(".complexes-list__wrapper");
let complexesListSlideArr = Array.from(complexesListSlide);

let btns = document?.querySelectorAll(".complexes-list-slide__btn-box");
const btnsArr = Array.from(btns);

let modal = document?.querySelector(".new-level-box");
let close = modal?.querySelector(".new-level__close");

let repeatViewingBtn = modal?.querySelector(".new-level__repeat-btn");

// Отправляем fetch-запрос после загрузки страницы complexes_list
if (urlPath.includes("complexes_list")) {
    document.addEventListener("DOMContentLoaded", async (evt) => {
        const response = await fetch(serverUrl + '/web/complex/list', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json;charset=utf-8',
            },
        });

        let result = await response.json();
        // console.log(result);

        const levelUser = await result.user.level;
        const todayComplex = result.today_complex;
        const viewedComplexes = await result.viewed_complexes;

        complexesListNumberComplex.textContent = " " + levelUser;


        for (let i = 0; i <= complexesListSlideArr.length - 1; i++) {

            let item = complexesListSlideArr[i];

            if (i < levelUser) {
                item.querySelector('.complexes-list-slide__lock').style.display = "none";
                item.querySelector('.complexes-list-slide__btn-box').style.display = "flex";
                item.querySelector('.complexes-list-image').classList.remove('lock');
            }
            if (i < viewedComplexes.length) {
                item.querySelector('.complexes-list-slide__btn-text').textContent = "Просмотрено";
                item.querySelector('.complexes-list-image').classList.add("lock");
                complexesListSlideArr[i + 1].querySelector(".complexes-list-slide__btn-box").classList.add("active-btn");

            }
            if (i == todayComplex.length) {
                item.querySelector('.complexes-list-slide__btn-text').textContent = "Посмотреть";
            }

        }

        let next = Object.keys(todayComplex).length;

        btnsArr.forEach((el) => {
            el.addEventListener("click", (evt) => {
                if ((el.classList.contains("active-btn") && next === 0)) {
                    evt.preventDefault();
                    evt.stopPropagation();
                    modal.classList.remove("hidden");
                }
            })
        })

        close?.addEventListener("click", closeModalNewLevelHandler);


    })
}


// Инициализируем слайдер для комплексов
let swiper1 = new Swiper(".mySwiperComplex", {
    slidesPerView: 3,
    spaceBetween: 30,
    speed: 400,
    grabCursor: true,
    //отключение функционала, если слайдов меньше чем нужно
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