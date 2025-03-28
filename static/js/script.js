let userInfo = {};

function startChat() {
    let name = document.getElementById("name").value.trim();
    let email = document.getElementById("email").value.trim();
    let phone = document.getElementById("phone").value.trim();

    if (!name || !email || !phone) {
        alert("Please fill in all fields to start the chat.");
        return;
    }

    userInfo = { name, email, phone };

    document.getElementById("user-form").style.display = "none";
    document.getElementById("chat-container").style.display = "block";

    fetch("/store_user", {
        method: "POST",
        body: JSON.stringify(userInfo),
        headers: { "Content-Type": "application/json" }
    });

    // Ensure chat starts at the bottom
    scrollToBottom();
}

function sendMessage() {
    let userInput = document.getElementById("user-input").value.trim();
    if (!userInput) return;

    let chatOutput = document.getElementById("chat-output");

    // Create user message div
    let userMessageDiv = document.createElement("div");
    userMessageDiv.className = "message user-message";

    let userAvatar = document.createElement("img");
    userAvatar.src = "https://cdn-icons-png.flaticon.com/512/847/847969.png";
    userAvatar.className = "avatar user-avatar";

    let userText = document.createElement("span");
    userText.textContent = userInput;

    userMessageDiv.appendChild(userText);
    userMessageDiv.appendChild(userAvatar);

    // Insert new messages at the beginning instead of the end
    chatOutput.prepend(userMessageDiv);

    fetch("/chat", {
        method: "POST",
        body: JSON.stringify({ message: userInput, user: userInfo }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        let botMessageDiv = document.createElement("div");
        botMessageDiv.className = "message bot-message";

        let botAvatar = document.createElement("img");
        botAvatar.src = "https://cdn-icons-png.flaticon.com/512/4712/4712036.png";
        botAvatar.className = "avatar";

        let botText = document.createElement("span");
        botText.textContent = data.response;

        botMessageDiv.appendChild(botAvatar);
        botMessageDiv.appendChild(botText);

        // Insert bot messages at the beginning
        chatOutput.prepend(botMessageDiv);
    });

    // Clear input field
    document.getElementById("user-input").value = "";
}

// Function to scroll to the bottom
function scrollToBottom() {
    let chatOutput = document.getElementById("chat-output");
    setTimeout(() => {
        chatOutput.scrollTop = 0;  // Since column-reverse is used, 0 scrolls to the bottom
    }, 100);
}
