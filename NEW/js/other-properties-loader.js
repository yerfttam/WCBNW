/**
 * other-properties-loader.js
 *
 * Fetches NEW/data/listings.json and renders the "other-properties"
 * category into the horizontal listing-card layout on other-properties.html.
 */

// Registry of all listings by id — used by modal
const listingRegistry = new Map();

const FEATURE_PRIORITY = [
  'Waterfront', 'Beach access', 'Pets allowed', 'Indoor fireplace',
  'BBQ grill', 'Hot tub', 'Patio or balcony', 'Wireless Internet',
  'Heating', 'Kitchen', 'Parking'
];

function pickFeatures(amenities, n = 4) {
  const set    = new Set(amenities);
  const picked = FEATURE_PRIORITY.filter(f => set.has(f));
  for (const a of amenities) {
    if (picked.length >= n) break;
    if (!picked.includes(a)) picked.push(a);
  }
  return picked.slice(0, n);
}

function renderPrice(price) {
  if (!price || !price.base) return '';
  return `From $${price.base}/night`;
}

// Full modal description — first 2 meaningful paragraphs
function getFullDesc(listing) {
  if (!listing.description) return listing.summary ? [listing.summary] : [];
  const paras = listing.description.split('\n\n').map(p => p.trim()).filter(Boolean);
  const good  = paras.filter(p => !p.startsWith('***') && !p.startsWith('**') && p.length > 40);
  return good.slice(0, 2);
}

function renderCard(listing, index) {
  const isReverse = index % 2 === 1;
  const photos    = (listing.photos && listing.photos.length)
    ? listing.photos
    : [{ original: 'images/bkgds/bkgd1.jpg' }];
  const firstSrc  = photos[0].original;
  const photoData = JSON.stringify(photos.map(p => p.original));

  const dots = photos.map((_, i) =>
    `<span class="lc-dot${i === 0 ? ' active' : ''}"></span>`
  ).join('');

  const arrows = photos.length > 1 ? `
    <button class="lc-btn lc-btn--prev" aria-label="Previous photo">&#8249;</button>
    <button class="lc-btn lc-btn--next" aria-label="Next photo">&#8250;</button>` : '';

  const price = listing.price && listing.price.base
    ? `From $${listing.price.base}/night`
    : '';

  const guests = listing.accommodates ? `${listing.accommodates} guests` : '';
  const beds   = listing.bedrooms     ? `${listing.bedrooms} bed${listing.bedrooms > 1 ? 's' : ''}` : '';
  const baths  = listing.bathrooms    ? `${listing.bathrooms} bath${listing.bathrooms > 1 ? 's' : ''}` : '';
  const meta   = [guests, beds, baths].filter(Boolean).join(' &middot; ');

  const features    = pickFeatures(listing.amenities || []);
  const featureHtml = features.map(f => `<li>${f}</li>`).join('');

  return `
    <div class="listing-card${isReverse ? ' listing-card--reverse' : ''}" data-listing-id="${listing.id}">
      <div class="listing-card-photo">
        <div class="lc-carousel" data-photos='${photoData}' data-index="0">
          <img class="lc-carousel-img"
               src="${firstSrc}"
               alt="${listing.name}"
               loading="lazy"
               onerror="this.src='images/bkgds/bkgd1.jpg'" />
          ${arrows}
          ${photos.length > 1 ? `<div class="lc-dots">${dots}</div>` : ''}
        </div>
      </div>
      <div class="listing-card-info">
        <p class="listing-card-label">Other Properties</p>
        <h2 class="listing-card-name copperplate">${listing.title || listing.name}</h2>
        ${price ? `<p class="listing-card-price">${price}</p>` : ''}
        ${listing.summary ? `<p class="listing-card-desc">${listing.summary}</p>` : ''}
        ${meta ? `<p class="listing-card-meta">${meta}</p>` : ''}
        ${featureHtml ? `<ul class="listing-card-features">${featureHtml}</ul>` : ''}
        <a href="${listing.bookingUrl}" target="_blank" rel="noopener" class="btn-book">Book This Property</a>
      </div>
    </div>`;
}

// ── Modal ────────────────────────────────────────────────────────────────────

let modalPhotoIndex = 0;
let modalPhotos     = [];

function buildModal() {
  const el = document.createElement('div');
  el.id = 'prop-modal';
  el.innerHTML = `
    <div class="modal-overlay"></div>
    <div class="modal-panel">
      <button class="modal-close" aria-label="Close">&times;</button>
      <div class="modal-carousel">
        <img class="modal-img" src="" alt="" />
        <button class="modal-carousel-btn modal-carousel-prev">&#8249;</button>
        <button class="modal-carousel-btn modal-carousel-next">&#8250;</button>
        <div class="modal-dots"></div>
      </div>
      <div class="modal-body">
        <div class="modal-header">
          <div>
            <h2 class="modal-name copperplate"></h2>
            <p class="modal-meta"></p>
          </div>
          <div class="modal-price-wrap">
            <p class="modal-price"></p>
            <a class="modal-book" href="#" target="_blank" rel="noopener">Book Now</a>
          </div>
        </div>
        <div class="modal-desc"></div>
        <div class="modal-amenities-wrap">
          <h3 class="modal-amenities-title copperplate">Amenities</h3>
          <ul class="modal-amenities"></ul>
        </div>
      </div>
    </div>`;
  document.body.appendChild(el);
  return el;
}

function openModal(listing) {
  const modal = document.getElementById('prop-modal');
  modalPhotos     = (listing.photos || []).map(p => p.original);
  modalPhotoIndex = 0;

  const price  = renderPrice(listing.price);
  const guests = listing.accommodates ? `${listing.accommodates} guests` : '';
  const beds   = listing.bedrooms     ? `${listing.bedrooms} bed`        : '';
  const baths  = listing.bathrooms    ? `${listing.bathrooms} bath`      : '';
  const meta   = [guests, beds, baths].filter(Boolean).join(' · ');
  const descParas = getFullDesc(listing);
  const amenities = listing.amenities || [];

  modal.querySelector('.modal-img').src           = modalPhotos[0] || '';
  modal.querySelector('.modal-img').alt           = listing.name;
  modal.querySelector('.modal-name').textContent  = listing.title || listing.name;
  modal.querySelector('.modal-price').textContent = price;
  modal.querySelector('.modal-meta').textContent  = meta;
  modal.querySelector('.modal-desc').innerHTML    = descParas.map(p => `<p>${p}</p>`).join('');
  modal.querySelector('.modal-book').href         = listing.bookingUrl;
  modal.querySelector('.modal-amenities').innerHTML = amenities.map(a => `<li>${a}</li>`).join('');
  modal.querySelector('.modal-amenities-wrap').style.display = amenities.length ? '' : 'none';

  // Dots
  const dotsEl = modal.querySelector('.modal-dots');
  dotsEl.innerHTML = modalPhotos.map((_, i) =>
    `<span class="modal-dot${i === 0 ? ' active' : ''}"></span>`
  ).join('');

  // Arrow visibility
  const showArrows = modalPhotos.length > 1;
  modal.querySelector('.modal-carousel-prev').style.display = showArrows ? '' : 'none';
  modal.querySelector('.modal-carousel-next').style.display = showArrows ? '' : 'none';

  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('prop-modal').classList.remove('open');
  document.body.style.overflow = '';
}

function stepModalPhoto(dir) {
  const modal = document.getElementById('prop-modal');
  modalPhotoIndex = (modalPhotoIndex + dir + modalPhotos.length) % modalPhotos.length;
  modal.querySelector('.modal-img').src = modalPhotos[modalPhotoIndex];
  modal.querySelectorAll('.modal-dot').forEach((d, i) =>
    d.classList.toggle('active', i === modalPhotoIndex)
  );
}

function initModal() {
  const modal = buildModal();

  modal.querySelector('.modal-overlay').addEventListener('click', closeModal);
  modal.querySelector('.modal-close').addEventListener('click', closeModal);

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape')     closeModal();
    if (e.key === 'ArrowLeft')  stepModalPhoto(-1);
    if (e.key === 'ArrowRight') stepModalPhoto(1);
  });

  modal.querySelector('.modal-carousel-prev').addEventListener('click', () => stepModalPhoto(-1));
  modal.querySelector('.modal-carousel-next').addEventListener('click', () => stepModalPhoto(1));

  // Card click → open modal (ignore carousel buttons and book link)
  document.getElementById('listings-container').addEventListener('click', e => {
    if (e.target.closest('.lc-btn'))   return;
    if (e.target.closest('.btn-book')) return;
    const card = e.target.closest('.listing-card');
    if (!card) return;
    const listing = listingRegistry.get(card.dataset.listingId);
    if (listing) openModal(listing);
  });
}

// ── Carousels ────────────────────────────────────────────────────────────────

function initCarousels() {
  const container = document.getElementById('listings-container');
  if (!container) return;

  container.addEventListener('click', e => {
    const btn = e.target.closest('.lc-btn');
    if (!btn) return;

    e.preventDefault();
    const carousel = btn.closest('.lc-carousel');
    const card     = carousel.closest('.listing-card');
    const photos   = JSON.parse(carousel.dataset.photos);
    let   index    = parseInt(carousel.dataset.index, 10);

    if (btn.classList.contains('lc-btn--prev')) {
      index = (index - 1 + photos.length) % photos.length;
    } else {
      index = (index + 1) % photos.length;
    }

    carousel.querySelector('.lc-carousel-img').src = photos[index];
    carousel.dataset.index = index;

    card.querySelectorAll('.lc-dot').forEach((d, i) =>
      d.classList.toggle('active', i === index)
    );
  });
}

// ── Load + init ──────────────────────────────────────────────────────────────

async function loadOtherProperties() {
  const container = document.getElementById('listings-container');
  if (!container) return;

  try {
    const res  = await fetch('data/listings.json');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    const category = data.categories.find(c => c.slug === 'other-properties');
    if (!category || !category.listings.length) {
      container.innerHTML = '<p style="padding:3rem;text-align:center;color:var(--brown);">No listings found.</p>';
      return;
    }

    // Register all listings by id
    category.listings.forEach(l => listingRegistry.set(l.id, l));

    container.innerHTML = category.listings.map(renderCard).join('');

  } catch (err) {
    console.error('other-properties-loader: failed to load listings.json', err);
    container.innerHTML = `
      <div style="padding:4rem 2rem; text-align:center; color:#6b452e;">
        <p>Unable to load property listings. Please try again later.</p>
      </div>`;
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  await loadOtherProperties();
  initCarousels();
  initModal();
});
