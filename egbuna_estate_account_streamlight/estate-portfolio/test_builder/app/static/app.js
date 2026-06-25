// === LocalStorage Draft Cache ===
const DRAFTS_KEY = 'epm_test_builder_drafts';

function getDrafts() {
    try {
        return JSON.parse(localStorage.getItem(DRAFTS_KEY)) || [];
    } catch {
        return [];
    }
}

function saveDrafts(drafts) {
    localStorage.setItem(DRAFTS_KEY, JSON.stringify(drafts));
}

function addDraft(draft) {
    const drafts = getDrafts();
    drafts.push(draft);
    saveDrafts(drafts);
    renderDraftList();
    return drafts;
}

function clearDrafts() {
    localStorage.removeItem(DRAFTS_KEY);
    renderDraftList();
}

// === Test ID Generation ===
function generateTestId(domain, workflow, layer, testType, seqNum) {
    const seq = String(seqNum || 1).padStart(3, '0');
    return `${domain}-${workflow}-${layer}-${testType}-${seq}`;
}

// === Form Handling ===
document.addEventListener('DOMContentLoaded', () => {
    renderDraftList();

    const form = document.getElementById('test-case-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            handleSaveDraft();
        });
    }
});

function handleSaveDraft() {
    const domain = document.getElementById('domain').value.trim();
    const workflow = document.getElementById('workflow').value.trim();
    const layer = document.getElementById('layer').value.trim();
    const testType = document.getElementById('test_type').value.trim();
    const title = document.getElementById('title').value.trim();
    const requirementRef = document.getElementById('requirement_ref').value.trim();

    // Validation
    const errorEl = document.getElementById('form-error');
    errorEl.style.display = 'none';

    if (!domain) { showFormError('Domain is required'); return; }
    if (!workflow) { showFormError('Workflow is required'); return; }
    if (!layer) { showFormError('Layer is required to generate a Test ID'); return; }
    if (!testType) { showFormError('Test type is required'); return; }
    if (!title) { showFormError('Title is required'); return; }

    // Determine next sequence within current drafts
    const drafts = getDrafts();
    const sameKey = drafts.filter(d =>
        d.domain === domain.toUpperCase() &&
        d.workflow === workflow.toUpperCase() &&
        d.layer === layer.toUpperCase() &&
        d.test_type === testType.toUpperCase()
    );
    const nextSeq = sameKey.length + 1;
    const testId = generateTestId(domain, workflow, layer, testType, nextSeq);

    const draft = {
        id: testId,
        domain: domain.toUpperCase(),
        workflow: workflow.toUpperCase(),
        layer: layer.toUpperCase(),
        test_type: testType.toUpperCase(),
        sequence_no: nextSeq,
        title: title,
        requirement_ref: requirementRef || null,
        created_at: new Date().toISOString(),
    };

    addDraft(draft);
    document.getElementById('test-case-form').reset();
    document.getElementById('test-id-preview').textContent = '';
}

function showFormError(msg) {
    const el = document.getElementById('form-error');
    el.textContent = msg;
    el.style.display = 'block';
}

function previewTestId() {
    const domain = document.getElementById('domain').value.trim();
    const workflow = document.getElementById('workflow').value.trim();
    const layer = document.getElementById('layer').value.trim();
    const testType = document.getElementById('test_type').value.trim();

    if (!domain || !workflow || !layer || !testType) {
        document.getElementById('test-id-preview').textContent = 'Fill all taxonomy fields to preview ID';
        return;
    }

    const drafts = getDrafts();
    const sameKey = drafts.filter(d =>
        d.domain === domain.toUpperCase() &&
        d.workflow === workflow.toUpperCase() &&
        d.layer === layer.toUpperCase() &&
        d.test_type === testType.toUpperCase()
    );
    const nextSeq = sameKey.length + 1;
    const previewId = generateTestId(domain, workflow, layer, testType, nextSeq);
    document.getElementById('test-id-preview').textContent = `Preview: ${previewId}`;
}

// === Draft List Rendering ===
function renderDraftList() {
    const drafts = getDrafts();
    const listEl = document.getElementById('draft-list');
    const countEl = document.getElementById('draft-count');
    const submitBtn = document.getElementById('submit-btn');

    if (countEl) countEl.textContent = `${drafts.length} case${drafts.length !== 1 ? 'es' : ''}`;
    if (submitBtn) submitBtn.disabled = drafts.length === 0;

    if (!listEl) return;

    if (drafts.length === 0) {
        listEl.innerHTML = '<p class="text-muted text-center">No test cases drafted yet. Fill in the form above and click "Save Draft".</p>';
        return;
    }

    const table = document.createElement('table');
    table.className = 'data-table';
    table.innerHTML = `
        <thead>
            <tr>
                <th>Test ID</th>
                <th>Title</th>
                <th>Domain</th>
                <th>Layer</th>
                <th>Type</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            ${drafts.map((d, i) => `
                <tr>
                    <td class="font-mono">${d.id}</td>
                    <td>${escapeHtml(d.title)}</td>
                    <td>${d.domain}</td>
                    <td>${d.layer}</td>
                    <td>${d.test_type}</td>
                    <td><button class="btn btn-ghost btn-sm" onclick="removeDraft(${i})">Remove</button></td>
                </tr>
            `).join('')}
        </tbody>
    `;
    listEl.innerHTML = '';
    listEl.appendChild(table);
}

function removeDraft(index) {
    const drafts = getDrafts();
    drafts.splice(index, 1);
    saveDrafts(drafts);
    renderDraftList();
}

// === Submit to Database ===
async function submitDrafts() {
    const drafts = getDrafts();
    const errorEl = document.getElementById('submit-error');
    errorEl.style.display = 'none';

    if (drafts.length === 0) {
        showSubmitError('Add at least one test case before submitting');
        return;
    }

    try {
        const res = await fetch('/test-cases/api/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ cases: drafts }),
        });

        if (!res.ok) {
            const data = await res.json();
            showSubmitError(data.detail || 'Submission failed');
            return;
        }

        const data = await res.json();
        clearDrafts();
        window.location.href = '/test-cases/execute';
    } catch (err) {
        showSubmitError('Network error: ' + err.message);
    }
}

function showSubmitError(msg) {
    const el = document.getElementById('submit-error');
    el.textContent = msg;
    el.style.display = 'block';
}

// === Utility ===
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
