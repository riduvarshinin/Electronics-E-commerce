(function () {
    "use strict";

    // Show / hide password
    document.querySelectorAll("[data-toggle]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            var input = document.getElementById(btn.dataset.toggle);
            if (!input) return;
            var show = input.type === "password";
            input.type = show ? "text" : "password";
            btn.textContent = show ? "Hide" : "Show";
            btn.setAttribute("aria-label", show ? "Hide password" : "Show password");
        });
    });

    // Password strength meter (register page)
    var pw = document.getElementById("password");
    var meter = document.getElementById("strength");
    if (pw && meter) {
        var bar = meter.querySelector(".strength-bar span");
        var label = meter.querySelector(".strength-label");
        var levels = [
            { text: "Too short", cls: "s0" },
            { text: "Weak", cls: "s1" },
            { text: "Fair", cls: "s2" },
            { text: "Good", cls: "s3" },
            { text: "Strong", cls: "s4" }
        ];
        pw.addEventListener("input", function () {
            var v = pw.value, score = 0;
            if (v.length >= 8) score++;
            if (/[a-z]/.test(v) && /[A-Z]/.test(v)) score++;
            if (/\d/.test(v)) score++;
            if (/[^A-Za-z0-9]/.test(v) || v.length >= 14) score++;
            if (v.length === 0) {
                meter.hidden = true;
                return;
            }
            if (v.length < 8) score = 0;
            meter.hidden = false;
            meter.className = "strength " + levels[score].cls;
            bar.style.width = (score === 0 ? 12 : score * 25) + "%";
            label.textContent = levels[score].text;
        });
    }

    // Confirm password must match
    var confirm = document.getElementById("confirm_password");
    var hint = document.getElementById("confirm-hint");
    if (pw && confirm) {
        var check = function () {
            if (!confirm.value) {
                confirm.setCustomValidity("");
                if (hint) hint.textContent = "";
                return;
            }
            if (confirm.value !== pw.value) {
                confirm.setCustomValidity("Passwords do not match.");
                if (hint) { hint.textContent = "Passwords do not match."; hint.className = "hint hint-error"; }
            } else {
                confirm.setCustomValidity("");
                if (hint) { hint.textContent = "Passwords match."; hint.className = "hint hint-ok"; }
            }
        };
        pw.addEventListener("input", check);
        confirm.addEventListener("input", check);
    }

    // Prevent double submit
    document.querySelectorAll("form[data-once]").forEach(function (form) {
        form.addEventListener("submit", function () {
            var b = form.querySelector("button[type=submit]");
            if (b && form.checkValidity()) {
                setTimeout(function () { b.disabled = true; b.classList.add("is-loading"); }, 0);
            }
        });
    });

    // Toasts: dismiss on click, auto-hide
    document.querySelectorAll(".toast").forEach(function (t) {
        var remove = function () {
            t.classList.add("is-leaving");
            setTimeout(function () { t.remove(); }, 250);
        };
        var close = t.querySelector(".toast-close");
        if (close) close.addEventListener("click", remove);
        setTimeout(remove, 6000);
    });
})();
