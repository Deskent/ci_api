const imageInput = document.querySelector(".user-profile__img-input");
const image = document.querySelector(".user-profile__img");
const imageWrapper = document.querySelector(".user-profile__image-wrapper");

// загружаем фото user и тут же его просматриваем без отправки на сервер, это нужно для редактирования с помощью Croppie
var uploadedImage = "";

imageInput?.addEventListener("change", function(){
    console.log(imageInput.value);
    const reader = new FileReader();
    reader.addEventListener("load", () => {
        uploadedImage = reader.result;
        image.src = uploadedImage;
    })
    reader.readAsDataURL(this.files[0]);
    imageInput.style.zIndex = "-1";
})



image?.addEventListener("click", () => {

    // инициализируем редактор аватарок Croppie
    var vanilla = new Croppie(image, {
        viewport: { width: 100, height: 100, type: 'circle' },
        boundary: { width: 300, height: 300, type: 'circle' },
        showZoomer: false,
        enableOrientation: true,
    });
    vanilla.bind({
        url: uploadedImage,
        orientation: 4,
        zoom: 0

    });


    const uploadResultBtn = document.querySelector(".vanilla-result");
    const rotateBtn = document.querySelector(".vanilla-rotate");

    uploadResultBtn.style.display = "block";
    rotateBtn.style.display = "block";

    uploadResultBtn?.addEventListener("click", async function() {
        let res = await vanilla.result({type: 'base64'});
        image.src = res;
        const Base64Avatar = image.src;
        vanilla.destroy();
        uploadResultBtn.style.display = "none";
        rotateBtn.style.display = "none";
        imageInput.style.zIndex = "2";
    // console.log(Base64Avatar);

    // Отправляем на сервер обрезанное фото в формате base64

    // const response = await fetch('http://127.0.0.1:8000/api/v1/web/...........', {
    //     //    const response = await fetch('http://energy.qidoctor.ru/aapi/v1/web/.........', {
    //           method: 'POST',
    //           Base64Avatar: Base64Avatar,
    //           headers: {
    //           'Content-Type': 'application/json;charset=utf-8',
    //           },
    //        });
        
    // let answer = await response.json();
    // console.log(answer);
   
    })


    // не получилось переписать эти строки на vanilla-js
    $('.vanilla-rotate').on('click', function(ev) {
        vanilla.rotate(parseInt($(this).data('deg')));
    });



})