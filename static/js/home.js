

document.addEventListener("DOMContentLoaded", function () {

    const themeToggle = document.getElementById("themeToggle");

    if (!themeToggle) return;

    const themeIcon = themeToggle.querySelector("i");

    function applyTheme(theme) {

        const isDark = theme === "dark";

        document.body.classList.toggle("dark-mode", isDark);

        // Set the correct icon
        themeIcon.className = isDark
            ? "fa-solid fa-sun"
            : "fa-regular fa-moon";

        // Update tooltip
        themeToggle.title = isDark
            ? "Switch to light mode"
            : "Switch to dark mode";
    }

    // Load saved theme
    const savedTheme = localStorage.getItem("electromart-theme") || "light";

    applyTheme(savedTheme);

    // Toggle theme on click
    themeToggle.addEventListener("click", function () {

        const isCurrentlyDark =
            document.body.classList.contains("dark-mode");

        const newTheme = isCurrentlyDark ? "light" : "dark";

        localStorage.setItem("electromart-theme", newTheme);

        applyTheme(newTheme);

    });

});
