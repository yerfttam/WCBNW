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

