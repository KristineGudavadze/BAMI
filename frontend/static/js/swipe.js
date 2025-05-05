document.addEventListener("DOMContentLoaded", function () {
    const connectButtons = document.querySelectorAll(".connect-btn");
    const skipButtons = document.querySelectorAll(".skip-btn");

    connectButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            alert("You connected with this user!");
        });
    });

    skipButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            alert("Skipped user.");
        });
    });
});
