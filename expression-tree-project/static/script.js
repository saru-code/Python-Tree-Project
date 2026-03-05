/**
 * ============================================================================
 *  Expression Tree Evaluation — Frontend JavaScript
 * ============================================================================
 *
 *  This script handles:
 *    1. Capturing user input from the expression text box
 *    2. Sending a POST request to the Flask /evaluate endpoint
 *    3. Rendering traversal results and the evaluated answer
 *    4. Drawing an interactive expression tree visualisation using SVG
 *
 *  No external libraries are used — just vanilla JavaScript + SVG.
 * ============================================================================
 */

// ─── DOM Element References ─────────────────────────────────────────────────
const expressionInput = document.getElementById('expressionInput');
const generateBtn = document.getElementById('generateBtn');
const evaluateBtn = document.getElementById('evaluateBtn');
const errorBox = document.getElementById('errorBox');
const resultsSection = document.getElementById('resultsSection');
const treeContainer = document.getElementById('treeContainer');
const inorderResult = document.getElementById('inorderResult');
const preorderResult = document.getElementById('preorderResult');
const postorderResult = document.getElementById('postorderResult');
const postfixResult = document.getElementById('postfixResult');
const finalResult = document.getElementById('finalResult');


// ─── Event Listeners ────────────────────────────────────────────────────────

// Both buttons trigger the same evaluation pipeline
generateBtn.addEventListener('click', handleEvaluate);
evaluateBtn.addEventListener('click', handleEvaluate);

// Allow pressing Enter to submit
expressionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleEvaluate();
});

// Sample expression chips — click to auto-fill and evaluate
document.querySelectorAll('.sample-chip').forEach(chip => {
    chip.addEventListener('click', () => {
        expressionInput.value = chip.dataset.expr;
        handleEvaluate();
    });
});


// ─── Main Handler ───────────────────────────────────────────────────────────

/**
 * Read the expression from the input box, call the Flask API,
 * and render the results on the page.
 */
async function handleEvaluate() {
    const expression = expressionInput.value.trim();

    // Validate that the user typed something
    if (!expression) {
        showError('Please enter an arithmetic expression.');
        return;
    }

    hideError();
    setLoading(true);

    try {
        // ── Call the Flask API ──
        const response = await fetch('/evaluate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ expression })
        });

        const data = await response.json();

        if (!response.ok) {
            // Server returned an error (e.g. invalid expression)
            showError(data.error || 'Something went wrong.');
            resultsSection.classList.add('hidden');
            return;
        }

        // ── Populate traversal results ──
        inorderResult.textContent = data.inorder;
        preorderResult.textContent = data.preorder;
        postorderResult.textContent = data.postorder;
        postfixResult.textContent = data.postfix;

        // ── Show the evaluated result with animation ──
        finalResult.textContent = data.result;
        finalResult.classList.remove('pop');
        // Force reflow so the animation re-triggers
        void finalResult.offsetWidth;
        finalResult.classList.add('pop');

        // ── Draw the expression tree ──
        drawTree(data.tree);

        // ── Reveal the results section ──
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (err) {
        showError('Could not connect to the server. Is Flask running?');
        console.error(err);
    } finally {
        setLoading(false);
    }
}


// ─── Error Display Helpers ──────────────────────────────────────────────────

function showError(msg) {
    errorBox.textContent = msg;
    errorBox.classList.remove('hidden');
}

function hideError() {
    errorBox.textContent = '';
    errorBox.classList.add('hidden');
}

function setLoading(isLoading) {
    generateBtn.disabled = isLoading;
    evaluateBtn.disabled = isLoading;
    if (isLoading) {
        generateBtn.innerHTML = '<span class="spinner"></span> Processing…';
    } else {
        generateBtn.innerHTML = '<span class="btn-icon">🌲</span> Generate Tree';
    }
}


// ═══════════════════════════════════════════════════════════════════════════
//  EXPRESSION TREE VISUALISATION  (SVG-based)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Compute the layout of a binary tree and draw it as an SVG.
 *
 * The approach:
 *   1. Recursively compute the width (horizontal span) needed for each subtree.
 *   2. Position each node using (x, y) coordinates based on its depth and
 *      the width allocated to its subtree.
 *   3. Draw SVG elements: lines (edges) and circles+text (nodes).
 *
 * @param {Object} tree  – The tree in JSON form: { value, left?, right? }
 */
function drawTree(tree) {
    if (!tree) {
        treeContainer.innerHTML = '<p class="empty-tree">No tree to display.</p>';
        return;
    }

    // ── Layout parameters ──
    const nodeRadius = 38;
    const levelHeight = 110;
    const horizontalGap = 28;

    // ── Step 1: Compute subtree widths recursively ──
    function computeWidth(node) {
        if (!node) return 0;
        if (!node.left && !node.right) return nodeRadius * 2 + horizontalGap;
        const lw = computeWidth(node.left);
        const rw = computeWidth(node.right);
        return lw + rw + horizontalGap;
    }

    const totalWidth = Math.max(computeWidth(tree), 200);
    const totalDepth = getDepth(tree);
    const svgHeight = totalDepth * levelHeight + nodeRadius * 2 + 40;
    const svgWidth = totalWidth + 40;

    // ── Step 2: Build SVG markup ──
    let lines = '';   // edge lines (drawn first, behind nodes)
    let nodes = '';   // node circles + text

    /**
     * Recursively position and render each node.
     * @param {Object} node   – current tree node
     * @param {number} x      – x centre of the current subtree
     * @param {number} y      – y centre of this node
     * @param {number} width  – horizontal space allocated to this subtree
     * @param {number} delay  – animation delay (seconds)
     */
    function renderNode(node, x, y, width, delay) {
        if (!node) return;

        const isOperator = ['+', '-', '*', '/'].includes(node.value);
        const fillClass = isOperator ? 'operator-node' : 'operand-node';

        // Draw edges to children
        if (node.left) {
            const leftWidth = computeWidth(node.left);
            const childX = x - width / 2 + leftWidth / 2;
            const childY = y + levelHeight;
            lines += `<line x1="${x}" y1="${y}" x2="${childX}" y2="${childY}"
                        class="tree-edge" style="animation-delay:${delay}s" />`;
            renderNode(node.left, childX, childY, leftWidth, delay + 0.08);
        }

        if (node.right) {
            const leftWidth = computeWidth(node.left);
            const rightWidth = computeWidth(node.right);
            const childX = x - width / 2 + leftWidth + horizontalGap + rightWidth / 2;
            const childY = y + levelHeight;
            lines += `<line x1="${x}" y1="${y}" x2="${childX}" y2="${childY}"
                        class="tree-edge" style="animation-delay:${delay}s" />`;
            renderNode(node.right, childX, childY, rightWidth, delay + 0.08);
        }

        // Draw the node circle and label
        nodes += `
            <g class="tree-node ${fillClass}" style="animation-delay:${delay}s">
                <circle cx="${x}" cy="${y}" r="${nodeRadius}" />
                <text x="${x}" y="${y}" dy="0.35em">${node.value}</text>
            </g>`;
    }

    const startX = svgWidth / 2;
    const startY = nodeRadius + 20;
    renderNode(tree, startX, startY, totalWidth, 0);

    treeContainer.innerHTML = `
        <svg viewBox="0 0 ${svgWidth} ${svgHeight}" width="100%" height="${svgHeight}">
            ${lines}
            ${nodes}
        </svg>`;
}


/**
 * Get the depth (number of levels) of a tree.
 */
function getDepth(node) {
    if (!node) return 0;
    return 1 + Math.max(getDepth(node.left || null), getDepth(node.right || null));
}
