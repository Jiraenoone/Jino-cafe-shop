/**
 * Jino Café — Unified REST API Client
 * Decoupled client communicating strictly via REST to FastAPI
 */

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000/api'
  : '/api'; // In Azure SWA with linked backend or reverse proxy

const ADMIN_KEY_STORAGE = 'jinocafe_admin_key';

const Api = {
  getAdminKey() {
    return localStorage.getItem(ADMIN_KEY_STORAGE) || 'dev-admin-key-change-this-in-production';
  },

  setAdminKey(key) {
    localStorage.setItem(ADMIN_KEY_STORAGE, key);
  },

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    try {
      const response = await fetch(url, { ...options, headers });
      
      if (!response.ok) {
        let errDetail = 'An error occurred';
        try {
          const errData = await response.json();
          errDetail = errData.detail || errData.title || JSON.stringify(errData);
        } catch (_) {
          errDetail = `HTTP ${response.status}: ${response.statusText}`;
        }
        throw new Error(errDetail);
      }

      if (response.status === 204) return null;
      return await response.json();
    } catch (err) {
      console.error(`API Error on [${options.method || 'GET'}] ${endpoint}:`, err);
      throw err;
    }
  },

  // ── Public Endpoints ──────────────────────────────────────────────
  async getCategories() {
    return this.request('/categories');
  },

  async getProducts(params = {}) {
    const query = new URLSearchParams();
    if (params.categoryId) query.append('category_id', params.categoryId);
    if (params.search) query.append('search', params.search);
    if (params.skip) query.append('skip', params.skip);
    if (params.limit) query.append('limit', params.limit);

    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request(`/products${qs}`);
  },

  async getProduct(id) {
    return this.request(`/products/${id}`);
  },

  async createOrder(orderData) {
    return this.request('/orders', {
      method: 'POST',
      body: JSON.stringify(orderData)
    });
  },

  async getOrder(orderId, email) {
    return this.request(`/orders/${orderId}?email=${encodeURIComponent(email)}`);
  },

  // ── Admin Endpoints ───────────────────────────────────────────────
  async getAdminOrders(params = {}) {
    const query = new URLSearchParams();
    if (params.status) query.append('status', params.status);
    if (params.email) query.append('email', params.email);
    const qs = query.toString() ? `?${query.toString()}` : '';

    return this.request(`/admin/orders${qs}`, {
      headers: { 'X-Admin-Key': this.getAdminKey() }
    });
  },

  async updateOrderStatus(orderId, status) {
    return this.request(`/admin/orders/${orderId}/status`, {
      method: 'PATCH',
      headers: { 'X-Admin-Key': this.getAdminKey() },
      body: JSON.stringify({ status })
    });
  },

  async createProduct(productData) {
    return this.request('/admin/products', {
      method: 'POST',
      headers: { 'X-Admin-Key': this.getAdminKey() },
      body: JSON.stringify(productData)
    });
  },

  async updateProduct(productId, productData) {
    return this.request(`/admin/products/${productId}`, {
      method: 'PUT',
      headers: { 'X-Admin-Key': this.getAdminKey() },
      body: JSON.stringify(productData)
    });
  },

  async deleteProduct(productId) {
    return this.request(`/admin/products/${productId}`, {
      method: 'DELETE',
      headers: { 'X-Admin-Key': this.getAdminKey() }
    });
  }
};

window.Api = Api;
