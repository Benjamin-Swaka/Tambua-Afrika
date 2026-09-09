(function () {
    "use strict";

    function getCookie(name) {
        const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
        return match ? decodeURIComponent(match[2]) : null;
    }

    document.addEventListener("DOMContentLoaded", function () {
        const toggleBtn = document.getElementById("chatbotToggle");
        const toggleIcon = document.getElementById("chatbotToggleIcon");
        const panel = document.getElementById("chatbotPanel");
        const closeBtn = document.getElementById("chatbotClose");
        const messagesEl = document.getElementById("chatbotMessages");
        const typingEl = document.getElementById("chatbotTyping");
        const form = document.getElementById("chatbotForm");
        const input = document.getElementById("chatbotInput");

        if (!toggleBtn || !panel || !form) return;

        const endpoint = toggleBtn.dataset.endpoint;
        let isOpen = false;
        let isSending = false;

        function openPanel() {
            panel.hidden = false;
            // next frame so the transition actually runs
            requestAnimationFrame(function () {
                panel.classList.add("chatbot-panel--open");
            });
            toggleBtn.classList.add("is-active");
            toggleBtn.setAttribute("aria-expanded", "true");
            toggleIcon.classList.remove("fa-comment-dots");
            toggleIcon.classList.add("fa-times");
            isOpen = true;
            setTimeout(function () { input.focus(); }, 200);
        }

        function closePanel() {
            panel.classList.remove("chatbot-panel--open");
            toggleBtn.classList.remove("is-active");
            toggleBtn.setAttribute("aria-expanded", "false");
            toggleIcon.classList.remove("fa-times");
            toggleIcon.classList.add("fa-comment-dots");
            isOpen = false;
            setTimeout(function () {
                if (!isOpen) panel.hidden = true;
            }, 220);
        }

        toggleBtn.addEventListener("click", function () {
            isOpen ? closePanel() : openPanel();
        });
        closeBtn.addEventListener("click", closePanel);

        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && isOpen) closePanel();
        });

        function addMessage(text, kind) {
            const bubble = document.createElement("div");
            bubble.className = "chatbot-message chatbot-message--" + kind;
            const p = document.createElement("p");
            p.textContent = text;
            bubble.appendChild(p);
            messagesEl.appendChild(bubble);
            messagesEl.scrollTop = messagesEl.scrollHeight;
        }

        function setSending(state) {
            isSending = state;
            input.disabled = state;
            form.querySelector(".chatbot-send-btn").disabled = state;
            typingEl.hidden = !state;
            if (state) {
                messagesEl.scrollTop = messagesEl.scrollHeight;
            }
        }

        form.addEventListener("submit", function (e) {
            e.preventDefault();
            const message = input.value.trim();
            if (!message || isSending || !endpoint) return;

            addMessage(message, "user");
            input.value = "";
            setSending(true);

            fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken") || "",
                },
                credentials: "same-origin",
                body: JSON.stringify({ message: message }),
            })
                .then(function (response) {
                    if (!response.ok) throw new Error("bad-response");
                    return response.json();
                })
                .then(function (data) {
                    setSending(false);
                    addMessage(data.reply, "bot");
                })
                .catch(function () {
                    setSending(false);
                    addMessage(
                        "Sorry, I couldn't send that just now. Please try again, or reach us on WhatsApp.",
                        "error"
                    );
                });
        });
    });
})();
