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
function editUserName() {
   const userNameLabel = document.querySelector('.user-profile__name_label')
   if (userNameLabel) {
      userNameLabel.addEventListener("click", () => {
         const userNameInput = userNameLabel.control;
         userNameInput.disabled = false;
      })
   }
}
// slider
function sliderWork() {
   const chargingSlider = document.querySelector('.charging-slider')
   if (chargingSlider) {
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
editUserName()
activeInputs()
showPassword()
makeBurgerMenu()
sliderWork()



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



// // video
function controlsVideo() {
   const chargingVideoWrapper = document.querySelector('.charging-video__wrapper')
   const chargingVideo = document.querySelector('.charging-video');
   const playButtonVideo = document.querySelector('.charging-video__play');
   const pauseButtonVideo = document.querySelector('.charging-video__pause');
   if (chargingVideo && playButtonVideo && pauseButtonVideo) {
      chargingVideoWrapper.addEventListener("click", (e) => {
         if (e.target.closest(".charging-video__play")) {
            playButtonVideo.classList.add("hidden")
            chargingVideo.play()
            pauseButtonVideo.classList.remove("hidden")
         }
         if (e.target.closest(".charging-video__pause")) {
            pauseButtonVideo.classList.add("hidden")
            chargingVideo.pause()
            playButtonVideo.classList.remove("hidden")
         }
      })
      chargingVideo.addEventListener("ended", () => {
         playButtonVideo.classList.remove("hidden")
         pauseButtonVideo.classList.add("hidden")
         popupOpen(document.getElementById("successCharge"))
      })
   }
}
controlsVideo()