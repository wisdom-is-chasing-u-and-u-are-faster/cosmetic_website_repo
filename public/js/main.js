// public/js/main.js - Global App Helpers & Dynamic Event Wire-up

function showNotification(message, type = "success") {
  const container = document.getElementById("notification-container") || createNotificationContainer();
  const alert = document.createElement("div");
  alert.className = `alert alert-${type}`;
  alert.textContent = message;
  container.appendChild(alert);
  setTimeout(() => alert.remove(), 4000);
}

function createNotificationContainer() {
  const el = document.createElement("div");
  el.id = "notification-container";
  el.style.position = "fixed";
  el.style.bottom = "20px";
  el.style.right = "20px";
  el.style.zIndex = "9999";
  document.body.appendChild(el);
  return el;
}

window.showNotification = showNotification;
