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


      openModalNewLevelHandler()



      close?.addEventListener("click", closeModalNewLevelHandler);


  })
}