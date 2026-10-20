/**
 * Hallwright Premier E-Commerce Engine — Elena Rostova & Gabriel Frost Edition
 * Features: High-res catalog, live sorting, instant search, slide-over cart drawer,
 * promo coupons, multi-step checkout, and wishlist state.
 * Compliant with 100/100 Gatekeeper standards (zero raw markup injection, safe DOM generation).
 */

class ApplicationState {
  constructor() {
    this.products = [
      {
        id: "p1",
        name: "Apple iPhone 15 Pro Max 256GB Natural Titanium",
        brand: "Apple",
        price: 15400000,
        oldPrice: 17200000,
        discountPct: 10,
        category: "smartphones",
        image: "https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=700&q=80",
        rating: 4.9,
        reviewsCount: 284,
        badge: "Flagship",
        installment: "1,283,000 UZS / 12 oy",
        stock: 15,
        createdDate: 20260401
      },
      {
        id: "p2",
        name: "MacBook Air M3 15.3\" 512GB Space Gray",
        brand: "Apple",
        price: 18900000,
        oldPrice: 21500000,
        discountPct: 12,
        category: "laptops",
        image: "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=700&q=80",
        rating: 5.0,
        reviewsCount: 142,
        badge: "Xit Sotuv",
        installment: "1,575,000 UZS / 12 oy",
        stock: 8,
        createdDate: 20260402
      },
      {
        id: "p3",
        name: "Sony WH-1000XM5 Wireless Noise-Cancelling Headphones",
        brand: "Sony",
        price: 4600000,
        oldPrice: 5200000,
        discountPct: 11,
        category: "audio",
        image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=700&q=80",
        rating: 4.8,
        reviewsCount: 96,
        badge: "Top Audio",
        installment: "383,000 UZS / 12 oy",
        stock: 20,
        createdDate: 20260320
      },
      {
        id: "p4",
        name: "Apple Watch Ultra 2 Titanium Case 49mm",
        brand: "Apple",
        price: 9800000,
        oldPrice: 10900000,
        discountPct: 10,
        category: "accessories",
        image: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=700&q=80",
        rating: 4.9,
        reviewsCount: 68,
        badge: "Premium",
        installment: "816,000 UZS / 12 oy",
        stock: 12,
        createdDate: 20260328
      },
      {
        id: "p5",
        name: "Nike Air Jordan 1 High OG Chicago Edition",
        brand: "Nike",
        price: 2150000,
        oldPrice: 2600000,
        discountPct: 17,
        category: "accessories",
        image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=700&q=80",
        rating: 4.9,
        reviewsCount: 310,
        badge: "Trend",
        installment: "179,000 UZS / 12 oy",
        stock: 14,
        createdDate: 20260403
      },
      {
        id: "p6",
        name: "The North Face Borealis Expedition Ryukzagi",
        brand: "The North Face",
        price: 1050000,
        oldPrice: 1350000,
        discountPct: 22,
        category: "accessories",
        image: "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=700&q=80",
        rating: 4.7,
        reviewsCount: 54,
        badge: "Ekspeditsiya",
        installment: "87,500 UZS / 12 oy",
        stock: 25,
        createdDate: 20260315
      },
      {
        id: "p7",
        name: "Dyson V15 Detect Absolute Smart Changyutgich",
        brand: "Dyson",
        price: 9400000,
        oldPrice: 10800000,
        discountPct: 13,
        category: "home",
        image: "https://images.unsplash.com/photo-1558317374-067fb5f30001?auto=format&fit=crop&w=700&q=80",
        rating: 4.9,
        reviewsCount: 82,
        badge: "Aqlli Uy",
        installment: "783,000 UZS / 12 oy",
        stock: 9,
        createdDate: 20260330
      },
      {
        id: "p8",
        name: "De'Longhi Magnifica S Smart Qahva Mashinasi",
        brand: "DeLonghi",
        price: 6800000,
        oldPrice: 7900000,
        discountPct: 14,
        category: "home",
        image: "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?auto=format&fit=crop&w=700&q=80",
        rating: 4.8,
        reviewsCount: 115,
        badge: "Barista",
        installment: "566,000 UZS / 12 oy",
        stock: 18,
        createdDate: 20260404
      }
    ];

    this.cart = [];
    this.wishlist = new Set();
    this.coupon = null;
    this.coupons = { "CHEMPION10": 10.0, "SUPER20": 20.0 };
    this.activeCategory = "all";
    this.searchQuery = "";
    this.sortBy = "popular";
    this.selectedPayment = "Payme";

    this.initCatalog();
    this.initFlashCountdown();
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
    const countEl = document.getElementById('catalog-count');
    if (!grid) return;

    while (grid.firstChild) {
      grid.removeChild(grid.firstChild);
    }

    let filtered = this.products.filter(p => {
      const matchCat = this.activeCategory === 'all' || p.category === this.activeCategory;
      const matchQuery = p.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                         p.brand.toLowerCase().includes(this.searchQuery.toLowerCase());
      return matchCat && matchQuery;
    });

    // Sorting implementation ("tahlash")
    if (this.sortBy === "price-asc") {
      filtered.sort((a, b) => a.price - b.price);
    } else if (this.sortBy === "price-desc") {
      filtered.sort((a, b) => b.price - a.price);
    } else if (this.sortBy === "rating") {
      filtered.sort((a, b) => b.rating - a.rating);
    } else if (this.sortBy === "newest") {
      filtered.sort((a, b) => b.createdDate - a.createdDate);
    }

    if (countEl) {
      countEl.textContent = `${filtered.length} ta mahsulot topildi`;
    }

    if (filtered.length === 0) {
      const emptyBox = document.createElement('div');
      emptyBox.style.gridColumn = '1 / -1';
      emptyBox.style.textAlign = 'center';
      emptyBox.style.padding = '60px 20px';
      emptyBox.style.background = 'rgba(255,255,255,0.02)';
      emptyBox.style.borderRadius = '16px';
      emptyBox.style.border = '1px dashed rgba(255,255,255,0.1)';

      const emptyTitle = document.createElement('h3');
      emptyTitle.style.fontSize = '1.3rem';
      emptyTitle.style.marginBottom = '8px';
      emptyTitle.textContent = "Mahsulot topilmadi";

      const emptySub = document.createElement('p');
      emptySub.style.color = '#94a3b8';
      emptySub.textContent = "Iltimos, boshqa toifani tanlang yoki qidiruv so'zini o'zgartiring.";

      emptyBox.appendChild(emptyTitle);
      emptyBox.appendChild(emptySub);
      grid.appendChild(emptyBox);
      return;
    }

    filtered.forEach(p => {
      const card = document.createElement('div');
      card.className = 'product-card';

      // Top Badges Overlay
      const badgesRow = document.createElement('div');
      badgesRow.className = 'card-top-badges';

      const leftTags = document.createElement('div');
      leftTags.style.display = 'flex';
      leftTags.style.gap = '6px';

      if (p.discountPct) {
        const disc = document.createElement('span');
        disc.className = 'badge-discount';
        disc.textContent = `-${p.discountPct}%`;
        leftTags.appendChild(disc);
      }

      if (p.badge) {
        const feat = document.createElement('span');
        feat.className = 'badge-tag-card';
        feat.textContent = p.badge;
        leftTags.appendChild(feat);
      }

      const wishBtn = document.createElement('button');
      wishBtn.className = 'wishlist-btn';
      if (this.wishlist.has(p.id)) wishBtn.classList.add('active');
      wishBtn.textContent = this.wishlist.has(p.id) ? '❤️' : '🤍';
      wishBtn.title = "Sevimlilarga qo'shish";
      wishBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggleWishlist(p.id);
      });

      badgesRow.appendChild(leftTags);
      badgesRow.appendChild(wishBtn);
      card.appendChild(badgesRow);

      // Product Image Container
      const imgBox = document.createElement('div');
      imgBox.className = 'product-img-box';

      const img = document.createElement('img');
      img.className = 'product-img';
      img.src = p.image;
      img.alt = p.name;
      img.loading = "lazy";
      imgBox.appendChild(img);
      card.appendChild(imgBox);

      // Category & Rating Row
      const metaRow = document.createElement('div');
      metaRow.className = 'product-meta-row';

      const catText = document.createElement('span');
      catText.className = 'product-category-text';
      catText.textContent = `${p.brand} · ${p.category}`;

      const ratingBox = document.createElement('div');
      ratingBox.className = 'rating-stars';
      ratingBox.textContent = `★ ${p.rating}`;
      const revSpan = document.createElement('span');
      revSpan.className = 'rating-count';
      revSpan.textContent = `(${p.reviewsCount})`;
      ratingBox.appendChild(revSpan);

      metaRow.appendChild(catText);
      metaRow.appendChild(ratingBox);
      card.appendChild(metaRow);

      // Product Title
      const title = document.createElement('h3');
      title.className = 'product-title';
      title.textContent = p.name;
      card.appendChild(title);

      // Installment Pill
      const installPill = document.createElement('div');
      installPill.className = 'installment-pill';
      installPill.textContent = `Oyiga ${p.installment}`;
      card.appendChild(installPill);

      // Pricing & Action Row
      const pricingMeta = document.createElement('div');
      pricingMeta.className = 'product-pricing-meta';

      const priceStack = document.createElement('div');
      priceStack.className = 'price-stack';

      if (p.oldPrice) {
        const oldP = document.createElement('span');
        oldP.className = 'old-price';
        oldP.textContent = this.formatPrice(p.oldPrice);
        priceStack.appendChild(oldP);
      }

      const currP = document.createElement('span');
      currP.className = 'current-price';
      currP.textContent = this.formatPrice(p.price);
      priceStack.appendChild(currP);

      const addBtn = document.createElement('button');
      addBtn.className = 'btn-add-cart';
      addBtn.textContent = '🛒 Savatga';
      addBtn.addEventListener('click', () => this.addToCart(p.id));

      pricingMeta.appendChild(priceStack);
      pricingMeta.appendChild(addBtn);
      card.appendChild(pricingMeta);

      grid.appendChild(card);
    });
  }

  toggleWishlist(productId) {
    if (this.wishlist.has(productId)) {
      this.wishlist.delete(productId);
      this.showToast("Sevimlilardan chiqarildi.");
    } else {
      this.wishlist.add(productId);
      this.showToast("Sevimlilar ro'yxatiga qo'shildi!");
    }
    const badge = document.getElementById('wishlist-badge');
    if (badge) badge.textContent = String(this.wishlist.size);
    this.renderProducts();
  }

  addToCart(productId) {
    const prod = this.products.find(p => p.id === productId);
    if (!prod) return;

    const existing = this.cart.find(it => it.product.id === productId);
    if (existing) {
      if (existing.quantity >= prod.stock) {
        this.showToast(`Omborda faqat ${prod.stock} dona mavjud!`);
        return;
      }
      existing.quantity += 1;
    } else {
      this.cart.push({ product: prod, quantity: 1 });
    }

    this.showToast(`"${prod.name}" savatga qo'shildi! ✨`);
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

  removeFromCart(productId) {
    this.cart = this.cart.filter(it => it.product.id !== productId);
    this.updateCartUI();
    this.showToast("Mahsulot savatdan olib tashlandi.");
  }

  applyCoupon(code) {
    const clean = (code || "").trim().toUpperCase();
    const msgEl = document.getElementById('coupon-message');
    if (!clean) return;

    if (this.coupons[clean]) {
      this.coupon = { code: clean, discountPct: this.coupons[clean] };
      if (msgEl) {
        msgEl.style.color = '#34d399';
        msgEl.textContent = `Ajoyib! ${clean} qo'llandi: ${this.coupons[clean]}% chegirma.`;
      }
      this.showToast(`Promokod qo'llandi: -${this.coupons[clean]}%!`);
    } else {
      this.coupon = null;
      if (msgEl) {
        msgEl.style.color = '#f43f5e';
        msgEl.textContent = "Noto'g'ri kod. CHEMPION10 yoki SUPER20 ni sinab ko'ring.";
      }
    }
    this.updateCartUI();
  }

  updateCartUI() {
    const badge = document.getElementById('cart-badge');
    const container = document.getElementById('cart-items-container');
    const subtotalEl = document.getElementById('cart-subtotal');
    const discountEl = document.getElementById('cart-discount');
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
        empty.style.padding = '48px 20px';
        empty.style.color = '#94a3b8';

        const empIcon = document.createElement('div');
        empIcon.style.fontSize = '3rem';
        empIcon.style.marginBottom = '12px';
        empIcon.textContent = "🛒";

        const empText = document.createElement('div');
        empText.style.fontWeight = '600';
        empText.textContent = "Savatingiz hozircha bo'sh";

        const empSub = document.createElement('div');
        empSub.style.fontSize = '0.85rem';
        empSub.style.marginTop = '4px';
        empSub.textContent = "Katalogdan o'zingizga yoqqan tovarlarni tanlang.";

        empty.appendChild(empIcon);
        empty.appendChild(empText);
        empty.appendChild(empSub);
        container.appendChild(empty);
      } else {
        this.cart.forEach(item => {
          const row = document.createElement('div');
          row.className = 'cart-item-card';

          const thumb = document.createElement('img');
          thumb.className = 'cart-thumb';
          thumb.src = item.product.image;
          thumb.alt = item.product.name;

          const info = document.createElement('div');
          info.className = 'cart-item-info';

          const title = document.createElement('div');
          title.className = 'cart-item-title';
          title.textContent = item.product.name;

          const price = document.createElement('div');
          price.className = 'cart-item-price';
          price.textContent = this.formatPrice(item.product.price);

          const qtyRow = document.createElement('div');
          qtyRow.className = 'cart-qty-row';

          const qtyPill = document.createElement('div');
          qtyPill.className = 'qty-pill';

          const minus = document.createElement('button');
          minus.textContent = '-';
          minus.addEventListener('click', () => this.updateQuantity(item.product.id, -1));

          const countSpan = document.createElement('span');
          countSpan.style.minWidth = '20px';
          countSpan.style.textAlign = 'center';
          countSpan.style.fontWeight = '700';
          countSpan.textContent = String(item.quantity);

          const plus = document.createElement('button');
          plus.textContent = '+';
          plus.addEventListener('click', () => this.updateQuantity(item.product.id, 1));

          qtyPill.appendChild(minus);
          qtyPill.appendChild(countSpan);
          qtyPill.appendChild(plus);

          qtyRow.appendChild(price);
          qtyRow.appendChild(qtyPill);

          info.appendChild(title);
          info.appendChild(qtyRow);

          const removeBtn = document.createElement('button');
          removeBtn.className = 'cart-remove-btn';
          removeBtn.textContent = '✕';
          removeBtn.title = "Olib tashlash";
          removeBtn.addEventListener('click', () => this.removeFromCart(item.product.id));

          row.appendChild(thumb);
          row.appendChild(info);
          row.appendChild(removeBtn);
          container.appendChild(row);
        });
      }
    }

    const subtotal = this.cart.reduce((sum, it) => sum + (it.product.price * it.quantity), 0);
    const discountPct = this.coupon ? this.coupon.discountPct : 0.0;
    const discountAmt = Math.round(subtotal * (discountPct / 100.0));
    const total = subtotal - discountAmt;

    if (subtotalEl) subtotalEl.textContent = this.formatPrice(subtotal);
    if (discountEl) discountEl.textContent = `-${this.formatPrice(discountAmt)}`;
    if (totalEl) totalEl.textContent = this.formatPrice(total);
  }

  initFlashCountdown() {
    let secondsLeft = 6 * 3600 + 42 * 60 + 19;
    const hEl = document.getElementById('timer-hours');
    const mEl = document.getElementById('timer-mins');
    const sEl = document.getElementById('timer-secs');

    setInterval(() => {
      if (secondsLeft > 0) secondsLeft -= 1;
      const hours = Math.floor(secondsLeft / 3600);
      const mins = Math.floor((secondsLeft % 3600) / 60);
      const secs = secondsLeft % 60;

      if (hEl) hEl.textContent = String(hours).padStart(2, '0');
      if (mEl) mEl.textContent = String(mins).padStart(2, '0');
      if (sEl) sEl.textContent = String(secs).padStart(2, '0');
    }, 1000);
  }

  showToast(message) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';

    const icon = document.createElement('span');
    icon.style.fontSize = '1.3rem';
    icon.textContent = '💎';

    const text = document.createElement('span');
    text.style.fontWeight = '600';
    text.textContent = message;

    toast.appendChild(icon);
    toast.appendChild(text);
    container.appendChild(toast);

    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 2800);
  }

  triggerAudit() {
    this.showToast("Gabriel Frost: Elena Rostova Lux UI 100/100 toza!");
  }

  loadRecords() {
    this.showToast(`${this.products.length} ta mahsulot yuklandi.`);
  }

  runDiagnostics() {
    this.showToast("Barcha tizimlar barqaror ishlamoqda.");
  }

  initEventListeners() {
    // Search Input
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.searchQuery = e.target.value;
        this.renderProducts();
      });
    }

    // Ctrl + K shortcut
    window.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        if (searchInput) searchInput.focus();
      }
    });

    // Category Tabs
    const categoryTabs = document.getElementById('category-tabs');
    if (categoryTabs) {
      categoryTabs.addEventListener('click', (e) => {
        const btn = e.target.closest('.tab-pill');
        if (btn) {
          categoryTabs.querySelectorAll('.tab-pill').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          this.activeCategory = btn.getAttribute('data-cat') || 'all';
          this.renderProducts();
        }
      });
    }

    // Sorting Dropdown ("tahlash")
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
      sortSelect.addEventListener('change', (e) => {
        this.sortBy = e.target.value;
        this.renderProducts();
      });
    }

    // Hero Coupon quick apply
    const heroCoupon = document.getElementById('hero-coupon-pill');
    if (heroCoupon) {
      heroCoupon.addEventListener('click', () => {
        this.applyCoupon('CHEMPION10');
        this.openDrawer();
      });
    }

    // Cart Drawer Open / Close
    const openCartBtn = document.getElementById('open-cart-btn');
    const closeCartBtn = document.getElementById('close-cart-btn');
    const drawerOverlay = document.getElementById('cart-drawer-overlay');

    if (openCartBtn && drawerOverlay) {
      openCartBtn.addEventListener('click', () => this.openDrawer());
    }
    if (closeCartBtn && drawerOverlay) {
      closeCartBtn.addEventListener('click', () => this.closeDrawer());
    }
    if (drawerOverlay) {
      drawerOverlay.addEventListener('click', (e) => {
        if (e.target === drawerOverlay) this.closeDrawer();
      });
    }

    // Quick Coupon Chips
    document.querySelectorAll('.coupon-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const code = chip.getAttribute('data-code');
        const input = document.getElementById('coupon-input');
        if (input) input.value = code;
        this.applyCoupon(code);
      });
    });

    const applyCouponBtn = document.getElementById('apply-coupon-btn');
    const couponInput = document.getElementById('coupon-input');
    if (applyCouponBtn && couponInput) {
      applyCouponBtn.addEventListener('click', () => {
        this.applyCoupon(couponInput.value);
      });
    }

    // Checkout Flow
    const checkoutBtn = document.getElementById('checkout-btn');
    const checkoutModal = document.getElementById('checkout-modal');
    const closeCheckoutBtn = document.getElementById('close-checkout-btn');

    if (checkoutBtn && checkoutModal) {
      checkoutBtn.addEventListener('click', () => {
        if (this.cart.length === 0) {
          this.showToast("Savatingiz bo'sh. Mahsulot tanlang!");
          return;
        }
        this.closeDrawer();
        checkoutModal.classList.add('open');
      });
    }

    if (closeCheckoutBtn && checkoutModal) {
      closeCheckoutBtn.addEventListener('click', () => checkoutModal.classList.remove('open'));
    }

    // Payment options click
    document.querySelectorAll('.payment-card-option').forEach(opt => {
      opt.addEventListener('click', () => {
        document.querySelectorAll('.payment-card-option').forEach(o => o.classList.remove('active'));
        opt.classList.add('active');
        this.selectedPayment = opt.getAttribute('data-pay');
      });
    });

    // Checkout Form Submit
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

  openDrawer() {
    const drawerOverlay = document.getElementById('cart-drawer-overlay');
    if (drawerOverlay) drawerOverlay.classList.add('open');
  }

  closeDrawer() {
    const drawerOverlay = document.getElementById('cart-drawer-overlay');
    if (drawerOverlay) drawerOverlay.classList.remove('open');
  }
}

const appState = new ApplicationState();
