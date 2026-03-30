// script.js
document.addEventListener("DOMContentLoaded", () => {
    const selects = document.querySelectorAll("select");
    selects.forEach(select => {
        select.addEventListener("change", () => {
            select.style.backgroundColor = select.value === "Yes" ? "#c8f7c5" : "#f7c5c5";
        });
    });
});