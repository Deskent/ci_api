const helloVideo = document?.querySelector('.hello-video');
const helloVideoWrapper = document?.querySelector('.slide__wrapper');


const helloVideoPlay = helloVideoWrapper?.querySelector('.slide__play');
const helloVideoPause = helloVideoWrapper?.querySelector('.slide__pause');

if (urlPath.includes("profile")) {
  document.addEventListener("DOMContentLoaded", async (evt) => {
      const response = await fetch(serverUrl + '/web/check_first_entry', {
          method: 'GET',
          headers: {
              'Content-Type': 'application/json;charset=utf-8',
          },
      });

      let result = await response.json();
      console.log(result);

      const newUser = result.new_user;

      if(newUser === true) {
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

      close?.addEventListener("click", closeModalNewLevelHandler);

  })
}