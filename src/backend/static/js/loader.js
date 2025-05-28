const loadingScreen = document.getElementById("loading-screen");
const mainContent = document.getElementById("main-content");

// 첫 방문인지 확인 (localStorage 사용)
const isFirstVisit = !window.localStorage.getItem(VISIT_KEY);

// 첫 방문이면 2500ms, 재방문이면 500ms
const LOADING_DURATION = isFirstVisit ? 2500 : 500;

// 첫 방문 기록을 남기기
if (isFirstVisit) {
    localStorage.setItem(VISIT_KEY, "true");
}

window.addEventListener("load", () => {
    setTimeout(() => {
        // 페이드 아웃
        loadingScreen.style.opacity = 0;
        setTimeout(() => {
            // 화면 전환
            loadingScreen.style.display = "none";
            loadingScreen.style.zIndex = "0";
            mainContent.style.display = "block";
        }, 500); // opacity transition 시간 (CSS와 동일하게 0.5s)
    }, LOADING_DURATION);
});
