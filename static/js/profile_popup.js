const helloVideo = document?.querySelector('.hello-video');
const helloVideoWrapper = document?.querySelector('.slide__wrapper');
const helloVideoPlay = helloVideoWrapper?.querySelector('.slide__play');
const helloVideoPause = helloVideoWrapper?.querySelector('.slide__pause');
const newLevelDescription = modal?.querySelector('.new-level_description');
const formEmojiBox = document?.querySelector('.form_emoji-box');

const formEmoji = modal?.querySelector('.form_emoji');


const formEmojiBoxInput = modal?.querySelectorAll('.form_emoji-box-input');

const formEmojiLabel = modal?.querySelectorAll('.form_emoji-label');

const formEmojiImg = modal?.querySelectorAll('.form_emoji__img');

const formEmojiInput = modal?.querySelectorAll('.form_emoji-input');





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


      if(newUser === true) {
        formEmojiBox.remove();
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
      }

      if(todayFirstEntry === true) {
        openModalNewLevelHandler();

        console.log(emojies);

        helloVideoWrapper.remove();
        newLevelDescription.remove();
        const newLevelHeader = document.querySelector('.new-level_header');

        newLevelHeader.textContent = "Какое у Вас сегодня настроение?"
        
        for (let i = 0; i < formEmojiBoxInput.length; i++) {
          // const formEmojiBoxInput = formEmojiBoxInputArr[i];
          const formEmojiLabelItem = formEmojiLabel[i];
          const formEmojiInputItem = formEmojiInput[i]

          formEmojiLabelItem.textContent = emojies[i].name;
          formEmojiInputItem.setAttribute('id', emojies[i].id);
          formEmojiInputItem.setAttribute('value', emojies[i].name);
          formEmojiLabelItem.setAttribute('for', emojies[i].id);
        }

        formEmoji.addEventListener('submit', async(evt) => {
          evt.preventDefault();

          let inputId;
          for (let input of formEmojiInput) {
            if(input.checked) {
              inputId = Number(input.id);
            }
          };
          console.log(inputId);

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

        console.log(answer);
        })
        
      }

      if(isExpired === true) {
        helloVideoWrapper.remove();
        formEmojiBox.remove();
        newLevelHeader.textContent = "Подписка закончилась"
      }

      close?.addEventListener("click", closeModalNewLevelHandler);

  })
}