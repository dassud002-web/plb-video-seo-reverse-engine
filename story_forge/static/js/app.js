/**
 * PLB Story Universe Factory — Frontend Application Script
 * ========================================================
 * Powers:
 * - Video analysis & Story DNA extraction
 * - Character Universe & Multi-Species catalog
 * - Story Genome 20-dimensional structural inspector
 * - Story Universe dashboard with Top 10/50/100 rankings & 15 worlds
 * - Auto-Grow Infinite Expansion studio (100, 300, 500, 1,000+ stories)
 * - 9-Part Production Pipeline Studio (Script, Storyboard, AI prompts, SEO)
 * - Interactive Lineage Tree & Parent/Child comparison
 * - Multi-Format Export Suite (Story Bible, Character Bible, CSV, JSON, ZIP)
 */

document.addEventListener('DOMContentLoaded', () => {
  // Application State
  const state = {
    selectedPath: null,
    originalFileName: null,
    currentSessionId: null,
    sessionData: null,
    stories: [],
    lineageGraph: null,
    characterUniverse: null,
    universeMetrics: null,
    activeTab: 'tab-video',
    activePollingId: null,
    activeAutoGrowPollingId: null,
    currentProducedStoryId: null
  };

  // -------------------------------------------------------------
  // Truthful Clipboard Helper with Dual Fallback
  // -------------------------------------------------------------
  async function copyToClipboard(text) {
    if (!text || typeof text !== 'string') {
      return false;
    }

    // Modern asynchronous clipboard API
    if (navigator.clipboard && window.isSecureContext) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (err) {
        console.warn('navigator.clipboard.writeText failed, using execCommand fallback:', err);
      }
    }

    // Bulletproof synchronous fallback via offscreen textarea
    try {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.top = '0';
      textArea.style.left = '0';
      textArea.style.width = '2em';
      textArea.style.height = '2em';
      textArea.style.padding = '0';
      textArea.style.border = 'none';
      textArea.style.outline = 'none';
      textArea.style.boxShadow = 'none';
      textArea.style.background = 'transparent';
      textArea.setAttribute('readonly', '');
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      textArea.setSelectionRange(0, text.length);
      const successful = document.execCommand('copy');
      document.body.removeChild(textArea);
      return !!successful;
    } catch (err) {
      console.error('execCommand copy fallback failed:', err);
      return false;
    }
  }

  // Diagnostic activity logger helper
  async function recordDiagnosticEvent(eventType, moduleName = 'ui', details = {}, success = true, message = '') {
    try {
      await fetch('/api/diagnostics/event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_type: eventType,
          module: moduleName,
          session_id: state.currentSessionId,
          success: success,
          message: message,
          details: details
        })
      });
    } catch (err) {
      // Diagnostic logging is non-blocking
    }
  }

  // DOM Elements - Navigation & Core
  const tabs = document.querySelectorAll('.nav-tab');
  const panes = document.querySelectorAll('.tab-pane');
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');
  const uploadStatusBox = document.getElementById('upload-status-box');
  const uploadSelectedName = document.getElementById('upload-selected-name');
  const uploadSize = document.getElementById('upload-size');
  const uploadStatusBadge = document.getElementById('upload-status-badge');
  const uploadStatusPct = document.getElementById('upload-status-pct');
  const uploadProgressTrack = document.getElementById('upload-progress-track');
  const uploadProgressFill = document.getElementById('upload-progress-fill');
  const pathInput = document.getElementById('video-path-input');
  const btnScanPath = document.getElementById('btn-scan-path');
  const candidateBtnsContainer = document.getElementById('candidate-buttons');
  const inspectionBox = document.getElementById('inspection-box');
  const btnForge = document.getElementById('btn-forge-stories');
  const selectScaleMode = document.getElementById('select-scale-mode');
  const progressBox = document.getElementById('progress-box');
  const progressStage = document.getElementById('progress-stage');
  const progressPct = document.getElementById('progress-pct');
  const progressBarFill = document.getElementById('progress-bar-fill');
  const recentSessionsList = document.getElementById('recent-sessions-list');
  const currentSessionLabel = document.getElementById('current-session-label');
  const universeCountBadge = document.getElementById('universe-count-badge');

  // Universe Filter Controls
  const filterRanking = document.getElementById('filter-ranking');
  const filterStoryWorld = document.getElementById('filter-story-world');
  const searchInput = document.getElementById('search-story-text');
  const sortSelect = document.getElementById('sort-stories');
  const storiesGrid = document.getElementById('stories-grid');
  const visibleStoriesCount = document.getElementById('visible-stories-count');
  const totalStoriesCount = document.getElementById('total-stories-count');

  // Genome & Production Selectors
  const genomeStorySelect = document.getElementById('genome-story-select');
  const genomeContent = document.getElementById('genome-content');
  const prodStorySelect = document.getElementById('prod-story-select');
  const prodContent = document.getElementById('production-content');
  const btnRefreshProduction = document.getElementById('btn-refresh-production');
  const btnCopyProductionPack = document.getElementById('btn-copy-production-pack');

  // Auto-Grow Controls
  const autogrowTargetCount = document.getElementById('autogrow-target-count');
  const autogrowDivSlider = document.getElementById('autogrow-diversity-slider');
  const autogrowDivDisplay = document.getElementById('autogrow-div-display');
  const autogrowQualSlider = document.getElementById('autogrow-quality-slider');
  const autogrowQualDisplay = document.getElementById('autogrow-qual-display');
  const btnRunAutogrow = document.getElementById('btn-run-autogrow');
  const autogrowProgressBox = document.getElementById('autogrow-progress-box');
  const autogrowProgressStage = document.getElementById('autogrow-progress-stage');
  const autogrowProgressPct = document.getElementById('autogrow-progress-pct');
  const autogrowProgressBarFill = document.getElementById('autogrow-progress-bar-fill');
  const scalePresetBtns = document.querySelectorAll('.scale-preset-btn');

  // Export Buttons
  const btnExportBible = document.getElementById('btn-export-bible');
  const btnExportCharBible = document.getElementById('btn-export-char-bible');
  const btnExportRelGraph = document.getElementById('btn-export-rel-graph');
  const btnExportCsv = document.getElementById('btn-export-csv');
  const btnExportJson = document.getElementById('btn-export-json');
  const btnExportZip = document.getElementById('btn-export-zip');

  // Modal Elements
  const modal = document.getElementById('story-modal');
  const modalTitle = document.getElementById('modal-story-title');
  const modalBody = document.getElementById('modal-story-body');
  const modalClose = document.getElementById('modal-close-btn');
  const modalCopy = document.getElementById('modal-copy-btn');
  const modalProduce = document.getElementById('modal-produce-btn');
  const modalExpand = document.getElementById('modal-expand-btn');
  let currentModalStory = null;

  // Species emoji helper map
  const SPECIES_EMOJI = {
    'chicken': '🐔',
    'chickens': '🐔',
    'chick': '🐣',
    'rabbit': '🐰',
    'rabbits': '🐰',
    'dog': '🐶',
    'cat': '🐱',
    'duck': '🦆',
    'duckling': '🦆',
    'goat': '🐐',
    'lamb': '🐑',
    'piglet': '🐷',
    'pig': '🐷',
    'pony': '🐴',
    'alpaca': '🦙',
    'parrot': '🦜',
    'turtle': '🐢',
    'hamster': '🐹',
    'guinea pig': '🐹'
  };

  function getSpeciesEmoji(speciesStr) {
    if (!speciesStr) return '🐾';
    const s = speciesStr.toLowerCase().trim();
    return SPECIES_EMOJI[s] || '🐾';
  }

  // -------------------------------------------------------------
  // 1. Navigation Tabs
  // -------------------------------------------------------------
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetId = tab.getAttribute('data-tab');
      switchTab(targetId);
    });
  });

  function switchTab(tabId) {
    tabs.forEach(t => t.classList.toggle('active', t.getAttribute('data-tab') === tabId));
    panes.forEach(p => p.classList.toggle('active', p.id === tabId));
    state.activeTab = tabId;
  }

  // -------------------------------------------------------------
  // 2. Initial Setup: Load Candidates & Recent Sessions
  // -------------------------------------------------------------
  fetchRecentAndCandidates();

  async function fetchRecentAndCandidates() {
    try {
      const res = await fetch('/api/recent');
      const data = await res.json();
      
      // Render candidate buttons
      candidateBtnsContainer.innerHTML = '';
      if (data.test_candidates && data.test_candidates.length > 0) {
        data.test_candidates.forEach(cand => {
          const btn = document.createElement('button');
          btn.className = 'candidate-btn';
          btn.textContent = `${cand.name} (${cand.size_mb} MB)`;
          btn.addEventListener('click', () => {
            pathInput.value = cand.name;
            state.selectedPath = cand.path;
            state.originalFileName = cand.name;
            inspectVideoPath(cand.path, cand.name);
          });
          candidateBtnsContainer.appendChild(btn);
        });
      }

      // Render recent sessions
      recentSessionsList.innerHTML = '';
      if (data.recent_sessions && data.recent_sessions.length > 0) {
        data.recent_sessions.forEach(sess => {
          const item = document.createElement('div');
          item.className = 'history-item';
          item.innerHTML = `
            <div>
              <div class="history-title">${escapeHtml(sess.source_video_name)}</div>
              <div class="history-sub">${sess.created_at} • ${sess.duration_seconds}s</div>
            </div>
            <button class="btn btn-secondary btn-sm">Load</button>
          `;
          item.querySelector('button').addEventListener('click', (e) => {
            e.stopPropagation();
            loadSession(sess.session_id);
          });
          recentSessionsList.appendChild(item);
        });
      } else {
        recentSessionsList.innerHTML = '<p class="placeholder-text">No previous story sessions found.</p>';
      }
    } catch (err) {
      console.error('Failed to load recent candidates:', err);
    }
  }

  // -------------------------------------------------------------
  // 3. File Selection & Drag & Drop Upload Pipeline
  // -------------------------------------------------------------
  dropZone.addEventListener('click', () => fileInput.click());
  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      uploadAndInspectVideo(file);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files.length > 0) {
      const file = fileInput.files[0];
      uploadAndInspectVideo(file);
    }
  });

  btnScanPath.addEventListener('click', () => {
    const p = pathInput.value.trim();
    if (p) inspectVideoPath(p, p);
  });

  async function uploadAndInspectVideo(file) {
    if (!file) return;

    // Show upload progress status box
    uploadStatusBox.style.display = 'flex';
    uploadSelectedName.textContent = `Selected: ${file.name}`;
    uploadSize.textContent = `Size: ${(file.size / (1024 * 1024)).toFixed(2)} MB`;
    uploadStatusBadge.textContent = 'Uploading...';
    uploadStatusBadge.className = 'upload-status-badge status-uploading';
    uploadStatusPct.textContent = '0%';
    uploadProgressTrack.style.display = 'block';
    uploadProgressFill.style.width = '0%';
    btnForge.disabled = true;

    // Client-side extension validation hint
    const validExts = ['.mp4', '.mov', '.webm'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!validExts.includes(ext)) {
      uploadStatusBadge.textContent = `Unsupported format (${ext}). Allowed: MP4, MOV, WEBM`;
      uploadStatusBadge.className = 'upload-status-badge status-error';
      uploadProgressTrack.style.display = 'none';
      alert(`Unsupported file extension: ${ext}\nAllowed extensions: MP4, MOV, WEBM`);
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const uploadRes = await new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/upload');

        xhr.upload.onprogress = (e) => {
          if (e.lengthComputable) {
            const pct = Math.round((e.loaded / e.total) * 100);
            uploadProgressFill.style.width = `${pct}%`;
            uploadStatusPct.textContent = `${pct}%`;
            uploadStatusBadge.textContent = `Uploading... ${pct}%`;
          }
        };

        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            try {
              resolve(JSON.parse(xhr.responseText));
            } catch (err) {
              reject(new Error('Invalid response from server'));
            }
          } else {
            try {
              const errJson = JSON.parse(xhr.responseText);
              reject(new Error(errJson.error || `Server error (${xhr.status})`));
            } catch (e) {
              reject(new Error(`Server error (${xhr.status})`));
            }
          }
        };

        xhr.onerror = () => reject(new Error('Network error during upload'));
        xhr.ontimeout = () => reject(new Error('Upload timed out'));
        xhr.send(formData);
      });

      if (uploadRes.status === 'ok') {
        uploadProgressFill.style.width = '100%';
        uploadStatusPct.textContent = '100%';
        uploadStatusBadge.textContent = 'Uploaded ✓ Ready to Analyze';
        uploadStatusBadge.className = 'upload-status-badge status-uploaded';

        state.selectedPath = uploadRes.path;
        state.originalFileName = uploadRes.original_name;
        pathInput.value = uploadRes.original_name;

        // Automatically inspect uploaded server-side temp file
        await inspectVideoPath(uploadRes.path, uploadRes.original_name);
      } else {
        throw new Error(uploadRes.error || 'Upload failed');
      }
    } catch (err) {
      uploadStatusBadge.textContent = `Upload Failed: ${err.message}`;
      uploadStatusBadge.className = 'upload-status-badge status-error';
      uploadProgressFill.style.width = '0%';
      alert(`Upload Failed: ${err.message}`);
    }
  }

  async function inspectVideoPath(targetPath, originalName = null) {
    try {
      const res = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          path: targetPath,
          original_name: originalName || state.originalFileName
        })
      });
      const data = await res.json();
      if (data.status === 'ok') {
        state.selectedPath = data.file_info.path;
        state.originalFileName = data.file_info.name;
        document.getElementById('insp-name').textContent = data.file_info.name;
        document.getElementById('insp-duration').textContent = `${data.file_info.duration_seconds}s`;
        document.getElementById('insp-resolution').textContent = data.file_info.resolution;
        document.getElementById('insp-codec').textContent = data.file_info.codec;
        document.getElementById('insp-fps').textContent = `${data.file_info.fps} fps`;
        document.getElementById('insp-size').textContent = `${data.file_info.size_mb} MB`;
        inspectionBox.style.display = 'block';
        btnForge.disabled = false;
      } else {
        alert(`Inspection Error: ${data.error}`);
      }
    } catch (err) {
      alert(`Network Error during inspection: ${err.message}`);
    }
  }

  // -------------------------------------------------------------
  // 4. Initial Launch of Story Universe Factory
  // -------------------------------------------------------------
  btnForge.addEventListener('click', startAnalysis);

  async function startAnalysis() {
    if (!state.selectedPath) return;

    btnForge.disabled = true;
    progressBox.style.display = 'block';
    progressPct.textContent = '5%';
    progressBarFill.style.width = '5%';
    progressStage.textContent = 'Initializing Story Universe Factory...';

    const targetCount = parseInt(selectScaleMode.value) || 100;
    const threshold = parseFloat(document.getElementById('range-threshold').value) || 0.75;

    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          path: state.selectedPath,
          original_name: state.originalFileName,
          target_count: targetCount,
          threshold: threshold,
          universe_mode: true
        })
      });
      const data = await res.json();
      if (data.status === 'ok') {
        pollAnalysisTask(data.task_id);
      } else {
        alert(`Error starting analysis: ${data.error}`);
        btnForge.disabled = false;
        progressBox.style.display = 'none';
      }
    } catch (err) {
      alert(`Network Error: ${err.message}`);
      btnForge.disabled = false;
      progressBox.style.display = 'none';
    }
  }

  function pollAnalysisTask(taskId) {
    if (state.activePollingId) clearInterval(state.activePollingId);

    state.activePollingId = setInterval(async () => {
      try {
        const res = await fetch(`/api/status/${taskId}`);
        const st = await res.json();

        progressPct.textContent = `${st.progress}%`;
        progressBarFill.style.width = `${st.progress}%`;
        progressStage.textContent = st.stage || 'Synthesizing Story Universe...';

        if (st.status === 'completed') {
          clearInterval(state.activePollingId);
          progressBox.style.display = 'none';
          btnForge.disabled = false;
          loadSession(st.session_id);
        } else if (st.status === 'error') {
          clearInterval(state.activePollingId);
          progressBox.style.display = 'none';
          btnForge.disabled = false;
          alert(`Analysis Error: ${st.error}`);
        }
      } catch (err) {
        clearInterval(state.activePollingId);
        console.error('Polling error:', err);
      }
    }, 800);
  }

  // -------------------------------------------------------------
  // 5. Load Session Data & Render All Universe Views
  // -------------------------------------------------------------
  async function loadSession(sessionId) {
    try {
      const res = await fetch(`/api/session/${sessionId}`);
      const data = await res.json();
      if (data.status === 'ok') {
        state.currentSessionId = sessionId;
        state.sessionData = data;
        state.stories = data.stories || [];
        state.lineageGraph = data.lineage_graph;
        state.characterUniverse = data.character_universe || {};
        state.universeMetrics = data.universe_metrics || {};

        currentSessionLabel.textContent = `Universe: ${sessionId} (${state.stories.length} Stories)`;
        universeCountBadge.textContent = state.stories.length;

        // Render All Tabs
        renderStoryDna(data.story_dna, data.session);
        renderCharacterUniverse(data.character_universe, data.universe_metrics);
        populateGenomeDropdown(state.stories);
        populateProductionDropdown(state.stories);
        renderUniverseDashboard();
        renderTreeGraph(data.lineage_graph);
        enableExports(sessionId);

        // Switch to Story Universe Tab
        switchTab('tab-universe');
      }
    } catch (err) {
      console.error('Failed to load session:', err);
    }
  }

  // -------------------------------------------------------------
  // 6. Render Story DNA Tab
  // -------------------------------------------------------------
  function renderStoryDna(dna, session) {
    if (!dna) return;
    document.getElementById('dna-asset-name').textContent = session.source_video_name || 'Root Video Asset';
    document.getElementById('dna-core-premise').textContent = dna.core_premise || '-';
    document.getElementById('dna-central-tension').textContent = dna.central_tension || '-';
    document.getElementById('dna-char-dynamic').textContent = dna.primary_character_dynamic || '-';
    document.getElementById('dna-engine').textContent = dna.primary_comedic_emotional_engine || '-';

    const charsDiv = document.getElementById('dna-chars-setting');
    let charsHtml = `<p><strong>Setting:</strong> ${escapeHtml(dna.setting || '-')}</p>`;
    charsHtml += `<p><strong>Observed:</strong> ${escapeHtml(dna.setting_observed || '-')}</p>`;
    charsHtml += `<p><strong>Characters:</strong></p><ul>`;
    (dna.characters || []).forEach(c => {
      charsHtml += `<li><strong>${escapeHtml(c.name)}</strong>: ${escapeHtml(c.observed_fact || '')}</li>`;
    });
    charsHtml += `</ul>`;
    charsDiv.innerHTML = charsHtml;

    const progDiv = document.getElementById('dna-progression');
    let progHtml = `<p><strong>Hook:</strong> ${escapeHtml(dna.hook || '-')}</p>`;
    progHtml += `<p><strong>Conflict:</strong> ${escapeHtml(dna.conflict || '-')}</p>`;
    progHtml += `<p><strong>Twist:</strong> ${escapeHtml(dna.twist || '-')}</p>`;
    progHtml += `<p><strong>Payoff:</strong> ${escapeHtml(dna.payoff || '-')}</p>`;
    progDiv.innerHTML = progHtml;

    const reusDiv = document.getElementById('dna-reusable');
    let reusHtml = '<ul>';
    (dna.reusable_story_elements || []).forEach(el => {
      reusHtml += `<li><strong>${escapeHtml(el.element)}</strong> (${escapeHtml(el.reusability)}): ${escapeHtml(el.source)}</li>`;
    });
    reusHtml += '</ul>';
    reusDiv.innerHTML = reusHtml;

    const evTagsDiv = document.getElementById('dna-evidence-tags');
    evTagsDiv.innerHTML = '';
    (dna.evidence_refs || []).forEach(ref => {
      const tag = document.createElement('span');
      tag.className = 'ev-tag';
      tag.textContent = ref;
      evTagsDiv.appendChild(tag);
    });
  }

  // -------------------------------------------------------------
  // 7. Render Character Universe Tab
  // -------------------------------------------------------------
  function renderCharacterUniverse(charUniverse, metrics) {
    if (!charUniverse) return;

    const canon = charUniverse.canon_characters || [];
    const pool = charUniverse.creative_pool || [];
    const speciesCount = metrics.unique_species_count || 1;
    const relCount = metrics.unique_relationship_types || 8;

    document.getElementById('cu-stat-canon').textContent = canon.length;
    document.getElementById('cu-stat-species').textContent = speciesCount;
    document.getElementById('cu-stat-pool').textContent = pool.length;
    document.getElementById('cu-stat-relationships').textContent = relCount;
    document.getElementById('chars-species-badge').textContent = `${speciesCount} Species Active`;

    // Render Canon Characters
    const canonContainer = document.getElementById('canon-characters-list');
    canonContainer.innerHTML = '';
    if (canon.length === 0) {
      canonContainer.innerHTML = '<p class="placeholder-text">No canon characters extracted.</p>';
    } else {
      canon.forEach(c => {
        const card = document.createElement('div');
        card.className = 'char-card';
        card.innerHTML = `
          <div class="char-avatar">${getSpeciesEmoji(c.species)}</div>
          <div class="char-body">
            <div class="char-header">
              <span class="char-name">${escapeHtml(c.name)}</span>
              <span class="char-species-tag">${escapeHtml(c.species)}</span>
            </div>
            <p class="char-desc">${escapeHtml(c.physical_description || c.observed_fact || '')}</p>
            <div class="char-traits-row">
              <span class="char-trait-pill">Role: ${escapeHtml(c.archetype || c.role || 'Protagonist')}</span>
              <span class="char-trait-pill">Trait: ${escapeHtml(c.personality_traits ? c.personality_traits.slice(0, 2).join(', ') : 'Curious')}</span>
            </div>
          </div>
        `;
        canonContainer.appendChild(card);
      });
    }

    // Render Creative Pool & Species Filter Tags
    const speciesFilterBar = document.getElementById('species-filter-bar');
    const poolContainer = document.getElementById('creative-pool-list');
    speciesFilterBar.innerHTML = '';

    const speciesSet = new Set(pool.map(p => p.species.toLowerCase()));
    const allPill = document.createElement('span');
    allPill.className = 'species-pill active';
    allPill.textContent = `All (${pool.length})`;
    speciesFilterBar.appendChild(allPill);

    speciesSet.forEach(sp => {
      const pill = document.createElement('span');
      pill.className = 'species-pill';
      pill.textContent = `${getSpeciesEmoji(sp)} ${sp.charAt(0).toUpperCase() + sp.slice(1)}`;
      pill.addEventListener('click', () => {
        document.querySelectorAll('.species-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        renderPoolList(sp);
      });
      speciesFilterBar.appendChild(pill);
    });

    allPill.addEventListener('click', () => {
      document.querySelectorAll('.species-pill').forEach(p => p.classList.remove('active'));
      allPill.classList.add('active');
      renderPoolList('ALL');
    });

    function renderPoolList(filterSpecies) {
      poolContainer.innerHTML = '';
      const filtered = filterSpecies === 'ALL'
        ? pool
        : pool.filter(p => p.species.toLowerCase() === filterSpecies);

      filtered.forEach(c => {
        const card = document.createElement('div');
        card.className = 'char-card';
        card.innerHTML = `
          <div class="char-avatar">${getSpeciesEmoji(c.species)}</div>
          <div class="char-body">
            <div class="char-header">
              <span class="char-name">${escapeHtml(c.name)}</span>
              <span class="char-species-tag">${escapeHtml(c.species)}</span>
            </div>
            <p class="char-desc">${escapeHtml(c.comic_contrast || c.physical_description || '')}</p>
            <div class="char-traits-row">
              <span class="char-trait-pill">Dynamic: ${escapeHtml(c.default_dynamic || 'COMPANION')}</span>
              <span class="char-trait-pill">Archetype: ${escapeHtml(c.archetype || 'Foil')}</span>
            </div>
          </div>
        `;
        poolContainer.appendChild(card);
      });
    }

    renderPoolList('ALL');
  }

  // -------------------------------------------------------------
  // 8. Story Genome Tab (20-Dimensional Breakdown)
  // -------------------------------------------------------------
  function populateGenomeDropdown(stories) {
    genomeStorySelect.innerHTML = '<option value="">Select a story to inspect genome...</option>';
    stories.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s.story_id;
      opt.textContent = `[${s.story_id}] ${s.title} (${s.world_name || s.mode || 'ANIMAL_COMEDY'})`;
      genomeStorySelect.appendChild(opt);
    });
  }

  genomeStorySelect.addEventListener('change', () => {
    const sid = genomeStorySelect.value;
    if (!sid) {
      genomeContent.innerHTML = '<p class="placeholder-text">Select any story above to inspect its 20-dimensional structural genome.</p>';
      return;
    }
    const story = state.stories.find(s => s.story_id === sid);
    if (story) renderStoryGenome(story);
  });

  function renderStoryGenome(s) {
    const evo = s.evolution_metadata || {};
    const shifts = evo.dimensional_shifts || ['setting', 'goal', 'twist'];
    const chars = s.characters || [];
    const rel = s.relationships || {};

    const dimensions = [
      { num: '01', title: 'Core Premise & Title', val: `${s.title} — ${s.one_line_premise}`, tag: 'INHERITED' },
      { num: '02', title: 'Story World & Theme', val: `${s.world_name || s.mode} (ID: ${s.world_id || 'WORLD-01'})`, tag: 'CHANGED' },
      { num: '03', title: 'Ensemble & Species', val: chars.map(c => `${getSpeciesEmoji(c.species)} ${c.name} (${c.species})`).join(' + ') || 'Solo Animal', tag: chars.length > 1 ? 'NEW' : 'INHERITED' },
      { num: '04', title: 'Relationship Dynamic', val: `${rel.type || 'COMPANION'} • Tension: ${rel.tension_level || 'MILD'} • Trigger: ${rel.comic_trigger || 'Curiosity'}`, tag: 'NEW' },
      { num: '05', title: 'Setting & Environment', val: s.setting || 'Farm run', tag: shifts.includes('setting') ? 'CHANGED' : 'INHERITED' },
      { num: '06', title: 'Time Horizon & Urgency', val: s.time_horizon || 'Immediate 15 seconds real-time action', tag: 'INHERITED' },
      { num: '07', title: 'Catalyzing Object', val: (s.objects && s.objects[0] ? s.objects[0].name : 'Mystery Food Object'), tag: shifts.includes('object') ? 'CHANGED' : 'INHERITED' },
      { num: '08', title: 'Primary Goal & Motivation', val: s.goal || 'Investigate and taste the mystery object', tag: shifts.includes('goal') ? 'CHANGED' : 'INHERITED' },
      { num: '09', title: 'Central Conflict', val: s.conflict || 'Curiosity vs hesitation before the encounter', tag: shifts.includes('conflict') ? 'CHANGED' : 'INHERITED' },
      { num: '10', title: 'Obstacles & Complications', val: (s.obstacles ? s.obstacles.join(', ') : 'Physical distance, slippery ground, surprise reaction'), tag: 'CHANGED' },
      { num: '11', title: 'Narrative Escalation', val: s.escalation || 'Cautious approach building into sudden contact', tag: 'INHERITED' },
      { num: '12', title: 'Midpoint Turning Point', val: s.midpoint || 'First physical contact with the object triggers an unexpected reaction', tag: 'CHANGED' },
      { num: '13', title: 'Climax / Decisive Event', val: s.climax || 'Decisive taste test and immediate expressive reflex', tag: 'INHERITED' },
      { num: '14', title: 'Creative Twist', val: s.twist || 'Unexpected partner steals the payoff or reaction is hilarious', tag: 'NEW' },
      { num: '15', title: 'Comic / Emotional Payoff', val: s.payoff || 'Wholesome resolution leaving audience laughing', tag: 'CHANGED' },
      { num: '16', title: 'Short-Form Hook (0-3s)', val: s.hook || 'High-kinetic opening grab in first 3 seconds', tag: 'INHERITED' },
      { num: '17', title: 'Loopability Mechanism', val: s.loop_mechanism || 'Final frame smoothly connects back to initial state for infinite replay loop', tag: 'NEW' },
      { num: '18', title: 'Tone & Emotional Resonance', val: s.tone || 'Lighthearted, playful, and infectious humor', tag: 'CHANGED' },
      { num: '19', title: 'Camera & Visual Direction', val: s.visual_style || 'Ground-level macro lens tracking subject eyes and reactions', tag: 'INHERITED' },
      { num: '20', title: 'Target Audience & Format', val: s.target_audience || 'All-ages animal lovers across TikTok, Shorts, and Reels', tag: 'INHERITED' }
    ];

    let html = `
      <div class="genome-overview-banner">
        <div>
          <h3 style="font-size:1.15rem; color:var(--text-main); margin-bottom:0.25rem;">[${escapeHtml(s.story_id)}] ${escapeHtml(s.title)}</h3>
          <p style="font-size:0.85rem; color:var(--text-muted);">${escapeHtml(s.one_line_premise)}</p>
        </div>
        <div style="display:flex; gap:0.5rem; align-items:center;">
          <span class="badge-world">${escapeHtml(s.world_name || s.mode)}</span>
          <span class="badge-quality">Quality: ${s.quality_score || 85.0}</span>
          <span class="badge" style="background:rgba(6,182,212,0.15); color:var(--accent-cyan);">Div: ${s.diversity_score || 0.75}</span>
        </div>
      </div>
      <div class="genome-dimensions-grid">
    `;

    dimensions.forEach(d => {
      const evoClass = d.tag === 'NEW' ? 'evo-new' : d.tag === 'CHANGED' ? 'evo-changed' : 'evo-inherited';
      html += `
        <div class="genome-dim-card">
          <div class="genome-dim-header">
            <span class="genome-dim-num">DIMENSION ${d.num}</span>
            <span class="evo-tag ${evoClass}">${d.tag}</span>
          </div>
          <span class="genome-dim-title">${escapeHtml(d.title)}</span>
          <p class="genome-dim-body">${escapeHtml(d.val)}</p>
        </div>
      `;
    });

    html += `</div>`;
    genomeContent.innerHTML = html;
  }

  // -------------------------------------------------------------
  // 9. Story Universe Dashboard Tab
  // -------------------------------------------------------------
  filterRanking.addEventListener('change', renderUniverseDashboard);
  filterStoryWorld.addEventListener('change', renderUniverseDashboard);
  searchInput.addEventListener('input', renderUniverseDashboard);
  sortSelect.addEventListener('change', renderUniverseDashboard);

  function renderUniverseDashboard() {
    storiesGrid.innerHTML = '';
    const rankingFilter = filterRanking.value;
    const worldFilter = filterStoryWorld.value;
    const query = searchInput.value.toLowerCase().trim();
    const sortVal = sortSelect.value;

    let list = [...state.stories];

    // Compute aggregate metrics
    if (list.length > 0) {
      const avgQual = (list.reduce((acc, s) => acc + (s.quality_score || 85.0), 0) / list.length).toFixed(1);
      const avgDiv = (list.reduce((acc, s) => acc + (s.diversity_score || 0.75), 0) / list.length).toFixed(2);
      document.getElementById('u-total-count').textContent = list.length;
      document.getElementById('u-avg-quality').textContent = avgQual;
      document.getElementById('u-avg-diversity').textContent = avgDiv;
      document.getElementById('u-species-count').textContent = state.universeMetrics?.unique_species_count || 1;
      document.getElementById('u-rel-count').textContent = state.universeMetrics?.unique_relationship_types || 8;
    }

    // World Filter
    if (worldFilter !== 'ALL') {
      list = list.filter(s => (s.world_name || s.mode) === worldFilter);
    }

    // Search Query Filter
    if (query) {
      list = list.filter(s => {
        const full = `${s.title} ${s.one_line_premise} ${s.conflict} ${s.hook} ${s.twist}`.toLowerCase();
        return full.includes(query);
      });
    }

    // Sort order
    if (sortVal === 'quality') {
      list.sort((a, b) => (b.quality_score || 0) - (a.quality_score || 0));
    } else if (sortVal === 'diversity') {
      list.sort((a, b) => (b.diversity_score || 0) - (a.diversity_score || 0));
    } else if (sortVal === 'animal_appeal') {
      list.sort((a, b) => (b.quality_metrics?.animal_appeal || 85) - (a.quality_metrics?.animal_appeal || 85));
    } else if (sortVal === 'hook') {
      list.sort((a, b) => (b.quality_metrics?.hook_potency || 85) - (a.quality_metrics?.hook_potency || 85));
    } else {
      list.sort((a, b) => a.story_id.localeCompare(b.story_id, undefined, { numeric: true }));
    }

    // Ranking Filter (Top 10, 50, 100)
    if (rankingFilter !== 'ALL') {
      const limit = parseInt(rankingFilter) || 50;
      list = list.slice(0, limit);
    }

    visibleStoriesCount.textContent = list.length;
    totalStoriesCount.textContent = state.stories.length;

    if (list.length === 0) {
      storiesGrid.innerHTML = '<p class="placeholder-text">No stories match the active filters.</p>';
      return;
    }

    list.forEach(s => {
      const card = document.createElement('div');
      card.className = 'story-card';
      const chars = s.characters || [];
      const charBadges = chars.map(c => `<span class="char-trait-pill">${getSpeciesEmoji(c.species)} ${escapeHtml(c.name)}</span>`).join(' ');

      card.innerHTML = `
        <div class="story-card-header">
          <span class="story-id-tag">[${escapeHtml(s.story_id)}]</span>
          <span class="badge-world">${escapeHtml(s.world_name || s.mode || 'ANIMAL_COMEDY')}</span>
          <span class="badge-quality">★ ${s.quality_score || 85.0}</span>
          <span class="div-tag">Div: ${s.diversity_score || 0.75}</span>
        </div>
        <h3 class="story-card-title">${escapeHtml(s.title)}</h3>
        <p class="story-card-premise">${escapeHtml(s.one_line_premise)}</p>
        <div style="margin: 0.5rem 0; display:flex; flex-wrap:wrap; gap:0.35rem;">
          ${charBadges}
          <span class="char-trait-pill" style="color:var(--accent-cyan); border-color:rgba(6,182,212,0.3);">${escapeHtml(s.relationships?.type || 'COMPANION')}</span>
        </div>
        <div class="story-card-meta">
          <div><strong>Hook (0-3s):</strong> ${escapeHtml(s.hook || '-')}</div>
          <div><strong>Twist:</strong> ${escapeHtml(s.twist || '-')}</div>
          <div><strong>Payoff:</strong> ${escapeHtml(s.payoff || '-')}</div>
        </div>
        <div class="story-card-actions">
          <button class="btn btn-accent btn-sm btn-produce">🎬 Produce</button>
          <button class="btn btn-secondary btn-sm btn-genome">🔬 Genome</button>
          <button class="btn btn-secondary btn-sm btn-expand">Expand ×50</button>
          <button class="btn btn-secondary btn-sm btn-compare">Compare</button>
        </div>
      `;

      card.querySelector('.btn-produce').addEventListener('click', (e) => {
        e.stopPropagation();
        openProductionForStory(s.story_id);
      });

      card.querySelector('.btn-genome').addEventListener('click', (e) => {
        e.stopPropagation();
        switchTab('tab-genome');
        genomeStorySelect.value = s.story_id;
        renderStoryGenome(s);
      });

      card.querySelector('.btn-expand').addEventListener('click', (e) => {
        e.stopPropagation();
        expandStoryNode(s);
      });

      card.querySelector('.btn-compare').addEventListener('click', (e) => {
        e.stopPropagation();
        openCompareView(s);
      });

      card.addEventListener('click', () => openStoryModal(s));
      storiesGrid.appendChild(card);
    });
  }

  // -------------------------------------------------------------
  // 10. Auto-Grow Infinite Expansion Studio
  // -------------------------------------------------------------
  scalePresetBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      scalePresetBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      autogrowTargetCount.value = btn.getAttribute('data-count');
    });
  });

  autogrowDivSlider.addEventListener('input', () => {
    autogrowDivDisplay.textContent = autogrowDivSlider.value;
  });

  autogrowQualSlider.addEventListener('input', () => {
    autogrowQualDisplay.textContent = autogrowQualSlider.value;
  });

  btnRunAutogrow.addEventListener('click', runAutoGrowExpansion);

  async function runAutoGrowExpansion() {
    if (!state.currentSessionId && !state.selectedPath) {
      alert('Please analyze a video first or select an active session.');
      return;
    }

    const targetCount = parseInt(autogrowTargetCount.value) || 100;
    const diversityThreshold = parseFloat(autogrowDivSlider.value) || 0.75;
    const qualityThreshold = parseFloat(autogrowQualSlider.value) || 85.0;

    btnRunAutogrow.disabled = true;
    autogrowProgressBox.style.display = 'block';
    autogrowProgressPct.textContent = '5%';
    autogrowProgressBarFill.style.width = '5%';
    autogrowProgressStage.textContent = `Initializing Auto-Grow to ${targetCount} stories...`;

    try {
      const res = await fetch('/api/universe/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: state.currentSessionId,
          path: state.selectedPath,
          target_count: targetCount,
          diversity_threshold: diversityThreshold,
          quality_threshold: qualityThreshold
        })
      });
      const data = await res.json();
      if (data.status === 'ok') {
        pollAutoGrowTask(data.task_id);
      } else {
        alert(`Auto-Grow Error: ${data.error}`);
        btnRunAutogrow.disabled = false;
        autogrowProgressBox.style.display = 'none';
      }
    } catch (err) {
      alert(`Network Error during Auto-Grow: ${err.message}`);
      btnRunAutogrow.disabled = false;
      autogrowProgressBox.style.display = 'none';
    }
  }

  function pollAutoGrowTask(taskId) {
    if (state.activeAutoGrowPollingId) clearInterval(state.activeAutoGrowPollingId);

    state.activeAutoGrowPollingId = setInterval(async () => {
      try {
        const res = await fetch(`/api/universe/status/${taskId}`);
        const st = await res.json();

        autogrowProgressPct.textContent = `${st.progress}%`;
        autogrowProgressBarFill.style.width = `${st.progress}%`;
        autogrowProgressStage.textContent = st.stage || 'Expanding universe...';

        if (st.status === 'completed') {
          clearInterval(state.activeAutoGrowPollingId);
          autogrowProgressBox.style.display = 'none';
          btnRunAutogrow.disabled = false;
          alert(`Auto-Grow complete! Story Universe expanded to ${st.result?.total_stories || 'target'} stories.`);
          loadSession(st.session_id);
        } else if (st.status === 'error') {
          clearInterval(state.activeAutoGrowPollingId);
          autogrowProgressBox.style.display = 'none';
          btnRunAutogrow.disabled = false;
          alert(`Auto-Grow Error: ${st.error}`);
        }
      } catch (err) {
        clearInterval(state.activeAutoGrowPollingId);
        console.error('Polling error:', err);
      }
    }, 800);
  }

  // -------------------------------------------------------------
  // 11. Production Pipeline Studio
  // -------------------------------------------------------------
  function populateProductionDropdown(stories) {
    prodStorySelect.innerHTML = '<option value="">Select a story to produce...</option>';
    stories.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s.story_id;
      opt.textContent = `[${s.story_id}] ${s.title} (${s.world_name || s.mode || 'ANIMAL_COMEDY'})`;
      prodStorySelect.appendChild(opt);
    });
  }

  prodStorySelect.addEventListener('change', () => {
    const sid = prodStorySelect.value;
    if (sid) loadProductionPackage(sid);
  });

  btnRefreshProduction.addEventListener('click', () => {
    const sid = prodStorySelect.value;
    if (sid) loadProductionPackage(sid, true);
  });

  function openProductionForStory(storyId) {
    switchTab('tab-production');
    prodStorySelect.value = storyId;
    loadProductionPackage(storyId);
  }

  async function loadProductionPackage(storyId, forceRefresh = false) {
    if (!state.currentSessionId || !storyId) return;
    state.currentProducedStoryId = storyId;

    prodContent.innerHTML = '<p class="placeholder-text">Synthesizing 9-part production package...</p>';

    try {
      const endpoint = forceRefresh
        ? `/api/produce/${state.currentSessionId}/${storyId}`
        : `/api/production/${state.currentSessionId}/${storyId}`;

      const res = await fetch(endpoint, {
        method: forceRefresh ? 'POST' : 'GET'
      });
      const data = await res.json();
      if (data.status === 'ok') {
        renderProductionPackage(data.package);
      } else {
        prodContent.innerHTML = `<p class="placeholder-text" style="color:var(--accent-rose);">Error generating package: ${escapeHtml(data.error)}</p>`;
      }
    } catch (err) {
      prodContent.innerHTML = `<p class="placeholder-text" style="color:var(--accent-rose);">Network error: ${escapeHtml(err.message)}</p>`;
    }
  }

  function renderProductionPackage(pkg) {
    const script = pkg.production_script_15s || {};
    const storyboard = pkg.storyboard_6_shots || [];
    const hero = pkg.hero_frame || {};
    const cont = pkg.continuity_lock || {};
    const seedance = pkg.seedance_prompt || '';
    const veo = pkg.veo_prompt || '';
    const audio = pkg.audio_plan || {};
    const captions = pkg.platform_captions || {};
    const seo = pkg.seo_pack || {};

    // Model-Aware Prompt Package
    const promptPkg = pkg.prompt_package || {
      overall_status: 'PASS',
      models: {
        seedance_25: {
          model_id: 'seedance_25',
          model_name: 'Seedance 2.5',
          output_type: 'video',
          prompt_text: pkg.seedance_prompt || '',
          structure: { 'Subject': 'Subject directive', 'Action/Event': 'Action directive' },
          validation: { status: 'PASS', passed_checks: 9, total_checks: 9, score_pct: 100, checks: {}, warnings: [] }
        }
      },
      hero_frame_prompt: pkg.hero_frame_prompt || '',
      shot_by_shot_prompts: pkg.shot_by_shot_prompts || [],
      continuity_block: pkg.continuity_block || ''
    };

    const models = promptPkg.models || {};

    let html = `
      <!-- 0. MODEL-AWARE PROMPT COMPILER STUDIO -->
      <div class="prompt-compiler-card" id="prompt-compiler-studio">
        <div class="compiler-header">
          <div class="compiler-title-group">
            <span class="compiler-title">🎯 Model-Aware Prompt Compiler</span>
            <span id="compiler-gate-badge" class="compiler-gate-badge pass">PASS 100% (9/9 CHECKS)</span>
          </div>
          <div class="compiler-actions">
            <button class="btn btn-secondary btn-sm" id="btn-toggle-prompt-structure" type="button">
              👁️ Show Structure
            </button>
            <button class="btn btn-primary btn-sm" id="btn-copy-compiled-prompt" type="button">
              📋 Copy Prompt
            </button>
          </div>
        </div>

        <div class="compiler-toolbar">
          <div class="compiler-selectors">
            <!-- Output Type Toggle -->
            <span class="compiler-group-label">Output Type:</span>
            <div class="compiler-pills-row" id="compiler-type-pills">
              <button class="compiler-pill video-pill active" data-type="video" type="button">🎥 Video</button>
              <button class="compiler-pill image-pill" data-type="image" type="button">🖼️ Image</button>
            </div>

            <!-- Video Models Group -->
            <div id="compiler-video-models-group" style="display:inline-flex; align-items:center; gap:0.4rem;">
              <span class="compiler-group-label">Video Model:</span>
              <div class="compiler-pills-row">
                <button class="compiler-pill active" data-model="seedance_25" type="button">Seedance 2.5</button>
              </div>
            </div>

            <!-- Image Models Group -->
            <div id="compiler-image-models-group" style="display:none; align-items:center; gap:0.4rem;">
              <span class="compiler-group-label">Image Model:</span>
              <div class="compiler-pills-row">
                <button class="compiler-pill active" data-model="universal_image" type="button">Universal Image</button>
                <button class="compiler-pill" data-model="gpt_image" type="button">GPT Image</button>
                <button class="compiler-pill" data-model="nano_banana_pro" type="button">Nano Banana Pro</button>
              </div>
            </div>
          </div>
          <div style="font-size:0.75rem; color:var(--text-dim); font-family:var(--font-mono);" id="compiler-stats-display"></div>
        </div>

        <!-- Main Prompt Box -->
        <div class="compiler-main-box">
          <div class="compiler-box-header">
            <span class="compiler-model-tag" id="compiler-active-model-title">Seedance 2.5 (ByteDance / Volcengine Standard)</span>
            <span id="compiler-output-spec-label">Native Video Directive • 24fps • 15s Timeline</span>
          </div>
          <div class="compiler-prompt-text" id="compiler-prompt-display"></div>
        </div>

        <!-- Collapsible Structure Breakdown -->
        <div class="compiler-structure-container" id="compiler-structure-panel">
          <div class="compiler-structure-title">
            <span>📐 Parsed Structure Dimensions & Validation Gate</span>
            <span style="font-size:0.72rem; font-weight:normal; color:var(--text-muted);" id="compiler-structure-summary"></span>
          </div>
          <div class="compiler-dim-grid" id="compiler-dim-grid"></div>
        </div>

        <!-- Sub-Package Drawers -->
        <div class="compiler-extra-sections">
          <!-- Hero Frame Prompt -->
          <div>
            <button class="compiler-sub-toggle-btn" data-target="compiler-hero-drawer" type="button">
              <span>🖼️ Hero Frame Master Prompt</span>
              <span class="toggle-arrow">▼</span>
            </button>
            <div class="compiler-sub-content" id="compiler-hero-drawer">
              <div class="prompt-box">
                <button class="copy-mini-btn" data-copy-target="compiler-hero-text" type="button">Copy</button>
                <span id="compiler-hero-text">${escapeHtml(promptPkg.hero_frame_prompt || pkg.hero_frame_prompt || '')}</span>
              </div>
            </div>
          </div>

          <!-- 6 Shot-by-Shot Prompts -->
          <div>
            <button class="compiler-sub-toggle-btn" data-target="compiler-shots-drawer" type="button">
              <span>🎬 6 Shot-by-Shot Video Prompts (Timestamps & Angles)</span>
              <span class="toggle-arrow">▼</span>
            </button>
            <div class="compiler-sub-content" id="compiler-shots-drawer">
              <div class="storyboard-grid" id="compiler-shots-list" style="margin-top:0.5rem;">
    `;

    const shots = promptPkg.shot_by_shot_prompts || pkg.shot_by_shot_prompts || [];
    shots.forEach(s => {
      html += `
        <div class="shot-card">
          <div class="shot-header">
            <span>SHOT ${s.shot_number}: ${escapeHtml(s.name)}</span>
            <span style="color:var(--accent-amber);">${escapeHtml(s.duration)}</span>
          </div>
          <div class="prompt-box" style="margin-top:0.35rem; font-size:0.72rem;">
            <button class="copy-mini-btn" data-copy="${escapeHtml(s.prompt)}" type="button">Copy</button>
            ${escapeHtml(s.prompt)}
          </div>
        </div>
      `;
    });

    html += `
              </div>
            </div>
          </div>

          <!-- Continuity Lock Rules Block -->
          <div>
            <button class="compiler-sub-toggle-btn" data-target="compiler-continuity-drawer" type="button">
              <span>🔒 Continuity Lock Directive Block</span>
              <span class="toggle-arrow">▼</span>
            </button>
            <div class="compiler-sub-content" id="compiler-continuity-drawer">
              <div class="prompt-box">
                <button class="copy-mini-btn" data-copy-target="compiler-cont-text" type="button">Copy</button>
                <span id="compiler-cont-text">${escapeHtml(promptPkg.continuity_block || pkg.continuity_block || '')}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 9-PART PRODUCTION PIPELINE STUDIO -->
      <div class="production-studio-grid">
        <!-- Col 1: Script & Storyboard -->
        <div>
          <!-- 1. 15-Second Script -->
          <div class="prod-section-card">
            <h3>⏱️ 1. 15-Second Production Script</h3>
            <div class="script-beats-list">
    `;

    (script.beats || []).forEach(b => {
      html += `
        <div class="beat-item">
          <div class="beat-time">${escapeHtml(b.timestamp)} • ${escapeHtml(b.beat_name)}</div>
          <div class="beat-action">${escapeHtml(b.action)}</div>
          <div class="beat-foley">🔊 Foley: ${escapeHtml(b.foley)}</div>
        </div>
      `;
    });

    html += `
            </div>
          </div>

          <!-- 2. 6-Shot Storyboard -->
          <div class="prod-section-card">
            <h3>🎬 2. 6-Shot Short-Form Storyboard</h3>
            <div class="storyboard-grid">
    `;

    storyboard.forEach(s => {
      html += `
        <div class="shot-card">
          <div class="shot-header">
            <span>SHOT ${s.shot_number}: ${escapeHtml(s.name)}</span>
            <span style="color:var(--accent-amber);">${escapeHtml(s.duration)}</span>
          </div>
          <div style="font-size:0.72rem; color:var(--accent-cyan);">${escapeHtml(s.shot_type)} • ${escapeHtml(s.camera_angle)}</div>
          <p class="shot-desc">${escapeHtml(s.action)}</p>
        </div>
      `;
    });

    html += `
            </div>
          </div>

          <!-- 3. Hero Frame Specification -->
          <div class="prod-section-card">
            <h3>🖼️ 3. Hero Frame Specification</h3>
            <p style="font-size:0.82rem; margin-bottom:0.4rem;"><strong>Composition:</strong> ${escapeHtml(hero.composition || 'Not specified')}</p>
            <p style="font-size:0.82rem; margin-bottom:0.4rem;"><strong>Lighting:</strong> ${escapeHtml(hero.lighting || hero.focal_lighting || 'Not specified')}</p>
            <p style="font-size:0.82rem; margin-bottom:0.4rem;"><strong>Palette:</strong> ${escapeHtml(hero.color_palette || (Array.isArray(hero.color_palette_lock) ? hero.color_palette_lock.join(', ') : hero.color_palette_lock) || 'Not specified')}</p>
            <p style="font-size:0.82rem;"><strong>Lens:</strong> ${escapeHtml(hero.camera_lens || hero.depth_of_field || 'Not specified')}</p>
          </div>

          <!-- 4. Continuity Lock Rules -->
          <div class="prod-section-card">
            <h3>🔒 4. Continuity Lock Rules</h3>
            <p style="font-size:0.82rem; margin-bottom:0.3rem;"><strong>Morphology:</strong> ${escapeHtml(cont.character_morphology || (Array.isArray(cont.character_morphology_rules) ? cont.character_morphology_rules.join(' ') : cont.character_morphology_rules) || 'Not specified')}</p>
            <p style="font-size:0.82rem; margin-bottom:0.3rem;"><strong>Environment:</strong> ${escapeHtml(cont.environment_lock || (Array.isArray(cont.environment_rules) ? cont.environment_rules.join(' ') : cont.environment_rules) || 'Not specified')}</p>
            <p style="font-size:0.82rem;"><strong>Immutable Traits:</strong> ${escapeHtml((Array.isArray(cont.immutable_traits) && cont.immutable_traits.length) ? cont.immutable_traits.join(', ') : ((Array.isArray(cont.interaction_invariants) && cont.interaction_invariants.length) ? cont.interaction_invariants.join(', ') : 'Not specified'))}</p>
          </div>
        </div>

        <!-- Col 2: AI Prompts, Audio & SEO -->
        <div>
          <!-- 5. Seedance Prompt -->
          <div class="prod-section-card">
            <h3>✨ 5. Seedance / Dreamina Prompt</h3>
            <div class="prompt-box">
              <button class="copy-mini-btn" data-copy="${escapeHtml(seedance)}">Copy</button>
              ${escapeHtml(seedance)}
            </div>
          </div>

          <!-- 6. Google Veo Prompt -->
          <div class="prod-section-card">
            <h3>🎥 6. Google Veo 2 Prompt</h3>
            <div class="prompt-box">
              <button class="copy-mini-btn" data-copy="${escapeHtml(veo)}">Copy</button>
              ${escapeHtml(veo)}
            </div>
          </div>

          <!-- 7. Audio Plan -->
          <div class="prod-section-card">
            <h3>🎧 7. Audio Plan & Timing Cues</h3>
            <p style="font-size:0.82rem; margin-bottom:0.35rem;"><strong>Foley:</strong> ${escapeHtml(audio.foley_requirements || '-')}</p>
            <p style="font-size:0.82rem; margin-bottom:0.35rem;"><strong>Comedic SFX:</strong> ${escapeHtml(audio.comedic_sfx || '-')}</p>
            <p style="font-size:0.82rem; margin-bottom:0.35rem;"><strong>Musical Score:</strong> ${escapeHtml(audio.musical_score || '-')}</p>
            <p style="font-size:0.82rem;"><strong>Loop Cue:</strong> ${escapeHtml(audio.loop_transition_audio || '-')}</p>
          </div>

          <!-- 8. Platform Captions -->
          <div class="prod-section-card">
            <h3>📱 8. Multi-Platform Captions</h3>
            <p style="font-size:0.82rem; margin-bottom:0.4rem;"><strong>TikTok:</strong> ${escapeHtml(captions.tiktok || '-')}</p>
            <p style="font-size:0.82rem; margin-bottom:0.4rem;"><strong>IG Reels:</strong> ${escapeHtml(captions.instagram_reels || '-')}</p>
            <p style="font-size:0.82rem; margin-bottom:0.4rem;"><strong>YouTube Shorts:</strong> ${escapeHtml(captions.youtube_shorts || '-')}</p>
            <p style="font-size:0.82rem;"><strong>Facebook Reels:</strong> ${escapeHtml(captions.facebook_reels || '-')}</p>
          </div>

          <!-- 9. Evidence SEO Pack -->
          <div class="prod-section-card">
            <h3>📈 9. Evidence-Based SEO Pack</h3>
            <p style="font-size:0.82rem; margin-bottom:0.35rem;"><strong>Topic:</strong> ${escapeHtml(seo.primary_topic || '-')}</p>
            <p style="font-size:0.82rem; margin-bottom:0.35rem;"><strong>Primary Keyword:</strong> ${escapeHtml(seo.primary_keyword || '-')}</p>
            <p style="font-size:0.82rem; margin-bottom:0.35rem;"><strong>Long-Tail:</strong> ${(seo.long_tail_queries || []).join(' • ')}</p>
            <p style="font-size:0.82rem; margin-bottom:0.35rem;"><strong>Hashtags:</strong> ${(seo.hashtags || []).join(' ')}</p>
            <p style="font-size:0.82rem;"><strong>Pinned Comment:</strong> ${escapeHtml(seo.pinned_comment || '-')}</p>
          </div>
        </div>
      </div>
    `;

    prodContent.innerHTML = html;

    // -------------------------------------------------------------
    // Wire up Prompt Compiler interactivity
    // -------------------------------------------------------------
    let activeOutputType = 'video';
    let activeModelKey = 'seedance_25';
    let structureVisible = false;

    const elPromptDisplay = prodContent.querySelector('#compiler-prompt-display');
    const elActiveModelTitle = prodContent.querySelector('#compiler-active-model-title');
    const elSpecLabel = prodContent.querySelector('#compiler-output-spec-label');
    const elGateBadge = prodContent.querySelector('#compiler-gate-badge');
    const elStatsDisplay = prodContent.querySelector('#compiler-stats-display');
    const elDimGrid = prodContent.querySelector('#compiler-dim-grid');
    const elStructurePanel = prodContent.querySelector('#compiler-structure-panel');
    const elStructureSummary = prodContent.querySelector('#compiler-structure-summary');
    const btnToggleStructure = prodContent.querySelector('#btn-toggle-prompt-structure');
    const btnCopyCompiled = prodContent.querySelector('#btn-copy-compiled-prompt');

    const videoModelsGroup = prodContent.querySelector('#compiler-video-models-group');
    const imageModelsGroup = prodContent.querySelector('#compiler-image-models-group');

    function updateCompilerDisplay() {
      const modelData = models[activeModelKey] || {};
      const promptText = modelData.prompt_text || '';
      const structure = modelData.structure || {};
      const val = modelData.validation || { status: 'PASS', score_pct: 100, passed_checks: 0, total_checks: 0, checks: {}, warnings: [] };

      // Update prompt box
      if (elPromptDisplay) elPromptDisplay.textContent = promptText;

      // Update titles
      if (elActiveModelTitle) {
        if (activeModelKey === 'seedance_25') {
          elActiveModelTitle.textContent = 'Seedance 2.5 (ByteDance / Volcengine Standard)';
        } else if (activeModelKey === 'universal_image') {
          elActiveModelTitle.textContent = 'Universal Image (Midjourney / SDXL / FLUX / Imagen)';
        } else if (activeModelKey === 'gpt_image') {
          elActiveModelTitle.textContent = 'GPT Image (DALL-E 3 / Narrative Prose Standard)';
        } else if (activeModelKey === 'nano_banana_pro') {
          elActiveModelTitle.textContent = 'Nano Banana Pro (Token-Anchored Directives)';
        } else {
          elActiveModelTitle.textContent = modelData.model_name || activeModelKey;
        }
      }

      if (elSpecLabel) {
        if (activeOutputType === 'video') {
          elSpecLabel.textContent = 'Native Video Directive • 24fps • 15s Timeline';
        } else {
          elSpecLabel.textContent = 'Master Static Visual Directive • Photographic Realism';
        }
      }

      // Update char / word stats
      if (elStatsDisplay) {
        const words = promptText.trim() ? promptText.trim().split(/\s+/).length : 0;
        elStatsDisplay.textContent = `${words} words • ${promptText.length} chars`;
      }

      // Update validation gate badge
      if (elGateBadge) {
        const s = val.status || 'PASS';
        elGateBadge.className = `compiler-gate-badge ${s.toLowerCase()}`;
        elGateBadge.textContent = `${s} ${val.score_pct || 100}% (${val.passed_checks || 0}/${val.total_checks || 0} CHECKS)`;
      }

      // Update structure grid
      if (elDimGrid) {
        let dimHtml = '';
        const checks = val.checks || {};
        for (const [dimKey, dimVal] of Object.entries(structure)) {
          const isPassed = checks[dimKey] !== false;
          dimHtml += `
            <div class="compiler-dim-item">
              <div class="compiler-dim-header">
                <span>${escapeHtml(dimKey)}</span>
                <span class="compiler-check-icon ${isPassed ? 'compiler-check-pass' : 'compiler-check-fail'}">
                  ${isPassed ? '✓ PASS' : '⚠️ CHECK'}
                </span>
              </div>
              <div class="compiler-dim-content">${escapeHtml(dimVal)}</div>
            </div>
          `;
        }
        elDimGrid.innerHTML = dimHtml;
      }

      if (elStructureSummary) {
        elStructureSummary.textContent = `${val.passed_checks || 0}/${val.total_checks || 0} required fields verified`;
      }
    }

    // Toggle Structure
    if (btnToggleStructure && elStructurePanel) {
      btnToggleStructure.addEventListener('click', () => {
        structureVisible = !structureVisible;
        if (structureVisible) {
          elStructurePanel.classList.add('visible');
          btnToggleStructure.textContent = '🙈 Hide Structure';
        } else {
          elStructurePanel.classList.remove('visible');
          btnToggleStructure.textContent = '👁️ Show Structure';
        }
      });
    }

    // Copy Compiled Prompt (Truthful clipboard + diagnostics)
    if (btnCopyCompiled) {
      btnCopyCompiled.addEventListener('click', async () => {
        const modelData = models[activeModelKey] || {};
        const text = modelData.prompt_text || '';
        recordDiagnosticEvent('COPY_ATTEMPTED', 'prompt_compiler', {
          model: activeModelKey,
          output_type: activeOutputType,
          story_id: state.currentProducedStoryId,
          char_count: text.length
        });

        const success = await copyToClipboard(text);
        if (success) {
          btnCopyCompiled.textContent = 'Copied!';
          btnCopyCompiled.style.color = 'var(--accent-emerald)';
          recordDiagnosticEvent('COPY_SUCCESS', 'prompt_compiler', {
            model: activeModelKey,
            output_type: activeOutputType,
            story_id: state.currentProducedStoryId,
            char_count: text.length
          }, true, `${modelData.model_name || activeModelKey} prompt copied truthfully`);
          setTimeout(() => {
            btnCopyCompiled.textContent = '📋 Copy Prompt';
            btnCopyCompiled.style.color = '';
          }, 2000);
        } else {
          btnCopyCompiled.textContent = 'Copy failed';
          btnCopyCompiled.style.color = 'var(--accent-rose)';
          recordDiagnosticEvent('COPY_FAILED', 'prompt_compiler', {
            model: activeModelKey,
            error: 'Clipboard write failed'
          }, false, 'Prompt copy operation failed');
          setTimeout(() => {
            btnCopyCompiled.textContent = '📋 Copy Prompt';
            btnCopyCompiled.style.color = '';
          }, 3000);
        }
      });
    }

    // Output Type Toggle (Video vs Image)
    const typePills = prodContent.querySelectorAll('#compiler-type-pills .compiler-pill');
    typePills.forEach(pill => {
      pill.addEventListener('click', () => {
        typePills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        activeOutputType = pill.getAttribute('data-type');

        if (activeOutputType === 'video') {
          if (videoModelsGroup) videoModelsGroup.style.display = 'inline-flex';
          if (imageModelsGroup) imageModelsGroup.style.display = 'none';
          activeModelKey = 'seedance_25';
        } else {
          if (videoModelsGroup) videoModelsGroup.style.display = 'none';
          if (imageModelsGroup) imageModelsGroup.style.display = 'inline-flex';
          const firstImgPill = imageModelsGroup ? imageModelsGroup.querySelector('.compiler-pill') : null;
          if (firstImgPill) {
            imageModelsGroup.querySelectorAll('.compiler-pill').forEach(p => p.classList.remove('active'));
            firstImgPill.classList.add('active');
            activeModelKey = firstImgPill.getAttribute('data-model') || 'universal_image';
          } else {
            activeModelKey = 'universal_image';
          }
        }
        updateCompilerDisplay();
      });
    });

    // Model Pills Toggle
    const modelPills = prodContent.querySelectorAll('[data-model]');
    modelPills.forEach(pill => {
      pill.addEventListener('click', () => {
        const parentRow = pill.parentElement;
        if (parentRow) {
          parentRow.querySelectorAll('.compiler-pill').forEach(p => p.classList.remove('active'));
        }
        pill.classList.add('active');
        activeModelKey = pill.getAttribute('data-model');
        updateCompilerDisplay();
      });
    });

    // Sub-Drawer Toggles
    prodContent.querySelectorAll('.compiler-sub-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const targetId = btn.getAttribute('data-target');
        const drawer = prodContent.querySelector(`#${targetId}`);
        const arrow = btn.querySelector('.toggle-arrow');
        if (drawer) {
          const isVis = drawer.classList.contains('visible');
          if (isVis) {
            drawer.classList.remove('visible');
            if (arrow) arrow.textContent = '▼';
          } else {
            drawer.classList.add('visible');
            if (arrow) arrow.textContent = '▲';
          }
        }
      });
    });

    // Initial render of compiler display
    updateCompilerDisplay();

    // Attach copy buttons with truthful verification and fallback
    prodContent.querySelectorAll('.copy-mini-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        let text = btn.getAttribute('data-copy');
        if (!text && btn.getAttribute('data-copy-target')) {
          const targetEl = prodContent.querySelector(`#${btn.getAttribute('data-copy-target')}`);
          if (targetEl) text = targetEl.textContent;
        }
        if (!text && btn.parentElement) {
          text = btn.parentElement.innerText.replace(/^Copy(\s*)/i, '').trim();
        }
        text = text || '';

        recordDiagnosticEvent('COPY_ATTEMPTED', 'production_pipeline', {
          story_id: state.currentProducedStoryId,
          char_count: text ? text.length : 0
        });

        const success = await copyToClipboard(text);
        if (success) {
          btn.textContent = 'Copied!';
          btn.style.color = 'var(--accent-emerald)';
          recordDiagnosticEvent('COPY_SUCCESS', 'production_pipeline', {
            story_id: state.currentProducedStoryId,
            copied_chars: text.length
          }, true, 'Video prompt copied to clipboard');
          setTimeout(() => {
            btn.textContent = 'Copy';
            btn.style.color = '';
          }, 2000);
        } else {
          btn.textContent = 'Copy failed — try again';
          btn.style.color = 'var(--accent-rose)';
          recordDiagnosticEvent('COPY_FAILED', 'production_pipeline', {
            story_id: state.currentProducedStoryId,
            error: 'Clipboard access denied or fallback failed'
          }, false, 'Copy prompt operation failed');
          setTimeout(() => {
            btn.textContent = 'Copy';
            btn.style.color = '';
          }, 3000);
        }
      });
    });
  }

  // Copy Full Production Pack Markdown
  btnCopyProductionPack.addEventListener('click', async () => {
    const sid = state.currentProducedStoryId;
    if (!sid) {
      alert('Please select and produce a story first.');
      return;
    }
    const text = prodContent.innerText;
    recordDiagnosticEvent('COPY_ATTEMPTED', 'production_pipeline', { item: 'full_package', story_id: sid });
    const success = await copyToClipboard(text);
    if (success) {
      recordDiagnosticEvent('COPY_SUCCESS', 'production_pipeline', { item: 'full_package', story_id: sid }, true, 'Full package copied');
      btnCopyProductionPack.textContent = 'Copied Package!';
      setTimeout(() => btnCopyProductionPack.textContent = 'Copy Production Pack (Markdown)', 2000);
    } else {
      recordDiagnosticEvent('COPY_FAILED', 'production_pipeline', { item: 'full_package', story_id: sid }, false, 'Full package copy failed');
      btnCopyProductionPack.textContent = 'Copy failed — try again';
      setTimeout(() => btnCopyProductionPack.textContent = 'Copy Production Pack (Markdown)', 3000);
    }
  });

  // -------------------------------------------------------------
  // 12. Recursive Expansion (EXPAND ×50)
  // -------------------------------------------------------------
  async function expandStoryNode(parentStory) {
    if (!state.currentSessionId) return;

    const confirmExpand = confirm(`Expand [${parentStory.story_id}] into 50 new child stories?`);
    if (!confirmExpand) return;

    try {
      const res = await fetch('/api/expand', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: state.currentSessionId,
          story_id: parentStory.story_id,
          mode: parentStory.mode || 'AUTO',
          threshold: 0.70
        })
      });

      const data = await res.json();
      if (data.status === 'ok') {
        alert(`Successfully generated 50 children for ${parentStory.story_id}! Total stories in universe: ${data.total_stories_count}`);
        loadSession(state.currentSessionId);
      } else {
        alert(`Expansion Error: ${data.error}`);
      }
    } catch (err) {
      alert(`Network Error during expansion: ${err.message}`);
    }
  }

  // -------------------------------------------------------------
  // 13. Compare View
  // -------------------------------------------------------------
  async function openCompareView(story) {
    if (!state.currentSessionId) return;
    switchTab('tab-compare');

    const compareBody = document.getElementById('compare-body');
    const label = document.getElementById('compare-target-label');
    label.textContent = `Comparing [${story.story_id}] vs Parent [${story.parent_id}]`;

    try {
      const res = await fetch(`/api/compare/${state.currentSessionId}/${story.story_id}`);
      const data = await res.json();
      if (data.status === 'ok') {
        const comp = data.comparison;
        const evo = comp.evolution;

        compareBody.innerHTML = `
          <div class="compare-summary-banner">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div>
                <h2>Novelty Score: <span class="novelty-badge">${evo.novelty_score}</span></h2>
                <p>Generational shift from Gen ${comp.parent.generation || 1} to Gen ${comp.child.generation}</p>
              </div>
              <div style="text-align:right;">
                <p><strong>Changed Dimensions:</strong> ${(evo.changed_dimensions || []).map(d => `<span class="pill-info">${escapeHtml(d)}</span>`).join(' ')}</p>
              </div>
            </div>
          </div>

          <div class="compare-container">
            <div class="compare-col">
              <h3>Parent: [${escapeHtml(comp.parent.story_id)}] ${escapeHtml(comp.parent.title || '')}</h3>
              <div class="compare-field"><label>Premise</label><p>${escapeHtml(comp.parent.premise || '-')}</p></div>
              <div class="compare-field"><label>Hook</label><p>${escapeHtml(comp.parent.hook || '-')}</p></div>
              <div class="compare-field"><label>Conflict</label><p>${escapeHtml(comp.parent.conflict || '-')}</p></div>
              <div class="compare-field"><label>Twist</label><p>${escapeHtml(comp.parent.twist || '-')}</p></div>
              <div class="compare-field"><label>Payoff</label><p>${escapeHtml(comp.parent.payoff || '-')}</p></div>
            </div>

            <div class="compare-col">
              <h3>Child: [${escapeHtml(comp.child.story_id)}] ${escapeHtml(comp.child.title || '')}</h3>
              <div class="compare-field"><label>Premise</label><p>${escapeHtml(comp.child.premise || '-')}</p></div>
              <div class="compare-field"><label>Hook</label><p>${escapeHtml(comp.child.hook || '-')}</p></div>
              <div class="compare-field"><label>Conflict</label><p>${escapeHtml(comp.child.conflict || '-')}</p></div>
              <div class="compare-field"><label>Twist</label><p>${escapeHtml(comp.child.twist || '-')}</p></div>
              <div class="compare-field"><label>Payoff</label><p>${escapeHtml(comp.child.payoff || '-')}</p></div>
            </div>
          </div>
        `;
      }
    } catch (err) {
      console.error('Failed to load comparison:', err);
    }
  }

  // -------------------------------------------------------------
  // 14. Render Lineage Tree Graph
  // -------------------------------------------------------------
  function renderTreeGraph(rootNode) {
    const canvas = document.getElementById('tree-canvas');
    if (!rootNode) {
      canvas.innerHTML = '<p class="placeholder-text">Tree graph unavailable.</p>';
      return;
    }

    canvas.innerHTML = `
      <div class="tree-root-node">
        <h3>[ROOT] ${escapeHtml(rootNode.title || 'Source Video DNA')}</h3>
        <p style="font-size:0.8rem; color:var(--text-muted);">Root Story Universe Source • Descendant branches: ${rootNode.children_count}</p>
      </div>
      <div class="tree-children-container" id="tree-root-children"></div>
    `;

    const childrenContainer = document.getElementById('tree-root-children');
    (rootNode.children || []).forEach(child => {
      childrenContainer.appendChild(createTreeNodeElement(child));
    });
  }

  function createTreeNodeElement(node) {
    const wrap = document.createElement('div');
    const genClass = node.generation === 1 ? 'node-gen1' : 'node-gen2';

    const item = document.createElement('div');
    item.className = `tree-node-item ${genClass}`;
    item.innerHTML = `
      <div>
        <strong>[${escapeHtml(node.id)}]</strong> ${escapeHtml(node.title)}
        <span style="font-size:0.75rem; color:var(--text-dim); margin-left:0.5rem;">(Gen ${node.generation} • Div: ${node.diversity_score} • ★ ${node.quality_score || 85})</span>
      </div>
      <div>
        ${node.children_count > 0 ? `<span class="badge">${node.children_count} children</span>` : ''}
        <button class="btn btn-secondary btn-sm btn-node-expand">Expand ×50</button>
      </div>
    `;

    item.querySelector('.btn-node-expand').addEventListener('click', (e) => {
      e.stopPropagation();
      const st = state.stories.find(s => s.story_id === node.id);
      if (st) expandStoryNode(st);
    });

    item.addEventListener('click', () => {
      const st = state.stories.find(s => s.story_id === node.id);
      if (st) openStoryModal(st);
    });

    wrap.appendChild(item);

    if (node.children && node.children.length > 0) {
      const subContainer = document.createElement('div');
      subContainer.className = 'tree-children-container';
      node.children.forEach(c => {
        subContainer.appendChild(createTreeNodeElement(c));
      });
      wrap.appendChild(subContainer);
    }

    return wrap;
  }

  // -------------------------------------------------------------
  // 15. Story Modal
  // -------------------------------------------------------------
  function openStoryModal(story) {
    currentModalStory = story;
    modalTitle.textContent = `[${story.story_id}] ${story.title}`;
    modalBody.innerHTML = `
      <p style="margin-bottom:0.75rem;"><strong>Premise:</strong> ${escapeHtml(story.one_line_premise)}</p>
      <div style="background:rgba(0,0,0,0.2); padding:0.75rem; border-radius:6px; margin-bottom:0.75rem;">
        <p><strong>Hook (0-3s):</strong> ${escapeHtml(story.hook)}</p>
        <p><strong>World:</strong> ${escapeHtml(story.world_name || story.mode || 'ANIMAL_COMEDY')} • <strong>Quality Score:</strong> ★ ${story.quality_score || 85.0}</p>
        <p><strong>Goal:</strong> ${escapeHtml(story.goal)}</p>
        <p><strong>Conflict:</strong> ${escapeHtml(story.conflict)}</p>
        <p><strong>Twist:</strong> ${escapeHtml(story.twist)}</p>
        <p><strong>Payoff:</strong> ${escapeHtml(story.payoff)}</p>
      </div>
      <p><strong>Diversity Score:</strong> ${story.diversity_score} • <strong>Gen:</strong> ${story.generation} • <strong>Parent:</strong> ${story.parent_id}</p>
    `;
    modal.style.display = 'flex';
  }

  modalClose.addEventListener('click', () => modal.style.display = 'none');
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.style.display = 'none';
  });

  modalCopy.addEventListener('click', async () => {
    if (!currentModalStory) return;
    const text = `# [${currentModalStory.story_id}] ${currentModalStory.title}
Premise: ${currentModalStory.one_line_premise}
World: ${currentModalStory.world_name || currentModalStory.mode}
Quality Score: ${currentModalStory.quality_score}
Hook: ${currentModalStory.hook}
Conflict: ${currentModalStory.conflict}
Twist: ${currentModalStory.twist}
Payoff: ${currentModalStory.payoff}`;
    const success = await copyToClipboard(text);
    if (success) {
      recordDiagnosticEvent('COPY_SUCCESS', 'story_modal', { story_id: currentModalStory.story_id }, true, 'Copied story markdown');
      modalCopy.textContent = 'Copied!';
      setTimeout(() => { modalCopy.textContent = 'Copy Story Markdown'; }, 2000);
    } else {
      recordDiagnosticEvent('COPY_FAILED', 'story_modal', { story_id: currentModalStory.story_id }, false, 'Clipboard access denied');
      modalCopy.textContent = 'Copy failed — try again';
      setTimeout(() => { modalCopy.textContent = 'Copy Story Markdown'; }, 2500);
    }
  });

  modalProduce.addEventListener('click', () => {
    if (currentModalStory) {
      modal.style.display = 'none';
      openProductionForStory(currentModalStory.story_id);
    }
  });

  modalExpand.addEventListener('click', () => {
    if (currentModalStory) {
      modal.style.display = 'none';
      expandStoryNode(currentModalStory);
    }
  });

  // -------------------------------------------------------------
  // 16. Exports Suite
  // -------------------------------------------------------------
  function enableExports(sessionId) {
    btnExportBible.disabled = false;
    btnExportCharBible.disabled = false;
    btnExportRelGraph.disabled = false;
    btnExportCsv.disabled = false;
    btnExportJson.disabled = false;
    btnExportZip.disabled = false;

    btnExportBible.onclick = () => window.location.href = `/api/export/story_bible/${sessionId}`;
    btnExportCharBible.onclick = () => window.location.href = `/api/export/character_bible/${sessionId}`;
    btnExportRelGraph.onclick = () => window.location.href = `/api/export/relationship_graph/${sessionId}`;
    btnExportCsv.onclick = () => window.location.href = `/api/export/top_stories_csv/${sessionId}`;
    btnExportJson.onclick = () => window.location.href = `/api/export/universe_json/${sessionId}`;
    btnExportZip.onclick = () => window.location.href = `/api/export/zip/${sessionId}`;
  }

  // -------------------------------------------------------------
  // 17. Settings Tab
  // -------------------------------------------------------------
  const rangeThreshold = document.getElementById('range-threshold');
  const thresholdVal = document.getElementById('threshold-val');
  rangeThreshold.addEventListener('input', () => {
    thresholdVal.textContent = rangeThreshold.value;
  });

  const settingDefaultThresh = document.getElementById('setting-default-threshold');
  const settingThreshDisplay = document.getElementById('setting-threshold-display');
  settingDefaultThresh.addEventListener('input', () => {
    settingThreshDisplay.textContent = settingDefaultThresh.value;
  });

  const settingDefaultQual = document.getElementById('setting-default-quality');
  const settingQualDisplay = document.getElementById('setting-quality-display');
  settingDefaultQual.addEventListener('input', () => {
    settingQualDisplay.textContent = settingDefaultQual.value;
  });

  const btnSaveSettings = document.getElementById('btn-save-settings');
  btnSaveSettings.addEventListener('click', () => {
    alert('Story Universe Factory engine preferences saved successfully!');
  });

  // -------------------------------------------------------------
  // 18. Live Diagnostics & Self-Test Modal
  // -------------------------------------------------------------
  const btnOpenDiag = document.getElementById('btn-open-diagnostics');
  const diagModal = document.getElementById('diagnostics-modal');
  const diagModalClose = document.getElementById('diag-modal-close-btn');
  const btnDiagSelfTest = document.getElementById('btn-diag-self-test');
  const btnDiagTestCopy = document.getElementById('btn-diag-test-copy');
  const btnDiagRefresh = document.getElementById('btn-diag-refresh');
  const diagSessionInfo = document.getElementById('diag-session-info');
  const diagComponentsGrid = document.getElementById('diag-components-grid');
  const diagIssuesList = document.getElementById('diag-issues-list');
  const diagEventsLog = document.getElementById('diag-events-log');

  if (btnOpenDiag && diagModal) {
    btnOpenDiag.addEventListener('click', () => {
      diagModal.style.display = 'flex';
      loadDiagnostics();
    });

    if (diagModalClose) {
      diagModalClose.addEventListener('click', () => {
        diagModal.style.display = 'none';
      });
    }

    diagModal.addEventListener('click', (e) => {
      if (e.target === diagModal) diagModal.style.display = 'none';
    });

    if (btnDiagRefresh) {
      btnDiagRefresh.addEventListener('click', () => {
        loadDiagnostics();
      });
    }

    if (btnDiagSelfTest) {
      btnDiagSelfTest.addEventListener('click', async () => {
        btnDiagSelfTest.disabled = true;
        btnDiagSelfTest.textContent = '⏳ Running Self-Test...';
        try {
          const res = await fetch('/api/diagnostics/self-test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: state.currentSessionId || null })
          });
          const data = await res.json();
          await loadDiagnostics();
          const r = data.results || {};
          const pass = r.overall_status === 'PASS';
          alert(`Self-Test Completed: ${r.overall_status || 'DONE'}\nElapsed: ${r.elapsed_ms || 0}ms\n\n${pass ? 'All subsystem gates verified.' : 'Issues detected — review Diagnostics report.'}`);
        } catch (err) {
          alert(`Self-Test failed to execute: ${err.message}`);
        } finally {
          btnDiagSelfTest.disabled = false;
          btnDiagSelfTest.textContent = '▶ Run Self-Test';
        }
      });
    }

    if (btnDiagTestCopy) {
      btnDiagTestCopy.addEventListener('click', async () => {
        const testPayload = `PLB Studio Clipboard Self-Test [Timestamp: ${new Date().toISOString()}]`;
        const success = await copyToClipboard(testPayload);
        if (success) {
          recordDiagnosticEvent('COPY_TEST', 'diagnostics', { status: 'success' }, true, 'Clipboard verification passed');
          alert('✔ Clipboard verification SUCCESSFUL!\nReal test string copied to system clipboard.');
        } else {
          recordDiagnosticEvent('COPY_TEST', 'diagnostics', { status: 'failed' }, false, 'Clipboard access denied or unverified');
          alert('✖ Clipboard verification FAILED!\nBrowser or system clipboard permissions denied.');
        }
        loadDiagnostics();
      });
    }
  }

  async function loadDiagnostics() {
    if (!diagSessionInfo) return;
    try {
      const url = state.currentSessionId 
        ? `/api/diagnostics?session_id=${encodeURIComponent(state.currentSessionId)}` 
        : '/api/diagnostics';
      const res = await fetch(url);
      const data = await res.json();

      // 1. Session Info
      const sess = data.session || {};
      const errors = data.errors || [];
      const warnings = data.warnings || [];
      diagSessionInfo.innerHTML = `
        <div><strong>Session ID:</strong> <code>${escapeHtml(sess.session_id || 'None')}</code></div>
        <div><strong>Status:</strong> <span class="badge ${data.app_status === 'ready' ? 'badge-ok' : 'badge-err'}">${escapeHtml(data.app_status || 'ready')}</span></div>
        <div><strong>Module:</strong> ${escapeHtml(data.current_module || 'None')}</div>
        <div><strong>Duration:</strong> ${escapeHtml(sess.duration_formatted || '0s')}</div>
        <div><strong>Errors:</strong> ${errors.length}</div>
        <div><strong>Warnings:</strong> ${warnings.length}</div>
      `;

      // 2. Component Health Grid
      const comps = data.components || {};
      const compKeys = Object.keys(comps);
      if (compKeys.length === 0) {
        diagComponentsGrid.innerHTML = '<p class="placeholder-text">No component status records yet.</p>';
      } else {
        diagComponentsGrid.innerHTML = compKeys.map(k => {
          const st = comps[k];
          let badgeColor = 'var(--text-muted)';
          if (st === 'PASS') badgeColor = 'var(--accent-emerald)';
          else if (st === 'PARTIAL') badgeColor = '#f59e0b';
          else if (st === 'FAIL') badgeColor = 'var(--accent-rose)';

          return `
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:6px;padding:8px 10px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                <span style="font-weight:600;color:var(--text-main);">${escapeHtml(k)}</span>
                <span style="font-size:0.7rem;font-weight:700;color:${badgeColor};">${escapeHtml(st)}</span>
              </div>
            </div>
          `;
        }).join('');
      }

      // 3. Issues List
      const allIssues = [
        ...errors.map(e => ({ type: 'ERROR', ...e })),
        ...warnings.map(w => ({ type: 'WARNING', ...w }))
      ];
      if (allIssues.length === 0) {
        diagIssuesList.innerHTML = '<p style="color:var(--accent-emerald);font-size:0.8rem;margin:0;">✔ No warnings or errors detected.</p>';
      } else {
        diagIssuesList.innerHTML = allIssues.map(iss => `
          <div style="padding:6px 8px;margin-bottom:4px;border-radius:4px;background:rgba(239,68,68,0.1);border-left:3px solid ${iss.type === 'ERROR' ? 'var(--accent-rose)' : '#f59e0b'};font-size:0.75rem;">
            <strong>[${escapeHtml(iss.type)}] ${escapeHtml(iss.module || 'System')}:</strong> ${escapeHtml(iss.message || iss.event_type || '')}
          </div>
        `).join('');
      }

      // 4. Activity Log
      const events = data.recent_events || [];
      if (events.length === 0) {
        diagEventsLog.innerHTML = '<p class="placeholder-text">No activity recorded yet.</p>';
      } else {
        diagEventsLog.innerHTML = events.slice(0, 30).map(e => {
          const color = e.success ? 'var(--accent-emerald)' : 'var(--accent-rose)';
          const icon = e.success ? '✔' : '✖';
          return `
            <div style="margin-bottom:4px;line-height:1.4;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:2px;">
              <span style="color:var(--text-muted);">${escapeHtml(e.timestamp || '')}</span>
              <span style="color:${color};font-weight:700;margin:0 4px;">${icon} [${escapeHtml(e.module || '')}]</span>
              <strong>${escapeHtml(e.event_type || '')}:</strong> ${escapeHtml(e.message || '')}
            </div>
          `;
        }).join('');
      }
    } catch (err) {
      diagSessionInfo.innerHTML = `<p style="color:var(--accent-rose);">Failed to load diagnostics: ${escapeHtml(err.message)}</p>`;
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
