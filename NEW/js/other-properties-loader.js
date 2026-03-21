/**
 * other-properties-loader.js
 *
 * Fetches NEW/data/listings.json and renders the "other-properties"
 * category into the horizontal listing-card layout on other-properties.html.
 */

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
    <div class="listing-card${isReverse ? ' listing-card--reverse' : ''}">
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

    container.innerHTML = category.listings.map(renderCard).join('');

  } catch (err) {
    console.error('other-properties-loader: failed to load listings.json', err);
    container.innerHTML = `
      <div style="padding:4rem 2rem; text-align:center; color:#6b452e;">
        <p>Unable to load property listings. Please try again later.</p>
      </div>`;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadOtherProperties();
  initCarousels();
});
