if (!document.getElementById("my-sidebar")) {

    const sidebar = document.createElement("div");
    sidebar.id = "my-sidebar";
    sidebar.innerHTML = `<div id="welcome-message"> Welcome to ClosetX </div>`;
    
    document.body.appendChild(sidebar);
  
    const style = document.createElement("style");
    style.textContent = `
      #my-sidebar {
        text-align: center;
        position: fixed;
        color: black;
        background; solid;
        background-color: white;
        top: 0;
        right: 0;
        width: 300px;
        height: 100%;
        z-index: 10000;
        box-shadow: -3px 0 8px rgba(128, 128, 128, 0.05);
        }
      #welcome-message {
        opacity: 0;
        animation: fadeIn 2s ease forwards;
        text-align: center;
        font-size: 1.5rem;
        font-family: 'IBM Plex Mono';
        padding-top: 1rem;
        }
      @keyframes fadeIn {
        to {
          opacity: 1;
        }
    `;
    document.head.appendChild(style);

    const prompt = document.createElement("p");
    prompt.innerHTML = `
              Enter your username
    `
    sidebar.appendChild(prompt);

    const inputField = document.createElement("input");
    sidebar.appendChild(inputField);

    const inputBr = document.createElement("br");
    sidebar.appendChild(inputBr);

    const submitButton = document.createElement("button");
    submitButton.setAttribute = ("id", "username-submit-button");
    submitButton.textContent = "Go";
    sidebar.appendChild(submitButton); 

    submitButton.addEventListener('click', async () => {
      const res = await fetch("http://127.0.0.1:5000/closet/closet", {
        method: "POST",
        body: new URLSearchParams({userid: inputField.value}),
      });
      const data = await res.json();
      if (data.apparels.length > 0) {
        const welcomeMessage = document.getElementById("welcome-message");
        welcomeMessage.textContent = "My closet";
        inputField.style.display = "none";
        submitButton.style.display = "none";
        prompt.style.display = "none";
        fetch("http://127.0.0.1:5000/closet/closet", {
                method: "POST",
                body: new URLSearchParams ({
                        userid: inputField.value
                })})
        .then(res => res.json()) 
        .then(data => {
          const stringList = data.apparels;
          stringList.forEach(uri => {
              fetch("http://127.0.0.1:5000/closet/get/apparel", {
                  method: 'POST',
                  body: new URLSearchParams({ uri: uri })
              })
              .then(res => res.blob())
              .then(blob => {
                  const img = document.createElement("img");
                  img.src = URL.createObjectURL(blob);
                  img.style.width = "100px";
                  img.style.margin = "10px";
                  document.getElementById("my-sidebar").appendChild(img);
                  const breakSize = document.createElement("br");
                  document.getElementById("my-sidebar").appendChild(breakSize);
                })
          });
      })
    }
  });
}  