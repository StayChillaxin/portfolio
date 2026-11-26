// Assignment 6: add a class after the page finishes loading.
window.addEventListener("load", function () {
  document.body.classList.add("page-loaded");
});

// Assignment 6 / 7: skills are stored in an array and generated on the About Me page.
const skills = [
  "IT Support and Troubleshooting",
  "Microsoft Active Directory",
  "Networking and Systems Administration",
  "Python Programming",
  "SQL and Database Management",
  "HTML and CSS",
  "Cybersecurity Fundamentals"
];

const list = document.querySelector("#list");
if (list) {
  skills.forEach(function (skill) {
    const li = document.createElement("li");
    li.textContent = skill;
    list.appendChild(li);
  });

  const count = document.getElementById("count");
  if (count) {
    count.textContent = "I have " + skills.length + " skills and areas of experience listed.";
  }
}

// Assignment 7: dark-mode button uses addEventListener and classList.toggle.
const themeToggle = document.querySelector("#theme-toggle");
if (themeToggle) {
  themeToggle.addEventListener("click", function () {
    const darkModeEnabled = document.body.classList.toggle("dark-mode");
    themeToggle.setAttribute("aria-pressed", String(darkModeEnabled));
    themeToggle.textContent = darkModeEnabled ? "Turn off dark mode" : "Toggle dark mode";
  });
}

// Assignment 7: client-side contact form validation.
const contactForm = document.querySelector("#contact-form");
if (contactForm) {
  contactForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const nameField = document.querySelector("#contact-name");
    const emailField = document.querySelector("#contact-email");
    const messageField = document.querySelector("#contact-message");
    const nameMessage = document.querySelector("#name-message");
    const emailMessage = document.querySelector("#email-message");
    const messageFeedback = document.querySelector("#message-feedback");
    const formResult = document.querySelector("#form-result");

    nameMessage.textContent = "";
    emailMessage.textContent = "";
    messageFeedback.textContent = "";
    formResult.textContent = "";

    let valid = true;

    if (!nameField.value.trim()) {
      nameMessage.textContent = "Please enter your name.";
      valid = false;
    }

    if (!emailField.value.trim()) {
      emailMessage.textContent = "Please enter your email address.";
      valid = false;
    } else if (!emailField.validity.valid) {
      emailMessage.textContent = "Please enter a valid email address.";
      valid = false;
    }

    // Custom rule: the message must contain at least 20 characters.
    if (messageField.value.trim().length < 20) {
      messageFeedback.textContent = "Your message must be at least 20 characters long.";
      valid = false;
    }

    if (valid) {
      formResult.textContent = "Thank you! Your form passed validation. This demo does not send the message.";
      contactForm.reset();
    }
  });
}
