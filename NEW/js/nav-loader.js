// Loads the shared nav partial into pages and attaches mobile toggle behavior
(async function(){
  try {
    const res = await fetch('partials/nav.html');
    if (!res.ok) return;
    const html = await res.text();
    const placeholder = document.getElementById('site-nav-placeholder');
    if (!placeholder) return;
    placeholder.innerHTML = html;

    const hamburger = placeholder.querySelector('.hamburger');
    const mobileMenu = document.getElementById('mobileMenu');

    function toggleMenu(){
      if (!mobileMenu) return;
      mobileMenu.classList.toggle('open');
    }

    if (hamburger) hamburger.addEventListener('click', toggleMenu);

    // Close mobile menu when a mobile link is clicked
    const mobileLinks = placeholder.querySelectorAll('.mobile-menu a');
    mobileLinks.forEach(a => a.addEventListener('click', ()=>{
      if (mobileMenu) mobileMenu.classList.remove('open');
    }));

    // Mark active link based on current file name
    const current = location.pathname.split('/').pop() || 'index.html';
    placeholder.querySelectorAll('.nav-links a').forEach(a=>{
      const href = a.getAttribute('href') || '';
      if (href.split('#')[0] === current) a.classList.add('active');
    });

  } catch (e) {
    console.error('nav-loader error', e);
  }
})();
