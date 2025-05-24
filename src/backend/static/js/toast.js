const toastTrigger = document.getElementById('liveToastBtn')
const toastLiveExample = document.getElementById('liveToast')
const toastMessage = document.getElementById("toast-message")
const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toastLiveExample)
console.log(`Toast status: ${toastBootstrap}`)
function showToast() {
    toastBootstrap.show();
}