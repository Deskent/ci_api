// var serverUrl = 'http://127.0.0.1:8000/api/v1'
// var serverUrl = 'https://energy.qidoctor.ru/api/v1'
const serverUrl = '/api/v1'

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