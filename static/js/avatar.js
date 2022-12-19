const imageInput = document.querySelector(".user-profile__img-input");
const image = document.querySelector(".user-profile__img");
const imageWrapper = document.querySelector(".user-profile__image-wrapper");

// загружаем фото user и тут же его просматриваем без отправки на сервер, это нужно для редактирования с помощью Croppie
var uploadedImage = "";

imageInput?.addEventListener("change", function () {
    console.log(imageInput.value);
    const reader = new FileReader();
    reader.addEventListener("load", () => {
        uploadedImage = reader.result;
        image.src = uploadedImage;
    })
    reader.readAsDataURL(this.files[0]);
    imageInput.style.zIndex = "-1";
})

const userProfileImgForm = document.querySelector(".user-profile__img-form");


// Отправляем форму после того как input изменился
let formAvatar = document?.querySelector(".user-profile__img-form");
let formAvatarInput = formAvatar?.querySelector(".user-profile__img-input");
let formAvatarBtn = formAvatar?.querySelector(".user-profile__img-submit");

formAvatarInput?.addEventListener("change", (env) => {
    formAvatarBtn.click();
})


// отправляем на сервер фото, которое загрузил пользователь без редактирования

userProfileImgForm?.addEventListener('submit', async (event) => {
    event.preventDefault();

    const fileInput = document.querySelector('.user-profile__img-input');

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    // const response = fetch('http://127.0.0.1:8000/api/v1/web/upload_avatar_as_file', {
    const response = fetch('https://energy.qidoctor.ru/api/v1/web/upload_avatar_as_file', {
        method: 'POST',
        body: formData,
    })

    const answer = await response.json;
    console.log(answer);
})




