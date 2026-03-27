(function () {
  const API_URL = "http://127.0.0.1:8000";

  // Create chatbot icon
  const button = document.createElement("div");
  button.innerHTML = "💬";
  button.style.position = "fixed";
  button.style.bottom = "20px";
  button.style.left = "20px";
  button.style.background = "#007bff";
  button.style.color = "#fff";
  button.style.padding = "15px";
  button.style.borderRadius = "50%";
  button.style.cursor = "pointer";
  button.style.zIndex = "9999";

  document.body.appendChild(button);

  // Create chat box
  const chatBox = document.createElement("div");
  chatBox.style.position = "fixed";
  chatBox.style.bottom = "80px";
  chatBox.style.left = "20px";
  chatBox.style.width = "300px";
  chatBox.style.height = "400px";
  chatBox.style.background = "#fff";
  chatBox.style.border = "1px solid #ccc";
  chatBox.style.display = "none";
  chatBox.style.flexDirection = "column";
  chatBox.style.zIndex = "9999";

  chatBox.innerHTML = `
    <div style="padding:10px;background:#007bff;color:#fff">Pragnaware Chat</div>
    <div id="messages" style="flex:1;padding:10px;overflow:auto"></div>
    <div id="leadForm" style="padding:10px">
      <input id="name" placeholder="Your Name" style="width:100%;margin-bottom:5px"/>
      <input id="email" placeholder="Your Email" style="width:100%;margin-bottom:5px"/>
      <button onclick="saveLead()">Start Chat</button>
    </div>
    <div id="chatInput" style="display:none;padding:10px">
      <input id="msg" placeholder="Type message..." style="width:70%"/>
      <button onclick="sendMessage()">Send</button>
    </div>
  `;

  document.body.appendChild(chatBox);

  // Toggle chat
  button.onclick = () => {
    chatBox.style.display = chatBox.style.display === "none" ? "flex" : "none";
  };

  // Save lead
  window.saveLead = async function () {
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;

    await fetch(API_URL + "/save-lead", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email })
    });

    document.getElementById("leadForm").style.display = "none";
    document.getElementById("chatInput").style.display = "block";
  };

  // Send message
  window.sendMessage = async function () {
    const msg = document.getElementById("msg").value;
    const messages = document.getElementById("messages");

    messages.innerHTML += `<div><b>You:</b> ${msg}</div>`;

    const res = await fetch(API_URL + "/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: msg })
    });

    const data = await res.json();

    messages.innerHTML += `<div><b>Bot:</b> ${data.reply}</div>`;
  };
})();