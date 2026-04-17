async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData
    });

    alert("Uploaded!");
}

let messages = [];

async function sendQuestion() {
    const q = document.getElementById("question").value;

    const res = await fetch(`http://localhost:8000/chat?q=${q}`);
    const data = await res.json();

    messages.push({ role: "user", content: q });
    messages.push({ role: "bot", content: data.answer });

    const chatBox = document.getElementById("chatBox");

    chatBox.innerHTML = "";

    messages.forEach(m => {
        if (m.role === "user") {
            chatBox.innerHTML += `<p><b>You:</b> ${m.content}</p>`;
        } else {
            chatBox.innerHTML += `<p><b>Bot:</b> ${m.content}</p>`;
        }
    });
}