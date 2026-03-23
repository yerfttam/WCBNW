/**
 * listings-loader.js
 *
 * Fetches NEW/data/listings.json and dynamically renders the accommodations
 * page: category nav tabs, section headers, and property cards.
 *
 * Matches the existing CSS classes in accommodations.html — no style changes needed.
 */

// Registry of all listings by id — used by modal
const listingRegistry = new Map();

// Section descriptions keyed by category slug.
// These come from the owner, not Guesty — edit here to update copy.
const SECTION_COPY = {
  'beach-front-cabins': {
    label: 'Waterfront Accommodations',
    desc:  'Five individual cabins set directly on the shoreline of the Strait of Juan de Fuca. Each cabin offers a private beachfront experience with stunning ocean views and the sound of waves steps from your door.',
  },
  'cottages': {
    label: 'Cozy Retreats',
    desc:  'Charming cottages tucked into the property, each with its own character. From rustic beachside stays to unique one-of-a-kind accommodations — perfect for couples and small families.',
  },
  'a-frames': {
    label: 'Unique Stays',
    desc:  'Classic A-frame shelters with incredible views of the Olympic Peninsula and the Strait of Juan de Fuca. A great option for adventurers who want to sleep close to nature without giving up comfort.',
  },
  'tent-sites': {
    label: 'Camping',
    desc:  'Designated tent sites set along the beachfront. Wake up to the sound of the waves and the smell of salt air. Bring your own tent and gear — fire rings and picnic tables provided.',
  },
  'rv-sites': {
    label: 'RV & Vehicle Camping',
    desc:  'Full-hookup RV sites with stunning ocean views. Pull in and enjoy all the amenities of Whiskey Creek Beach with the comforts of home on wheels.',
  },
  'other-properties': {
    label: 'Additional Properties',
    desc:  'Unique properties in the Whiskey Creek Beach family that offer a different kind of stay — from forested retreats to off-site cottages near the Lyre River.',
  },
};

// Grid column class per category (matches existing .prop-grid--N classes)
const GRID_CLASS = {
  'beach-front-cabins': '',       // default 3-col
  'cottages':           '',
  'a-frames':           'prop-grid--4',
  'tent-sites':         '',
  'rv-sites':           'prop-grid--2',
  'other-properties':   'prop-grid--2',
};

// Card size modifier per category
const CARD_CLASS = {
  'a-frames':   'prop-card--site',
  'tent-sites': 'prop-card--site',
  'rv-sites':   'prop-card--site',
};

function renderPrice(price) {
  if (!price || !price.base) return '';
  return `From $${price.base}/night`;
}

// Short card description (4 lines max, ~440 chars)
function getListingDesc(listing) {
  if (!listing.description) return listing.summary || '';
  const paras = listing.description.split('\n\n').map(p => p.trim()).filter(Boolean);
  const para  = paras.find(p => !p.startsWith('***') && !p.startsWith('**') && p.length > 40) || paras[0] || '';
  const clean = para.replace(/^\*+\s*/g, '').replace(/\*+\s*/g, '').trim();
  return clean.length > 440 ? clean.slice(0, 440).replace(/\s+\S*$/, '') + '…' : clean;
}

// Full modal description — first 2 meaningful paragraphs
function getFullDesc(listing) {
  if (!listing.description) return listing.summary ? [listing.summary] : [];
  const paras = listing.description.split('\n\n').map(p => p.trim()).filter(Boolean);
  const good  = paras.filter(p => !p.startsWith('***') && !p.startsWith('**') && p.length > 40);
  return good.slice(0, 2);
}

function renderCard(listing, slug) {
  const photos   = (listing.photos && listing.photos.length) ? listing.photos : [{ original: 'images/bkgds/bkgd1.jpg' }];
  const firstSrc = photos[0].original;
  const cardMod  = CARD_CLASS[slug] || '';
  const price    = renderPrice(listing.price);
  const guests   = listing.accommodates ? `${listing.accommodates} guests` : '';
  const beds     = listing.bedrooms     ? `${listing.bedrooms} bd`         : '';
  const baths    = listing.bathrooms    ? `${listing.bathrooms} ba`        : '';
  const meta     = [guests, beds, baths].filter(Boolean).join(' &middot; ');

  // Encode photo URLs as a data attribute for the carousel JS
  const photoData = JSON.stringify(photos.map(p => p.original));

  // Dots — one per photo
  const dots = photos.map((_, i) =>
    `<span class="prop-dot${i === 0 ? ' active' : ''}"></span>`
  ).join('');

  // Only render arrows if there's more than one photo
  const arrows = photos.length > 1 ? `
    <button class="carousel-btn carousel-btn--prev" aria-label="Previous photo">&#8249;</button>
    <button class="carousel-btn carousel-btn--next" aria-label="Next photo">&#8250;</button>` : '';

  return `
    <div class="prop-card ${cardMod}" data-listing-id="${listing.id}">
      <div class="prop-card-carousel" data-photos='${photoData}' data-index="0">
        <img class="prop-card-img"
             src="${firstSrc}"
             alt="${listing.name}"
             loading="lazy"
             onerror="this.src='images/bkgds/bkgd1.jpg'" />
        ${arrows}
      </div>
      <div class="prop-card-body">
        <div class="prop-card-dots">${dots}</div>
        <div class="prop-card-name copperplate">${listing.name}</div>
        <div class="prop-card-desc">${getListingDesc(listing)}</div>
        ${price ? `<div class="prop-card-price">${price}</div>` : ''}
        ${meta  ? `<div class="prop-card-meta">${meta}</div>`   : ''}
        <a href="${listing.bookingUrl}" target="_blank" rel="noopener" class="prop-card-book">
          Book Now &rarr;
        </a>
      </div>
    </div>`;
}

function renderSection(category) {
  const slug  = category.slug;
  const copy  = SECTION_COPY[slug] || { label: 'Accommodations', desc: '' };
  const grid  = GRID_CLASS[slug]   || '';
  const cards = category.listings.map(l => renderCard(l, slug)).join('');

  return `
    <section class="accom-section" id="${slug}">
      <div class="section-header">
        <p class="section-header-label">${copy.label}</p>
        <h2 class="section-header-title copperplate">${category.name}</h2>
        ${copy.desc ? `<p class="section-header-desc">${copy.desc}</p>` : ''}
      </div>
      <div class="prop-grid-wrap">
        <div class="prop-grid ${grid}">
          ${cards}
        </div>
      </div>
    </section>`;
}

function renderCatNav(categories) {
  return categories.map(cat =>
    `<a href="#${cat.slug}">${cat.name}</a>`
  ).join('');
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
  modal.querySelector('.modal-name').textContent  = listing.name;
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

  // Close on overlay click or X
  modal.querySelector('.modal-overlay').addEventListener('click', closeModal);
  modal.querySelector('.modal-close').addEventListener('click', closeModal);

  // Keyboard close + arrow nav
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape')     closeModal();
    if (e.key === 'ArrowLeft')  stepModalPhoto(-1);
    if (e.key === 'ArrowRight') stepModalPhoto(1);
  });

  // Modal carousel arrows
  modal.querySelector('.modal-carousel-prev').addEventListener('click', () => stepModalPhoto(-1));
  modal.querySelector('.modal-carousel-next').addEventListener('click', () => stepModalPhoto(1));

  // Card click → open modal (ignore carousel buttons and book link)
  document.getElementById('listings-sections').addEventListener('click', e => {
    if (e.target.closest('.carousel-btn'))   return;
    if (e.target.closest('.prop-card-book')) return;
    const card = e.target.closest('.prop-card');
    if (!card) return;
    const listing = listingRegistry.get(card.dataset.listingId);
    if (listing) openModal(listing);
  });
}

// ── Load + init ──────────────────────────────────────────────────────────────

async function loadListings() {
  const navEl      = document.getElementById('listings-cat-nav');
  const sectionsEl = document.getElementById('listings-sections');

  if (!navEl || !sectionsEl) return;

  try {
    const res  = await fetch('data/listings.json');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    const categories = data.categories.filter(c => c.slug !== 'other-properties');

    // Register all listings by id
    categories.forEach(cat =>
      cat.listings.forEach(l => listingRegistry.set(l.id, l))
    );

    navEl.innerHTML      = renderCatNav(categories);
    sectionsEl.innerHTML = categories.map(renderSection).join('');

    if (window.location.hash) {
      const target = document.querySelector(window.location.hash);
      if (target) setTimeout(() => target.scrollIntoView({ behavior: 'smooth' }), 50);
    }

  } catch (err) {
    console.error('listings-loader: failed to load listings.json', err);
    sectionsEl.innerHTML = `
      <div style="padding:4rem 2rem; text-align:center; color:#6b452e;">
        <p>Unable to load property listings. Please try again later.</p>
      </div>`;
  }
}

function initCarousels() {
  // Event delegation — one listener on the sections container handles all cards
  const container = document.getElementById('listings-sections');
  if (!container) return;

  container.addEventListener('click', e => {
    const btn = e.target.closest('.carousel-btn');
    if (!btn) return;

    e.preventDefault();
    const carousel = btn.closest('.prop-card-carousel');
    const card     = carousel.closest('.prop-card');
    const photos   = JSON.parse(carousel.dataset.photos);
    let   index    = parseInt(carousel.dataset.index, 10);

    if (btn.classList.contains('carousel-btn--prev')) {
      index = (index - 1 + photos.length) % photos.length;
    } else {
      index = (index + 1) % photos.length;
    }

    // Update image
    const img = carousel.querySelector('.prop-card-img');
    img.src = photos[index];
    carousel.dataset.index = index;

    // Update dots
    const dots = card.querySelectorAll('.prop-dot');
    dots.forEach((d, i) => d.classList.toggle('active', i === index));
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  await loadListings();
  initCarousels();
  initModal();
});
