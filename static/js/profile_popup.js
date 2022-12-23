const helloVideo = document?.querySelector('.hello-video');
const helloVideoWrapper = document?.querySelector('.slide__wrapper');
const helloVideoPlay = helloVideoWrapper?.querySelector('.slide__play');
const helloVideoPause = helloVideoWrapper?.querySelector('.slide__pause');
const newLevelDescription = modal?.querySelector('.new-level_description');
const formEmojiBox = document?.querySelector('.form_emoji-box');

const formEmoji = modal?.querySelector('.form_emoji');

const newLevelHeader = document.querySelector('.new-level_header');
const modalSubscriptionLink = document.querySelector('.modal__subscription-link');




if (urlPath.includes("profile")) {
    document.addEventListener("DOMContentLoaded", async (evt) => {
        const response = await fetch(serverUrl + '/web/check_first_entry', {
            method: 'GET',
            headers: {
                'Content-Type': 'text/html;charset=utf-8',
            },
        });

        let result = await response.json();
        console.log(result);

        const newUser = result.new_user;
        const todayFirstEntry = result.today_first_entry;
        const isExpired = result.is_expired;
        const emojies = result.emojies;
        let emojiesLength = result.emojies.length;




        if (newUser === true) {
            formEmojiBox.remove();
            modalSubscriptionLink.remove();
            openModalNewLevelHandler();
            helloVideoPlay?.addEventListener("click", (evt) => {
                helloVideoPlay?.classList.add("hidden");
                helloVideoPause?.classList.remove("hidden");
                helloVideo.play();
            })

            helloVideoPause?.addEventListener("click", (evt) => {
                helloVideoPlay?.classList.remove("hidden");
                helloVideoPause?.classList.add("hidden");
                helloVideo.pause();
            })
            helloVideo.addEventListener('ended', (env) => {
              helloVideoPlay?.classList.remove("hidden");
              helloVideoPause?.classList.add("hidden");
            })
        }

        if (todayFirstEntry === true) {
            openModalNewLevelHandler();

            console.log(emojies);

            helloVideoWrapper.remove();
            newLevelDescription.remove();
            modalSubscriptionLink.remove();



            newLevelHeader.textContent = "Какое у Вас сегодня настроение?"

            const formEmojiBoxInput = modal?.querySelector('.form_emoji-box-input');
            var fragment = document.createDocumentFragment();

            for (let i = 0; i < 5; i++) {

              let emojiCode = emojies[i].code;
              let emojiCodeReplase = emojiCode.replace("U+", '0x');

              //помогает отобразить emodji
              let emoji = String.fromCodePoint(emojiCodeReplase);

              if (i === 0 ) {
                let formEmojiLabel = modal?.querySelector('.form_emoji-label');
                let formEmojiImg = modal?.querySelector('.form_emoji__img');
                let formEmojiInput = modal?.querySelector('.form_emoji-input');

                formEmojiImg.textContent =  emoji;
                formEmojiLabel.textContent = emojies[i].name;
                formEmojiInput.setAttribute('id', emojies[i].id);
                formEmojiInput.setAttribute('value', emojies[i].name);
                formEmojiLabel.setAttribute('for', emojies[i].id);
              } else {
                let formEmojiBoxInputClone = formEmojiBoxInput.cloneNode(true);
                let formEmojiLabelClone = formEmojiBoxInputClone?.querySelector('.form_emoji-label');
                let formEmojiImgClone = formEmojiBoxInputClone?.querySelector('.form_emoji__img');
                let formEmojiInputClone = formEmojiBoxInputClone?.querySelector('.form_emoji-input');
                
                  formEmojiImgClone.textContent =  emoji;
                  formEmojiLabelClone.textContent = emojies[i].name;
                  formEmojiInputClone.setAttribute('id', emojies[i].id);
                  formEmojiInputClone.setAttribute('value', emojies[i].name);
                  formEmojiLabelClone.setAttribute('for', emojies[i].id);
                  fragment.prepend(formEmojiBoxInputClone);
              }
            }

            formEmoji.prepend(fragment);

            let formEmojiInputs = modal?.querySelectorAll('.form_emoji-input');


            formEmoji.addEventListener('submit', async (evt) => {
                evt.preventDefault();
                let inputId;
                for (let input of formEmojiInputs) {
                    if (input.checked) {
                        inputId = Number(input.id);
                    }
                }

                const request = fetch(serverUrl + '/web/set_user_mood', {
                    method: 'POST',
                    body: JSON.stringify({
                        'mood_id': inputId,
                    }),
                    headers: {
                        'Content-Type': 'application/json;charset=utf-8',
                    }
                });

                let answer = await request.json;

                // console.log(answer);
                modal.remove();
            })

        }

        if (isExpired === true) {
            openModalNewLevelHandler();
            newLevelDescription.remove();
            helloVideoWrapper.remove();
            formEmojiBox.remove();
            newLevelHeader.textContent = "Продлите Вашу подписку";
        }

        close?.addEventListener("click", closeModalNewLevelHandler);

    })
}
