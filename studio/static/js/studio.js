/**
 * PLB Creator Studio — Desktop Shell Client Script
 * ================================================
 * Handles workspace switching, keyboard shortcuts, health monitoring,
 * and IPC / host bridge actions.
 */

document.addEventListener('DOMContentLoaded', () => {
  const tabUniverse = document.getElementById('tab-btn-universe');
  const tabSeo = document.getElementById('tab-btn-seo');
  const paneUniverse = document.getElementById('pane-universe');
  const paneSeo = document.getElementById('pane-seo');
  const frameUniverse = document.getElementById('frame-universe');
  const frameSeo = document.getElementById('frame-seo');

  const healthUniverse = document.getElementById('health-universe');
  const healthSeo = document.getElementById('health-seo');
  const btnOpenFolder = document.getElementById('btn-open-folder');
  const btnReloadView = document.getElementById('btn-reload-view');
  const btnOpenExternal = document.getElementById('btn-open-external');

  let currentTab = 'universe';

  // 1. Tab Switching Function
  function switchWorkspace(target) {
    if (target === 'universe') {
      tabUniverse.classList.add('active');
      tabSeo.classList.remove('active');
      paneUniverse.classList.add('active');
      paneSeo.classList.remove('active');
      currentTab = 'universe';
    } else if (target === 'seo') {
      tabSeo.classList.add('active');
      tabUniverse.classList.remove('active');
      paneSeo.classList.add('active');
      paneUniverse.classList.remove('active');
      currentTab = 'seo';
    }
  }

  tabUniverse.addEventListener('click', () => switchWorkspace('universe'));
  tabSeo.addEventListener('click', () => switchWorkspace('seo'));

  // 2. Keyboard Shortcuts (Ctrl+1, Ctrl+2, F5)
  window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.altKey) && e.key === '1') {
      e.preventDefault();
      switchWorkspace('universe');
    } else if ((e.ctrlKey || e.altKey) && e.key === '2') {
      e.preventDefault();
      switchWorkspace('seo');
    } else if (e.key === 'F5' || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'r')) {
      e.preventDefault();
      reloadActiveView();
    }
  });

  // 3. Reload Active Workspace View
  function reloadActiveView() {
    if (currentTab === 'universe' && frameUniverse) {
      frameUniverse.src = frameUniverse.src;
    } else if (currentTab === 'seo' && frameSeo) {
      frameSeo.src = frameSeo.src;
    }
  }
  btnReloadView.addEventListener('click', reloadActiveView);

  // 4. Open Local Folder in Windows Explorer
  btnOpenFolder.addEventListener('click', async () => {
    try {
      await fetch('/api/studio/open-folder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder: 'uploads' })
      });
    } catch (err) {
      console.error('Failed to open folder:', err);
    }
  });

  // 5. Open in External Browser Tab
  btnOpenExternal.addEventListener('click', async () => {
    const url = currentTab === 'universe' ? 'http://127.0.0.1:5050' : 'http://127.0.0.1:5000';
    try {
      await fetch('/api/studio/open-browser', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url })
      });
    } catch (e) {
      window.open(url, '_blank');
    }
  });

  // 6. Child IFrame Message Bridge
  window.addEventListener('message', (event) => {
    if (event.data && event.data.action === 'switch-tab') {
      if (event.data.target) {
        switchWorkspace(event.data.target);
      }
    }
  });

  // 7. Health Polling Monitor
  async function checkHealth() {
    try {
      const res = await fetch('/api/studio/status');
      if (res.ok) {
        const data = await res.json();
        updateDot(healthUniverse, data.universe_online);
        updateDot(healthSeo, data.seo_online);
      }
    } catch (err) {
      updateDot(healthUniverse, false);
      updateDot(healthSeo, false);
    }
  }

  function updateDot(element, isOnline) {
    if (!element) return;
    const dot = element.querySelector('.health-dot');
    if (!dot) return;
    if (isOnline) {
      dot.className = 'health-dot dot-active';
      element.title = 'Service Online';
    } else {
      dot.className = 'health-dot dot-error';
      element.title = 'Service Offline / Starting';
    }
  }

  // Poll health immediately, then every 5 seconds
  checkHealth();
  setInterval(checkHealth, 5000);
});
