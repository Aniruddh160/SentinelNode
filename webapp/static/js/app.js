// ===============================
// 🔹 INDEX LOCAL FOLDER
// ===============================
document.getElementById("indexFolderBtn").addEventListener("click", async () => {
    const path = document.getElementById("folderPath").value;

    if (!path) {
        alert("Please enter folder path");
        return;
    }

    try {
        const res = await fetch("/index-folder", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ path })
        });

        const data = await res.json();
        alert(data.status || "Indexed");

        // Load graph after indexing
        await loadGraph();

    } catch (err) {
        console.error("Index error:", err);
        alert("Error indexing folder");
    }
});


// ===============================
// 🔹 CLONE + INDEX GITHUB REPO
// ===============================
document.getElementById("cloneRepoBtn").addEventListener("click", async () => {
    const repoUrl = document.getElementById("repoUrl").value;

    if (!repoUrl) {
        alert("Please enter a GitHub URL");
        return;
    }

    try {
        const res = await fetch("/clone-repo", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ repo_url: repoUrl })
        });

        const data = await res.json();
        alert(data.message || data.status);

        // Load graph after repo indexing
        await loadGraph();

    } catch (err) {
        console.error("Clone error:", err);
        alert("Error cloning repo");
    }
});


// ===============================
// 🔹 ASK QUESTION (RAG)
// ===============================
async function askQuestion() {
    const question = document.getElementById("queryInput").value;

    if (!question) return;

    try {
        const res = await fetch("/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question })
        });

        const data = await res.json();

        document.getElementById("answerBox").innerHTML =
            formatResponse(data.answer || "No response");

    } catch (err) {
        console.error("Query error:", err);
        alert("Error querying model");
    }
}


// ===============================
// 🔹 LOAD GRAPH FROM BACKEND
// ===============================
async function loadGraph() {
    try {
        const res = await fetch("/get-graph");
        const graph = await res.json();

        console.log("GRAPH DATA:", graph);

        renderGraph(graph);

    } catch (err) {
        console.error("Graph load error:", err);
    }
}


// ===============================
// 🔹 RENDER GRAPH (Vis.js)
// ===============================
function renderGraph(graph) {
    const container = document.getElementById("graphContainer");

    if (!container) {
        console.error("Graph container not found");
        return;
    }

    container.innerHTML = "";

    // Handle empty graph
    if (!graph.nodes || graph.nodes.length === 0) {
        container.innerHTML = "<p class='text-gray-400 p-4'>No graph data available</p>";
        return;
    }

    const uniqueNodes = [...new Set(graph.nodes.map(n => n.id))];

    const nodes = new vis.DataSet(
        uniqueNodes.map(id => ({
            id: id,
            label: id
        }))
    );

    const edges = new vis.DataSet(
        (graph.edges || []).map(e => ({
            from: e.source,
            to: e.target
        }))
    );

    const data = { nodes, edges };

    const options = {
        nodes: {
            shape: "dot",
            size: 18,
            font: {
                size: 14,
                color: "#ffffff"
            },
            color: {
                background: "#3b82f6",
                border: "#1d4ed8"
            }
        },
        edges: {
            color: "#9ca3af",
            width: 2,
            smooth: true
        },
        physics: {
            enabled: true,
            stabilization: false
        },
        interaction: {
            hover: true,
            zoomView: true,
            dragView: true
        }
    };

    new vis.Network(container, data, options);
}


// ===============================
// 🔹 FORMAT RESPONSE (CODE BLOCKS)
// ===============================
function formatResponse(text) {
    if (!text) return "";

    text = text.replace(/'''/g, "```");

    const codeBlockRegex = /```([\s\S]*?)```/g;

    let formatted = "";
    let lastIndex = 0;
    let match;

    while ((match = codeBlockRegex.exec(text)) !== null) {
        const normalText = text.substring(lastIndex, match.index);

        formatted += `<div class="mb-2">${formatText(normalText)}</div>`;

        formatted += `
            <div class="bg-black p-3 rounded mb-2 overflow-x-auto">
                <pre><code>${escapeHtml(match[1].trim())}</code></pre>
            </div>
        `;

        lastIndex = codeBlockRegex.lastIndex;
    }

    const remaining = text.substring(lastIndex);
    formatted += `<div>${formatText(remaining)}</div>`;

    return formatted;
}


// ===============================
// 🔹 HELPERS
// ===============================
function formatText(text) {
    return text.replace(/\n/g, "<br>").trim();
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}


// ===============================
// 🔹 AUTO LOAD GRAPH ON PAGE LOAD
// ===============================
window.onload = () => {
    loadGraph();
};

