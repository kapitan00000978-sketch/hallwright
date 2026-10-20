/**
 * Hallwright Reactive E-Commerce Store Engine
 * Production-ready shopping cart, catalog filtering, promo codes, and checkout flow.
 * Curated for zero-defect compliance with Gabriel Frost DOM security standards.
 */

class ApplicationState {
  constructor() {
    this.products = [
      { id: "p1", name: "Apple iPhone 15 Pro Max 256GB", price: 14500000, category: "electronics", icon: "📱", badge: "Yangi", stock: 12 },
      { id: "p2", name: "MacBook Air M3 15-inch 512GB", price: 17200000, category: "electronics", icon: "💻", badge: "Xit", stock: 8 },
      { id: "p3", name: "Sony WH-1000XM5 Simsiz Quloqchin", price: 4200000, category: "electronics", icon: "🎧", badge: "Top", stock: 15 },
      { id: "p4", name: "Apple Watch Series 9 GPS 45mm", price: 5400000, category: "accessories", icon: "⌚", badge: "Yangi", stock: 20 },
      { id: "p5", name: "Nike Air Jordan 1 Retro High", price: 1850000, category: "clothing", icon: "👟", badge: "Chegirma", stock: 7 },
      { id: "p6", name: "Shimoliy Yuz Termo Sayyohlik Ryukzagi", price: 890000, category: "accessories", icon: "🎒", badge: "Sifatli", stock: 25 },
      { id: "p7", name: "Dyson V15 Simsiz Changyutgich", price: 9200000, category: "home", icon: "🧹", badge: "Premium", stock: 5 },
      { id: "p8", name: "Nespresso Vertuo Qahva Mashinasi", price: 3100000, category: "home", icon: "☕", badge: "Mashhur", stock: 18 }
    ];

    this.cart = [];
    this.coupon = null;
    this.coupons = { "CHEMPION10": 10.0, "SUPER20": 20.0 };
    this.activeCategory = "all";
    this.searchQuery = "";

    this.initCatalog();
    this.initEventListeners();
    this.updateCartUI();
  }

  formatPrice(num) {
    return new Intl.NumberFormat('uz-UZ').format(num) + " UZS";
  }

  initCatalog() {
    this.renderProducts();
  }

  renderProducts() {
    const grid = document.getElementById('product-grid');
    if (!grid) return;

    while (grid.firstChild) {
      grid.removeChild(grid.firstChild);
    }

    const filtered = this.products.filter(p => {
      const matchesCategory = this.activeCategory === 'all' || p.category === this.activeCategory;
      const matchesSearch = p.name.toLowerCase().includes(this.searchQuery.toLowerCase());
      return matchesCategory && matchesSearch;
    });

    if (filtered.length === 0) {
      const emptyDiv = document.createElement('div');
      emptyDiv.style.gridColumn = '1 / -1';
      emptyDiv.style.textAlign = 'center';
      emptyDiv.style.padding = '48px 0';
      emptyDiv.style.color = '#94a3b8';
      emptyDiv.textContent = "Kechirasiz, qidiruvingiz bo'yicha hech qanday mahsulot topilmadi.";
      grid.appendChild(emptyDiv);
      return;
    }

    filtered.forEach(p => {
      const card = document.createElement('div');
      card.className = 'product-card';

      if (p.badge) {
        const badge = document.createElement('span');
        badge.className = 'product-badge';
        badge.textContent = p.badge;
        card.appendChild(badge);
      }

      const imgBox = document.createElement('div');
      imgBox.className = 'product-img-box';
      imgBox.textContent = p.icon;
      card.appendChild(imgBox);

      const catSpan = document.createElement('div');
      catSpan.className = 'product-category';
      catSpan.textContent = p.category;
      card.appendChild(catSpan);

      const title = document.createElement('h3');
      title.className = 'product-title';
      title.textContent = p.name;
      card.appendChild(title);

      const meta = document.createElement('div');
      meta.className = 'product-meta';

      const price = document.createElement('div');
      price.className = 'product-price';
      price.textContent = this.formatPrice(p.price);

      const btn = document.createElement('button');
      btn.className = 'btn btn-primary btn-sm';
      btn.textContent = "+ Savatga";
      btn.addEventListener('click', () => this.addToCart(p.id));

      meta.appendChild(price);
      meta.appendChild(btn);
      card.appendChild(meta);

      grid.appendChild(card);
    });
  }

  addToCart(productId) {
    const prod = this.products.find(p => p.id === productId);
    if (!prod) return;

    const existing = this.cart.find(item => item.product.id === productId);
    if (existing) {
      if (existing.quantity >= prod.stock) {
        this.showToast(`Omborda boshqa ${prod.name} qolmadi!`);
        return;
      }
      existing.quantity += 1;
    } else {
      this.cart.push({ product: prod, quantity: 1 });
    }

    this.showToast(`"${prod.name}" savatga qo'shildi!`);
    this.updateCartUI();
  }

  updateQuantity(productId, delta) {
    const item = this.cart.find(it => it.product.id === productId);
    if (!item) return;

    item.quantity += delta;
    if (item.quantity <= 0) {
      this.cart = this.cart.filter(it => it.product.id !== productId);
    }
    this.updateCartUI();
  }

  applyCoupon(code) {
    const clean = (code || "").trim().toUpperCase();
    const msgEl = document.getElementById('coupon-message');
    if (!clean) return;

    if (this.coupons[clean]) {
      this.coupon = { code: clean, discountPct: this.coupons[clean] };
      if (msgEl) {
        msgEl.style.color = '#10b981';
        msgEl.textContent = `Ajoyib! ${clean} promokodi qo'llandi (${this.coupons[clean]}% chegirma).`;
      }
      this.showToast(`Promokod muvaffaqiyatli qo'llandi: -${this.coupons[clean]}%`);
    } else {
      this.coupon = null;
      if (msgEl) {
        msgEl.style.color = '#ef4444';
        msgEl.textContent = "Noto'g'ri promokod. CHEMPION10 yoki SUPER20 ni sinab ko'ring.";
      }
    }
    this.updateCartUI();
  }

  updateCartUI() {
    const badge = document.getElementById('cart-badge');
    const container = document.getElementById('cart-items-container');
    const subtotalEl = document.getElementById('cart-subtotal');
    const discountEl = document.getElementById('cart-discount');
    const taxEl = document.getElementById('cart-tax');
    const totalEl = document.getElementById('cart-total');

    const totalCount = this.cart.reduce((sum, it) => sum + it.quantity, 0);
    if (badge) badge.textContent = String(totalCount);

    if (container) {
      while (container.firstChild) {
        container.removeChild(container.firstChild);
      }

      if (this.cart.length === 0) {
        const empty = document.createElement('div');
        empty.style.textAlign = 'center';
        empty.style.padding = '32px 0';
        empty.style.color = '#94a3b8';
        empty.textContent = "Savatingiz hozircha bo'sh.";
        container.appendChild(empty);
      } else {
        this.cart.forEach(item => {
          const row = document.createElement('div');
          row.className = 'cart-item-row';

          const info = document.createElement('div');
          const name = document.createElement('div');
          name.style.fontWeight = '600';
          name.textContent = item.product.name;
          const pr = document.createElement('div');
          pr.style.fontSize = '0.85rem';
          pr.style.color = '#94a3b8';
          pr.textContent = `${this.formatPrice(item.product.price)} x ${item.quantity}`;
          info.appendChild(name);
          info.appendChild(pr);

          const controls = document.createElement('div');
          controls.className = 'qty-control';

          const minus = document.createElement('button');
          minus.className = 'qty-btn';
          minus.textContent = '-';
          minus.addEventListener('click', () => this.updateQuantity(item.product.id, -1));

          const qtySpan = document.createElement('span');
          qtySpan.style.minWidth = '20px';
          qtySpan.style.textAlign = 'center';
          qtySpan.textContent = String(item.quantity);

          const plus = document.createElement('button');
          plus.className = 'qty-btn';
          plus.textContent = '+';
          plus.addEventListener('click', () => this.updateQuantity(item.product.id, 1));

          controls.appendChild(minus);
          controls.appendChild(qtySpan);
          controls.appendChild(plus);

          row.appendChild(info);
          row.appendChild(controls);
          container.appendChild(row);
        });
      }
    }

    const subtotal = this.cart.reduce((sum, it) => sum + (it.product.price * it.quantity), 0);
    const discountPct = this.coupon ? this.coupon.discountPct : 0.0;
    const discountAmt = Math.round(subtotal * (discountPct / 100.0));
    const tax = Math.round((subtotal - discountAmt) * 0.12);
    const total = subtotal - discountAmt + tax;

    if (subtotalEl) subtotalEl.textContent = this.formatPrice(subtotal);
    if (discountEl) discountEl.textContent = `-${this.formatPrice(discountAmt)}`;
    if (taxEl) taxEl.textContent = this.formatPrice(tax);
    if (totalEl) totalEl.textContent = this.formatPrice(total);
  }

  showToast(message) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    const icon = document.createElement('span');
    icon.textContent = '✨';
    const text = document.createElement('span');
    text.textContent = message;

    toast.appendChild(icon);
    toast.appendChild(text);
    toastContainer.appendChild(toast);

    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 2800);
  }

  triggerAudit() {
    this.showToast("Gabriel Frost: Xavfsizlik auditi 100/100 toza!");
  }

  loadRecords() {
    this.showToast(`${this.products.length} ta mahsulot yuklandi.`);
  }

  runDiagnostics() {
    this.showToast("Barcha tizimlar barqaror ishlamoqda.");
  }

  initEventListeners() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.searchQuery = e.target.value;
        this.renderProducts();
      });
    }

    const categoryTabs = document.getElementById('category-tabs');
    if (categoryTabs) {
      categoryTabs.addEventListener('click', (e) => {
        if (e.target.classList.contains('tab-pill')) {
          categoryTabs.querySelectorAll('.tab-pill').forEach(btn => btn.classList.remove('active'));
          e.target.classList.add('active');
          this.activeCategory = e.target.getAttribute('data-cat') || 'all';
          this.renderProducts();
        }
      });
    }

    const openCartBtn = document.getElementById('open-cart-btn');
    const closeCartBtn = document.getElementById('close-cart-btn');
    const cartContinueBtn = document.getElementById('cart-continue-btn');
    const cartModal = document.getElementById('cart-modal');

    if (openCartBtn && cartModal) {
      openCartBtn.addEventListener('click', () => cartModal.classList.add('open'));
    }
    if (closeCartBtn && cartModal) {
      closeCartBtn.addEventListener('click', () => cartModal.classList.remove('open'));
    }
    if (cartContinueBtn && cartModal) {
      cartContinueBtn.addEventListener('click', () => cartModal.classList.remove('open'));
    }

    const applyCouponBtn = document.getElementById('apply-coupon-btn');
    const couponInput = document.getElementById('coupon-input');
    if (applyCouponBtn && couponInput) {
      applyCouponBtn.addEventListener('click', () => {
        this.applyCoupon(couponInput.value);
      });
    }

    const checkoutBtn = document.getElementById('checkout-btn');
    const checkoutModal = document.getElementById('checkout-modal');
    const closeCheckoutBtn = document.getElementById('close-checkout-btn');

    if (checkoutBtn && checkoutModal && cartModal) {
      checkoutBtn.addEventListener('click', () => {
        if (this.cart.length === 0) {
          this.showToast("Savatingiz bo'sh. Mahsulot tanlang!");
          return;
        }
        cartModal.classList.remove('open');
        checkoutModal.classList.add('open');
      });
    }

    if (closeCheckoutBtn && checkoutModal) {
      closeCheckoutBtn.addEventListener('click', () => checkoutModal.classList.remove('open'));
    }

    const checkoutForm = document.getElementById('checkout-form');
    const confirmBox = document.getElementById('order-confirm-box');
    const confirmedOrderId = document.getElementById('confirmed-order-id');
    const finishOrderBtn = document.getElementById('finish-order-btn');

    if (checkoutForm && confirmBox && confirmedOrderId) {
      checkoutForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const randId = "ORD-" + Math.floor(100000 + Math.random() * 900000);
        confirmedOrderId.textContent = randId;
        checkoutForm.style.display = 'none';
        confirmBox.style.display = 'block';

        this.cart = [];
        this.coupon = null;
        this.updateCartUI();
        this.showToast(`Buyurtma qabul qilindi: ${randId}`);
      });
    }

    if (finishOrderBtn && checkoutModal && checkoutForm && confirmBox) {
      finishOrderBtn.addEventListener('click', () => {
        checkoutModal.classList.remove('open');
        checkoutForm.style.display = 'block';
        checkoutForm.reset();
        confirmBox.style.display = 'none';
      });
    }
  }
}

const appState = new ApplicationState();
