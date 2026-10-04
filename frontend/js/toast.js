/**
 * Jino Café — Toast Notification Utility
 */

const Toast = {
  container: null,

  init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },

  show(message, type = 'info', duration = 3500) {
    this.init();

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const iconMap = {
      success: '☕',
      error: '⚠️',
      info: 'ℹ️'
    };

    toast.innerHTML = `
      <span style="font-size: 18px;">${iconMap[type] || '✨'}</span>
      <span>${message}</span>
    `;

    this.container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },

  success(msg, dur) { this.show(msg, 'success', dur); },
  error(msg, dur) { this.show(msg, 'error', dur); },
  info(msg, dur) { this.show(msg, 'info', dur); }
};

window.Toast = Toast;
