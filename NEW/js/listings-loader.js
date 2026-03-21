/**
 * listings-loader.js
 *
 * Fetches NEW/data/listings.json and dynamically renders the accommodations
 * page: category nav tabs, section headers, and property cards.
 *
 * Matches the existing CSS classes in accommodations.html — no style changes needed.
 */

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

function slugify(str) {
  return str.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9\-]/g, '');
}

function renderPrice(price) {
  if (!price || !price.base) return '';
  return `From $${price.base}/night`;
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
    <div class="prop-card ${cardMod}">
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
        ${listing.summary ? `<div class="prop-card-desc">${listing.summary}</div>` : ''}
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

async function loadListings() {
  const navEl      = document.getElementById('listings-cat-nav');
  const sectionsEl = document.getElementById('listings-sections');

  if (!navEl || !sectionsEl) return;

  try {
    const res  = await fetch('data/listings.json');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    const categories = data.categories.filter(c => c.slug !== 'other-properties');
    navEl.innerHTML      = renderCatNav(categories);
    sectionsEl.innerHTML = categories.map(renderSection).join('');

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

document.addEventListener('DOMContentLoaded', loadListings);
document.addEventListener('DOMContentLoaded', initCarousels);
