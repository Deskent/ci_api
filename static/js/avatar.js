const imageInput = document.querySelector(".user-profile__img-input");
const image1 = document.querySelector(".user-profile__img");
const image2 = document.querySelector(".header-user__icon-img");
const image3 = document.querySelector(".header-menu__img");

const imageWrapper = document.querySelector(".user-profile__image-wrapper");

// загружаем фото user и тут же его просматриваем без отправки на сервер, это нужно для редактирования с помощью Croppie
var uploadedImage = "";

imageInput?.addEventListener("change", function () {
    console.log(imageInput.value);
    const reader = new FileReader();
    reader.addEventListener("load", () => {
        uploadedImage = reader.result;
        image1.src = uploadedImage;
        image2.src = uploadedImage;
        image3.src = uploadedImage;

    })
    reader.readAsDataURL(this.files[0]);
    imageInput.style.zIndex = "-1";
})



// Отправляем форму после того как input изменился
let formAvatar = document?.querySelector(".user-profile__img-form");
let formAvatarInput = formAvatar?.querySelector(".user-profile__img-input");


// отправляем на сервер фото, которое загрузил пользователь без редактирования

formAvatarInput?.addEventListener('change', async (event) => {
    event.preventDefault();

    const fileInput = document.querySelector('.user-profile__img-input');

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const response = fetch(serverUrl + '/web/upload_avatar_as_file', {
        method: 'POST',
        body: formData,
    })

    const answer = await response.json;
    // console.log(answer);
})




