/**
 * Jino Café — Menu Controller
 * Handles product browsing, category filtering, search, and option modal
 */

const DEFAULT_IMAGE_MAP = {
  'Signature Latte': 'https://images.unsplash.com/photo-1541167760496-1628856ab772?auto=format&fit=crop&w=600&q=80',
  'Americano': 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=600&q=80',
  'Cappuccino': 'https://images.unsplash.com/photo-1572442388796-11668a67e53d?auto=format&fit=crop&w=600&q=80',
  'Cold Brew': 'https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?auto=format&fit=crop&w=600&q=80',
  'Caramel Macchiato': 'https://images.unsplash.com/photo-1485808191679-5f86510681a2?auto=format&fit=crop&w=600&q=80',
  'Thai Milk Tea': 'https://images.unsplash.com/photo-1558857563-b37fe6581177?auto=format&fit=crop&w=600&q=80',
  'Matcha Latte': 'https://images.unsplash.com/photo-1536256263959-770b48d82b0a?auto=format&fit=crop&w=600&q=80',
  'Jasmine Green Tea': 'https://images.unsplash.com/photo-1627435601361-ec25f5b1d0e5?auto=format&fit=crop&w=600&q=80',
  'Mango Smoothie': 'https://images.unsplash.com/photo-1623065422902-30a2d299bbe4?auto=format&fit=crop&w=600&q=80',
  'Mixed Berry': 'https://images.unsplash.com/photo-1553530666-ba11a7da3888?auto=format&fit=crop&w=600&q=80',
  'Butter Croissant': 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=600&q=80',
  'Banana Bread': 'https://images.unsplash.com/photo-1605698802011-309855b376d8?auto=format&fit=crop&w=600&q=80',
  'Chocolate Muffin': 'https://images.unsplash.com/photo-1607958996333-41aef7caefaa?auto=format&fit=crop&w=600&q=80'
};

const Menu = {
  currentCategory: null,
  searchQuery: '',
  allProducts: [],
  selectedProduct: null,
  modalSelectedOptions: {},
  modalQuantity: 1,

  async init() {
    Cart.init();
    await this.loadCategories();
    await this.loadProducts();
    this.attachEvents();
  },

  getProductImage(product) {
    if (product.image_url && product.image_url.startsWith('http')) {
      return product.image_url;
    }
    return DEFAULT_IMAGE_MAP[product.name] || 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=600&q=80';
  },

  async loadCategories() {
    const tabsContainer = document.getElementById('categoryTabs');
    if (!tabsContainer) return;

    try {
      const categories = await Api.getCategories();
      
      let html = `
        <button class="category-tab active" data-id="all">
          <span>☕ All Menu</span>
        </button>
      `;

      categories.forEach(cat => {
        html += `
          <button class="category-tab" data-id="${cat.id}">
            <span>${cat.name}</span>
          </button>
        `;
      });

      tabsContainer.innerHTML = html;

      // Event listener for tabs
      tabsContainer.querySelectorAll('.category-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
          tabsContainer.querySelectorAll('.category-tab').forEach(t => t.classList.remove('active'));
          const btn = e.currentTarget;
          btn.classList.add('active');
          const catId = btn.dataset.id;
          this.currentCategory = catId === 'all' ? null : parseInt(catId);
          this.filterAndRender();
        });
      });
    } catch (err) {
      console.error('Failed to load categories:', err);
    }
  },

  async loadProducts() {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    // Show skeleton loaders
    grid.innerHTML = Array(6).fill(0).map(() => `
      <div class="product-card">
        <div class="card-media skeleton"></div>
        <div class="card-content">
          <div style="height: 20px; width: 60%; margin-bottom: 10px;" class="skeleton"></div>
          <div style="height: 14px; width: 90%; margin-bottom: 16px;" class="skeleton"></div>
          <div style="height: 24px; width: 40%;" class="skeleton"></div>
        </div>
      </div>
    `).join('');

    try {
      const response = await Api.getProducts({ limit: 100 });
      this.allProducts = response.items || [];
      this.filterAndRender();
    } catch (err) {
      grid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <div class="empty-icon">⚠️</div>
          <div class="empty-title">Cannot load café menu</div>
          <p class="empty-desc">${err.message}. Please verify the FastAPI backend is running.</p>
        </div>
      `;
    }
  },

  filterAndRender() {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    let filtered = this.allProducts;

    if (this.currentCategory) {
      filtered = filtered.filter(p => p.category_id === this.currentCategory);
    }

    if (this.searchQuery.trim()) {
      const q = this.searchQuery.toLowerCase().trim();
      filtered = filtered.filter(p => 
        p.name.toLowerCase().includes(q) || (p.description && p.description.toLowerCase().includes(q))
      );
    }

    if (filtered.length === 0) {
      grid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <div class="empty-icon">🔍</div>
          <div class="empty-title">No menu items found</div>
          <p class="empty-desc">Try clearing your search query or selecting another category.</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = filtered.map(p => {
      const img = this.getProductImage(p);
      const hasOptions = p.options && Object.keys(p.options).length > 0;
      return `
        <div class="product-card" data-id="${p.id}">
          <div class="card-media">
            <img src="${img}" alt="${p.name}" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=600&q=80'">
            ${hasOptions ? '<span class="card-badge">Customizable</span>' : ''}
          </div>
          <div class="card-content">
            <h3 class="card-title">${p.name}</h3>
            <p class="card-desc">${p.description || 'Crafted with premium beans and quality ingredients.'}</p>
            <div class="card-footer">
              <div class="card-price"><span>฿</span>${Number(p.price).toFixed(2)}</div>
              <button class="btn-add" onclick="Menu.openProductModal(${p.id})" title="Select options & add">
                +
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');
  },

  openProductModal(productId) {
    const product = this.allProducts.find(p => p.id === productId);
    if (!product) return;

    this.selectedProduct = product;
    this.modalQuantity = 1;
    this.modalSelectedOptions = {};

    const overlay = document.getElementById('productModal');
    const imgEl = document.getElementById('modalProductImg');
    const titleEl = document.getElementById('modalProductTitle');
    const descEl = document.getElementById('modalProductDesc');
    const priceEl = document.getElementById('modalProductPrice');
    const optionsContainer = document.getElementById('modalOptionsContainer');
    const qtyValEl = document.getElementById('modalQtyVal');
    const notesInput = document.getElementById('modalProductNotes');

    if (notesInput) notesInput.value = '';
    if (qtyValEl) qtyValEl.textContent = '1';
    if (imgEl) imgEl.src = this.getProductImage(product);
    if (titleEl) titleEl.textContent = product.name;
    if (descEl) descEl.textContent = product.description || '';
    if (priceEl) priceEl.textContent = `฿${Number(product.price).toFixed(2)}`;

    // Build options list (sizes, temperatures, sweetness)
    let optionsHtml = '';
    if (product.options && typeof product.options === 'object') {
      for (const [key, values] of Object.entries(product.options)) {
        if (Array.isArray(values) && values.length > 0) {
          // Default select first option
          this.modalSelectedOptions[key] = values[0];
          optionsHtml += `
            <div class="option-group">
              <label class="option-label">${key}</label>
              <div class="option-pills" data-option-key="${key}">
                ${values.map((v, i) => `
                  <button type="button" class="option-pill ${i === 0 ? 'selected' : ''}" data-val="${v}">
                    ${v}
                  </button>
                `).join('')}
              </div>
            </div>
          `;
        }
      }
    }

    if (optionsContainer) optionsContainer.innerHTML = optionsHtml;

    // Attach pill events
    if (optionsContainer) {
      optionsContainer.querySelectorAll('.option-pill').forEach(pill => {
        pill.addEventListener('click', (e) => {
          const p = e.currentTarget;
          const parent = p.closest('.option-pills');
          const optKey = parent.dataset.optionKey;
          parent.querySelectorAll('.option-pill').forEach(el => el.classList.remove('selected'));
          p.classList.add('selected');
          this.modalSelectedOptions[optKey] = p.dataset.val;
        });
      });
    }

    if (overlay) overlay.classList.add('active');
  },

  closeModal() {
    const overlay = document.getElementById('productModal');
    if (overlay) overlay.classList.remove('active');
  },

  updateModalQty(delta) {
    this.modalQuantity = Math.max(1, Math.min(20, this.modalQuantity + delta));
    const qtyValEl = document.getElementById('modalQtyVal');
    if (qtyValEl) qtyValEl.textContent = this.modalQuantity;
  },

  confirmAddFromModal() {
    if (!this.selectedProduct) return;
    const notesInput = document.getElementById('modalProductNotes');
    const notes = notesInput ? notesInput.value.trim() : '';

    Cart.addItem(
      this.selectedProduct,
      this.modalQuantity,
      this.modalSelectedOptions,
      notes
    );

    this.closeModal();
  },

  attachEvents() {
    const searchInput = document.getElementById('menuSearchInput');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.searchQuery = e.target.value;
        this.filterAndRender();
      });
    }

    const modalCloseBtn = document.getElementById('modalCloseBtn');
    const modalOverlay = document.getElementById('productModal');
    if (modalCloseBtn) modalCloseBtn.addEventListener('click', () => this.closeModal());
    if (modalOverlay) {
      modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) this.closeModal();
      });
    }
  }
};

window.Menu = Menu;

document.addEventListener('DOMContentLoaded', () => {
  Menu.init();
});
