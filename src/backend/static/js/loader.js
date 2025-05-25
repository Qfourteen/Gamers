const loadingScreen = document.getElementById("loading-screen");
const mainContent = document.getElementById("main-content");
const LOADING_DURATION = 2500;

window.addEventListener("load", () => {
    setTimeout(() => {
        loadingScreen.style.opacity = 0;
        setTimeout(() => {
            loadingScreen.style.display = "none";
            mainContent.style.display = "block";
        }, 500); // opacity transition 시간과 맞춤
    }, LOADING_DURATION);
});