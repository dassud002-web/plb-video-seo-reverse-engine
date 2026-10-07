/**
 * PLB Story Forge — Frontend Application Script
 * Orchestrates video analysis, Story DNA display, 50 root stories grid,
 * recursive expansion, interactive lineage tree, and comparisons.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Application State
  const state = {
    selectedPath: null,
    currentSessionId: null,
    sessionData: null,
    stories: [],
    lineageGraph: null,
    activeTab: 'tab-video',
    activePollingId: null
  };

  // DOM Elements
  const tabs = document.querySelectorAll('.nav-tab');
  const panes = document.querySelectorAll('.tab-pane');
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');
  const pathInput = document.getElementById('video-path-input');
  const btnScanPath = document.getElementById('btn-scan-path');
  const candidateBtnsContainer = document.getElementById('candidate-buttons');
  const inspectionBox = document.getElementById('inspection-box');
  const btnForge = document.getElementById('btn-forge-stories');
  const progressBox = document.getElementById('progress-box');
  const progressStage = document.getElementById('progress-stage');
  const progressPct = document.getElementById('progress-pct');
  const progressBarFill = document.getElementById('progress-bar-fill');
  const recentSessionsList = document.getElementById('recent-sessions-list');
  const currentSessionLabel = document.getElementById('current-session-label');

  // Filter & Search Controls
  const filterMode = document.getElementById('filter-story-mode');
  const searchInput = document.getElementById('search-story-text');
  const sortSelect = document.getElementById('sort-stories');
  const storiesGrid = document.getElementById('stories-grid');
  const visibleStoriesCount = document.getElementById('visible-stories-count');
  const totalStoriesCount = document.getElementById('total-stories-count');
  const storiesCountBadge = document.getElementById('stories-count-badge');

  // Export Buttons
  const btnExportMd = document.getElementById('btn-export-md');
  const btnExportJson = document.getElementById('btn-export-json');
  const btnExportTxt = document.getElementById('btn-export-txt');
  const btnExportZip = document.getElementById('btn-export-zip');

  // Modal Elements
  const modal = document.getElementById('story-modal');
  const modalTitle = document.getElementById('modal-story-title');
  const modalBody = document.getElementById('modal-story-body');
  const modalClose = document.getElementById('modal-close-btn');
  const modalCopy = document.getElementById('modal-copy-btn');
  const modalExpand = document.getElementById('modal-expand-btn');
  let currentModalStory = null;

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
            pathInput.value = cand.path;
            inspectVideoPath(cand.path);
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
  // 3. File Selection & Drag & Drop
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
    if (e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      // On local browsers, file.name can be used if in project directory, or full path if available
      pathInput.value = file.name;
      inspectVideoPath(file.name);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      const file = fileInput.files[0];
      pathInput.value = file.name;
      inspectVideoPath(file.name);
    }
  });

  btnScanPath.addEventListener('click', () => {
    const p = pathInput.value.trim();
    if (p) inspectVideoPath(p);
  });

  async function inspectVideoPath(targetPath) {
    try {
      const res = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: targetPath })
      });
      const data = await res.json();
      if (data.status === 'ok') {
        state.selectedPath = data.file_info.path;
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
  // 4. Analysis & 50 Story Generation
  // -------------------------------------------------------------
  btnForge.addEventListener('click', startAnalysis);

  async function startAnalysis() {
    if (!state.selectedPath) return;

    btnForge.disabled = true;
    progressBox.style.display = 'block';
    progressPct.textContent = '5%';
    progressBarFill.style.width = '5%';
    progressStage.textContent = 'Initializing Story Forge engine...';

    const mode = document.getElementById('select-mode').value;
    const threshold = document.getElementById('range-threshold').value;

    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          path: state.selectedPath,
          mode: mode,
          threshold: threshold
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
        progressStage.textContent = st.stage || 'Processing...';

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
  // 5. Load Session Data & Render Views
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

        currentSessionLabel.textContent = `Session: ${sessionId}`;

        // Render Views
        renderStoryDna(data.story_dna, data.session);
        renderStoriesGrid();
        renderTreeGraph(data.lineage_graph);
        enableExports(sessionId);

        // Switch to 50 Stories Tab
        switchTab('tab-stories');
      }
    } catch (err) {
      console.error('Failed to load session:', err);
    }
  }

  // -------------------------------------------------------------
  // 6. Render Story DNA
  // -------------------------------------------------------------
  function renderStoryDna(dna, session) {
    if (!dna) return;
    document.getElementById('dna-asset-name').textContent = session.source_video_name || 'Root Video Asset';
    document.getElementById('dna-core-premise').textContent = dna.core_premise || '-';
    document.getElementById('dna-central-tension').textContent = dna.central_tension || '-';
    document.getElementById('dna-char-dynamic').textContent = dna.primary_character_dynamic || '-';
    document.getElementById('dna-engine').textContent = dna.primary_comedic_emotional_engine || '-';

    // Characters & Setting
    const charsDiv = document.getElementById('dna-chars-setting');
    let charsHtml = `<p><strong>Setting:</strong> ${escapeHtml(dna.setting || '-')}</p>`;
    charsHtml += `<p><strong>Observed:</strong> ${escapeHtml(dna.setting_observed || '-')}</p>`;
    charsHtml += `<p><strong>Characters:</strong></p><ul>`;
    (dna.characters || []).forEach(c => {
      charsHtml += `<li><strong>${escapeHtml(c.name)}</strong>: ${escapeHtml(c.observed_fact || '')}</li>`;
    });
    charsHtml += `</ul>`;
    charsDiv.innerHTML = charsHtml;

    // Narrative Progression
    const progDiv = document.getElementById('dna-progression');
    let progHtml = `<p><strong>Hook:</strong> ${escapeHtml(dna.hook || '-')}</p>`;
    progHtml += `<p><strong>Conflict:</strong> ${escapeHtml(dna.conflict || '-')}</p>`;
    progHtml += `<p><strong>Twist:</strong> ${escapeHtml(dna.twist || '-')}</p>`;
    progHtml += `<p><strong>Payoff:</strong> ${escapeHtml(dna.payoff || '-')}</p>`;
    progDiv.innerHTML = progHtml;

    // Reusable Elements
    const reusDiv = document.getElementById('dna-reusable');
    let reusHtml = '<ul>';
    (dna.reusable_story_elements || []).forEach(el => {
      reusHtml += `<li><strong>${escapeHtml(el.element)}</strong> (${escapeHtml(el.reusability)}): ${escapeHtml(el.source)}</li>`;
    });
    reusHtml += '</ul>';
    reusDiv.innerHTML = reusHtml;

    // Evidence tags
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
  // 7. Render 50 Stories Grid
  // -------------------------------------------------------------
  filterMode.addEventListener('change', renderStoriesGrid);
  searchInput.addEventListener('input', renderStoriesGrid);
  sortSelect.addEventListener('change', renderStoriesGrid);

  function renderStoriesGrid() {
    storiesGrid.innerHTML = '';
    const modeVal = filterMode.value;
    const query = searchInput.value.toLowerCase().trim();
    const sortVal = sortSelect.value;

    let filtered = state.stories.filter(s => {
      if (modeVal !== 'ALL' && s.mode !== modeVal) return false;
      if (query) {
        const fullText = `${s.title} ${s.one_line_premise} ${s.conflict} ${s.twist}`.toLowerCase();
        if (!fullText.includes(query)) return false;
      }
      return true;
    });

    // Sorting
    if (sortVal === 'div_desc') {
      filtered.sort((a, b) => (b.diversity_score || 0) - (a.diversity_score || 0));
    } else if (sortVal === 'gen_asc') {
      filtered.sort((a, b) => (a.generation || 1) - (b.generation || 1));
    } else {
      filtered.sort((a, b) => a.story_id.localeCompare(b.story_id, undefined, { numeric: true }));
    }

    visibleStoriesCount.textContent = filtered.length;
    totalStoriesCount.textContent = state.stories.length;
    storiesCountBadge.textContent = state.stories.length;

    if (filtered.length === 0) {
      storiesGrid.innerHTML = '<p class="placeholder-text">No stories match the active filters.</p>';
      return;
    }

    filtered.forEach(s => {
      const card = document.createElement('div');
      card.className = 'story-card';
      card.innerHTML = `
        <div class="story-card-header">
          <span class="story-id-tag">[${escapeHtml(s.story_id)}]</span>
          <span class="mode-tag">${escapeHtml(s.mode || 'AUTO')}</span>
          <span class="div-tag">Div: ${s.diversity_score}</span>
        </div>
        <h3 class="story-card-title">${escapeHtml(s.title)}</h3>
        <p class="story-card-premise">${escapeHtml(s.one_line_premise)}</p>
        <div class="story-card-meta">
          <div><strong>Hook:</strong> ${escapeHtml(s.hook || '-')}</div>
          <div><strong>Conflict:</strong> ${escapeHtml(s.conflict || '-')}</div>
          <div><strong>Payoff:</strong> ${escapeHtml(s.payoff || '-')}</div>
          <div><strong>Gen:</strong> ${s.generation || 1} • <strong>Parent:</strong> ${s.parent_id || 'ROOT'}</div>
        </div>
        <div class="story-card-actions">
          <button class="btn btn-secondary btn-sm btn-view">View</button>
          <button class="btn btn-primary btn-sm btn-expand">Expand ×50</button>
          <button class="btn btn-secondary btn-sm btn-compare">Compare</button>
        </div>
      `;

      card.querySelector('.btn-view').addEventListener('click', (e) => {
        e.stopPropagation();
        openStoryModal(s);
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
  // 8. Recursive Expansion (EXPAND ×50)
  // -------------------------------------------------------------
  async function expandStoryNode(parentStory) {
    if (!state.currentSessionId) return;

    const confirmExpand = confirm(`Expand [${parentStory.story_id}] into 50 new child stories?`);
    if (!confirmExpand) return;

    try {
      const btn = event?.target;
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'Expanding...';
      }

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
        alert(`Successfully generated 50 children for ${parentStory.story_id}! Total stories: ${data.total_stories_count}`);
        // Reload session data
        loadSession(state.currentSessionId);
      } else {
        alert(`Expansion Error: ${data.error}`);
        if (btn) {
          btn.disabled = false;
          btn.textContent = 'Expand ×50';
        }
      }
    } catch (err) {
      alert(`Network Error during expansion: ${err.message}`);
    }
  }

  // -------------------------------------------------------------
  // 9. Compare View (Parent vs Child)
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
                <p><strong>Changed Dimensions:</strong> ${evo.changed_dimensions.map(d => `<span class="pill-info">${escapeHtml(d)}</span>`).join(' ')}</p>
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

          <div style="margin-top:1.5rem; display:grid; grid-template-columns:1fr 1fr 1fr; gap:1rem;">
            <div class="subcard">
              <h4>Inherited Elements</h4>
              <ul>${(evo.inherited_elements || []).map(el => `<li>${escapeHtml(el)}</li>`).join('') || '<li>None</li>'}</ul>
            </div>
            <div class="subcard">
              <h4>New Elements Introduced</h4>
              <ul>${(evo.new_elements || []).map(el => `<li>${escapeHtml(el)}</li>`).join('') || '<li>None</li>'}</ul>
            </div>
            <div class="subcard">
              <h4>Removed / Mutated</h4>
              <ul>${(evo.removed_elements || []).map(el => `<li>${escapeHtml(el)}</li>`).join('') || '<li>None</li>'}</ul>
            </div>
          </div>
        `;
      }
    } catch (err) {
      console.error('Failed to load comparison:', err);
    }
  }

  // -------------------------------------------------------------
  // 10. Render Lineage Tree Graph
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
        <p style="font-size:0.8rem; color:var(--text-muted);">Root Story DNA Source • Descendant branches: ${rootNode.children_count}</p>
      </div>
      <div class="tree-children-container" id="tree-root-children"></div>
    `;

    const childrenContainer = document.getElementById('tree-root-children');
    (rootNode.children || []).forEach(child => {
      const childEl = createTreeNodeElement(child);
      childrenContainer.appendChild(childEl);
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
        <span style="font-size:0.75rem; color:var(--text-dim); margin-left:0.5rem;">(Gen ${node.generation} • Div: ${node.diversity_score})</span>
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

    // If node has children, render sub-container
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
  // 11. Story Modal
  // -------------------------------------------------------------
  function openStoryModal(story) {
    currentModalStory = story;
    modalTitle.textContent = `[${story.story_id}] ${story.title}`;
    modalBody.innerHTML = `
      <p style="margin-bottom:0.75rem;"><strong>Premise:</strong> ${escapeHtml(story.one_line_premise)}</p>
      <div style="background:rgba(0,0,0,0.2); padding:0.75rem; border-radius:6px; margin-bottom:0.75rem;">
        <p><strong>Hook (0-3s):</strong> ${escapeHtml(story.hook)}</p>
        <p><strong>Goal:</strong> ${escapeHtml(story.goal)}</p>
        <p><strong>Conflict:</strong> ${escapeHtml(story.conflict)}</p>
        <p><strong>Escalation:</strong> ${escapeHtml(story.escalation)}</p>
        <p><strong>Twist:</strong> ${escapeHtml(story.twist)}</p>
        <p><strong>Payoff:</strong> ${escapeHtml(story.payoff)}</p>
      </div>
      <p><strong>Mode:</strong> ${escapeHtml(story.mode)} • <strong>Diversity Score:</strong> ${story.diversity_score}</p>
      <p><strong>Generation:</strong> ${story.generation} • <strong>Parent:</strong> ${story.parent_id}</p>
      <p><strong>New Elements:</strong> ${(story.new_elements || []).join(', ')}</p>
    `;
    modal.style.display = 'flex';
  }

  modalClose.addEventListener('click', () => modal.style.display = 'none');
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.style.display = 'none';
  });

  modalCopy.addEventListener('click', () => {
    if (!currentModalStory) return;
    const text = `# [${currentModalStory.story_id}] ${currentModalStory.title}
Premise: ${currentModalStory.one_line_premise}
Hook: ${currentModalStory.hook}
Conflict: ${currentModalStory.conflict}
Twist: ${currentModalStory.twist}
Payoff: ${currentModalStory.payoff}
Mode: ${currentModalStory.mode} | Diversity: ${currentModalStory.diversity_score}`;
    navigator.clipboard.writeText(text);
    alert('Story Markdown copied to clipboard!');
  });

  modalExpand.addEventListener('click', () => {
    if (currentModalStory) {
      modal.style.display = 'none';
      expandStoryNode(currentModalStory);
    }
  });

  // -------------------------------------------------------------
  // 12. Exports
  // -------------------------------------------------------------
  function enableExports(sessionId) {
    btnExportMd.disabled = false;
    btnExportJson.disabled = false;
    btnExportTxt.disabled = false;
    btnExportZip.disabled = false;

    btnExportMd.onclick = () => window.location.href = `/api/export/markdown/${sessionId}`;
    btnExportJson.onclick = () => window.location.href = `/api/export/json/${sessionId}`;
    btnExportTxt.onclick = () => window.location.href = `/api/export/txt/${sessionId}`;
    btnExportZip.onclick = () => window.location.href = `/api/export/zip/${sessionId}`;
  }

  // -------------------------------------------------------------
  // 13. Settings Tab
  // -------------------------------------------------------------
  const rangeThreshold = document.getElementById('range-threshold');
  const thresholdVal = document.getElementById('threshold-val');
  rangeThreshold.addEventListener('input', () => {
    thresholdVal.textContent = rangeThreshold.value;
  });

  const settingProvider = document.getElementById('setting-provider-mode');
  const groupApiKey = document.getElementById('group-api-key');
  settingProvider.addEventListener('change', () => {
    groupApiKey.style.display = settingProvider.value === 'configurable' ? 'block' : 'none';
  });

  const btnSaveSettings = document.getElementById('btn-save-settings');
  btnSaveSettings.addEventListener('click', () => {
    alert('Story Forge engine preferences saved successfully!');
  });

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
