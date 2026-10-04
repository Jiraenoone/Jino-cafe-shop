/**
 * Jino Café — Cart State & Drawer Controller
 * Handles local storage persistence, drawer UI, quantities, totals
 */

const CART_STORAGE_KEY = 'jinocafe_cart';

const Cart = {
  items: [],

  init() {
    this.load();
    this.render();
    this.updateBadge();
    this.attachEvents();
  },

  load() {
    try {
      const data = localStorage.getItem(CART_STORAGE_KEY);
      this.items = data ? JSON.parse(data) : [];
    } catch (_) {
      this.items = [];
    }
  },

  save() {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(this.items));
    this.updateBadge();
    this.render();
  },

  addItem(product, quantity = 1, options = {}, notes = '') {
    // Unique key considering selected options
    const optKey = JSON.stringify(options);
    const existingIndex = this.items.findIndex(
      item => item.product_id === product.id && JSON.stringify(item.selected_options) === optKey
    );

    if (existingIndex > -1) {
      this.items[existingIndex].quantity += quantity;
    } else {
      this.items.push({
        product_id: product.id,
        name: product.name,
        unit_price: Number(product.price),
        image_url: product.image_url,
        quantity: quantity,
        selected_options: options,
        notes: notes
      });
    }

    this.save();
    if (window.Toast) {
      Toast.success(`Added ${product.name} to cart!`);
    }
    this.openDrawer();
  },

  updateQuantity(index, delta) {
    if (!this.items[index]) return;
    this.items[index].quantity += delta;

    if (this.items[index].quantity <= 0) {
      this.items.splice(index, 1);
    }
    this.save();
  },

  removeItem(index) {
    if (!this.items[index]) return;
    this.items.splice(index, 1);
    this.save();
  },

  clear() {
    this.items = [];
    this.save();
  },

  getTotal() {
    return this.items.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0);
  },

  getCount() {
    return this.items.reduce((sum, item) => sum + item.quantity, 0);
  },

  updateBadge() {
    const badges = document.querySelectorAll('.cart-count');
    const count = this.getCount();
    badges.forEach(b => {
      b.textContent = count;
      b.style.display = count > 0 ? 'inline-flex' : 'none';
    });
  },

  openDrawer() {
    const overlay = document.getElementById('cartDrawerOverlay');
    const drawer = document.getElementById('cartDrawer');
    if (overlay && drawer) {
      overlay.classList.add('active');
      drawer.classList.add('active');
    }
  },

  closeDrawer() {
    const overlay = document.getElementById('cartDrawerOverlay');
    const drawer = document.getElementById('cartDrawer');
    if (overlay && drawer) {
      overlay.classList.remove('active');
      drawer.classList.remove('active');
    }
  },

  attachEvents() {
    const closeBtn = document.getElementById('closeCartBtn');
    const overlay = document.getElementById('cartDrawerOverlay');
    const cartTriggers = document.querySelectorAll('.btn-cart');

    if (closeBtn) closeBtn.addEventListener('click', () => this.closeDrawer());
    if (overlay) overlay.addEventListener('click', () => this.closeDrawer());
    cartTriggers.forEach(btn => btn.addEventListener('click', () => this.openDrawer()));
  },

  render() {
    const body = document.getElementById('cartDrawerBody');
    const totalEl = document.getElementById('cartTotalAmount');
    const checkoutBtn = document.getElementById('btnGoCheckout');

    if (!body) return;

    if (this.items.length === 0) {
      body.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">☕</div>
          <div class="empty-title">Your cart is empty</div>
          <p class="empty-desc">Choose your favorite artisan coffee or treat to get started.</p>
        </div>
      `;
      if (totalEl) totalEl.textContent = '฿0.00';
      if (checkoutBtn) checkoutBtn.setAttribute('disabled', 'true');
      return;
    }

    if (checkoutBtn) checkoutBtn.removeAttribute('disabled');

    let html = '';
    this.items.forEach((item, index) => {
      const optsText = item.selected_options && Object.keys(item.selected_options).length > 0
        ? Object.entries(item.selected_options).map(([k, v]) => `${k}: ${v}`).join(' • ')
        : 'Standard';

      const imgSrc = item.image_url || 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=200&q=80';

      html += `
        <div class="cart-item">
          <img src="${imgSrc}" class="cart-item-img" alt="${item.name}" onerror="this.src='https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=200&q=80'">
          <div class="cart-item-info">
            <div class="cart-item-title">${item.name}</div>
            <div class="cart-item-options">${optsText}</div>
            <div class="cart-item-price">฿${(item.unit_price * item.quantity).toFixed(2)}</div>
            <div class="cart-item-controls">
              <button class="qty-btn" onclick="Cart.updateQuantity(${index}, -1)">-</button>
              <span class="qty-val">${item.quantity}</span>
              <button class="qty-btn" onclick="Cart.updateQuantity(${index}, 1)">+</button>
              <button class="btn-item-remove" onclick="Cart.removeItem(${index})">Remove</button>
            </div>
          </div>
        </div>
      `;
    });

    body.innerHTML = html;
    if (totalEl) totalEl.textContent = `฿${this.getTotal().toFixed(2)}`;
  }
};

window.Cart = Cart;
