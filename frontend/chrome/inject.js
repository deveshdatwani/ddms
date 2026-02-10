// Persistent content script - runs on every page
if (!window.closetxLoaded) {
  window.closetxLoaded = true;

  function createSidebar() {
    // Create Shadow DOM for true isolation
    if (!document.getElementById("closetx-shadow-host")) {
      const host = document.createElement("div");
      host.id = "closetx-shadow-host";
      host.style.cssText = `
        all: initial;
        position: fixed !important;
        top: 0 !important;
        right: 0 !important;
        width: 300px !important;
        height: 100vh !important;
        z-index: 2147483647 !important;
      `;
      document.documentElement.appendChild(host);

      // Create shadow root
      const shadowRoot = host.attachShadow({ mode: "open" });

      // Create styles
      const style = document.createElement("style");
      style.textContent = `
        :host {
          all: initial;
          display: block;
          position: fixed;
          top: 0;
          right: 0;
          width: 300px;
          height: 100vh;
          z-index: 2147483647;
        }

        .sidebar {
          position: fixed;
          top: 0;
          right: 0;
          width: 300px;
          height: 100vh;
          background-color: white;
          color: black;
          text-align: center;
          z-index: 2147483647;
          box-shadow: -3px 0 8px rgba(128, 128, 128, 0.05);
          font-family: 'IBM Plex Mono', monospace;
          overflow-y: auto;
          box-sizing: border-box;
          margin: 0;
          padding: 0;
        }

        #welcome-message {
          opacity: 0;
          animation: fadeIn 2s ease forwards;
          text-align: center;
          font-size: 1.5rem;
          padding-top: 1rem;
          margin: 0;
        }

        @keyframes fadeIn {
          to {
            opacity: 1;
          }
        }

        p {
          text-align: center;
          margin: 1rem 0;
          font-size: 1rem;
        }

        input {
          display: block;
          margin: 0.5rem auto;
          padding: 0.5rem;
          width: 80%;
          box-sizing: border-box;
        }

        button {
          display: block;
          margin: 0.5rem auto;
          padding: 0.5rem 1rem;
          cursor: pointer;
          background-color: #f0f0f0;
          border: 1px solid #ccc;
          border-radius: 4px;
        }

        button:hover {
          background-color: #e0e0e0;
        }

        img {
          width: 100px;
          margin: 10px auto;
          display: block;
        }
      `;
      shadowRoot.appendChild(style);

      // Create sidebar container
      const sidebar = document.createElement("div");
      sidebar.className = "sidebar";
      
      sidebar.innerHTML = `
        <div id="welcome-message">Welcome to ClosetX</div>
        <p id="prompt">Enter your username</p>
        <input type="text" id="username-input" placeholder="username">
        <button id="submit-btn">Go</button>
        <div id="content"></div>
      `;

      shadowRoot.appendChild(sidebar);

      // Get references to elements in shadow DOM
      const inputField = shadowRoot.getElementById("username-input");
      const submitBtn = shadowRoot.getElementById("submit-btn");
      const prompt = shadowRoot.getElementById("prompt");
      const welcomeMessage = shadowRoot.getElementById("welcome-message");
      const content = shadowRoot.getElementById("content");

      submitBtn.addEventListener("click", async () => {
        const userIdValue = inputField.value;
        if (!userIdValue) return;

        try {
          const res = await fetch("http://127.0.0.1:5000/closet/closet", {
            method: "POST",
            body: new URLSearchParams({ userid: userIdValue }),
          });
          const data = await res.json();

          if (data.apparels && data.apparels.length > 0) {
            welcomeMessage.textContent = "My closet";
            inputField.style.display = "none";
            submitBtn.style.display = "none";
            prompt.style.display = "none";

            fetch("http://127.0.0.1:5000/closet/closet", {
              method: "POST",
              body: new URLSearchParams({ userid: userIdValue }),
            })
              .then((res) => res.json())
              .then((data) => {
                const stringList = data.apparels;
                stringList.forEach((uri) => {
                  fetch("http://127.0.0.1:5000/closet/get/apparel", {
                    method: "POST",
                    body: new URLSearchParams({ uri: uri }),
                  })
                    .then((res) => res.blob())
                    .then((blob) => {
                      const img = document.createElement("img");
                      img.src = URL.createObjectURL(blob);
                      content.appendChild(img);
                    });
                });
              });
          }
        } catch (error) {
          console.error("Error:", error);
        }
      });
    }
  }

  // Create sidebar on page load
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", createSidebar);
  } else {
    createSidebar();
  }
  
  // Listen for toggle messages from the background script
  if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.onMessage) {
    chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
      if (msg && msg.type === 'toggle-closetx') {
        const host = document.getElementById('closetx-shadow-host');
        if (host) {
          // toggle visibility
          host.style.display = (host.style.display === 'none') ? '' : 'none';
        } else {
          createSidebar();
        }
      }
    });
  }
}  

// Ensure sidebar persists: recreate if removed by page scripts
function ensureSidebarPresence() {
  try {
    if (!document.getElementById('closetx-shadow-host')) {
      createSidebar();
      console.debug('closetx: recreated sidebar');
    }
  } catch (e) {
    console.warn('closetx: ensureSidebarPresence failed', e);
  }
}

// Observe DOM mutations at the root and recreate host if necessary
const _closetxObserver = new MutationObserver(() => {
  ensureSidebarPresence();
});
_closetxObserver.observe(document.documentElement || document.body, { childList: true, subtree: true });

// Also check after any click (some sites synchronously remove injected nodes on click)
document.addEventListener('click', () => { setTimeout(ensureSidebarPresence, 0); }, true);