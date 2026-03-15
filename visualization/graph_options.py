"""
Graph Options for RIM Visualization.

Provides PyVis network configuration options.
"""

from typing import Dict, Any


def get_network_options(physics_enabled: bool = True) -> str:
    """
    Get PyVis network options as JSON string.
    
    Args:
        physics_enabled: Whether physics simulation is enabled
    
    Returns:
        JSON options string for PyVis
    """
    physics_str = "true" if physics_enabled else "false"
    
    return f"""
    {{
        "nodes": {{
            "font": {{
                "size": 18,
                "face": "Arial",
                "vadjust": -5
            }},
            "borderWidth": 2,
            "shadow": true,
            "widthConstraint": {{
                "minimum": 50,
                "maximum": 280
            }},
            "scaling": {{
                "min": 30,
                "max": 150,
                "label": {{
                    "enabled": true,
                    "min": 18,
                    "max": 55
                }}
            }}
        }},
        "edges": {{
            "arrows": {{"to": {{"enabled": true, "scaleFactor": 1.0}}}},
            "smooth": {{"type": "curvedCW", "roundness": 0.2}},
            "shadow": true,
            "font": {{"size": 12, "face": "Arial"}}
        }},
        "physics": {{
            "enabled": {physics_str},
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {{
                "gravitationalConstant": -300,
                "centralGravity": 0.01,
                "springLength": 600,
                "springConstant": 0.05
            }},
            "stabilization": {{
                "iterations": 150,
                "fit": true
            }}
        }},
        "interaction": {{
            "hover": true,
            "navigationButtons": true,
            "keyboard": true,
            "dragNodes": true,
            "dragView": true,
            "zoomView": true
        }}
    }}
    """


def get_position_capture_js() -> str:
    """
    Get JavaScript for position capture functionality.
    
    Returns:
        JavaScript and CSS string to inject
    """
    return """
    <style>
        #captureBtn {
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 9999;
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        #captureBtn:hover {
            background-color: #2980b9;
        }
        #positionOutput {
            position: fixed;
            top: 50px;
            right: 10px;
            z-index: 9999;
            width: 300px;
            max-height: 200px;
            overflow-y: auto;
            background: white;
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 10px;
            font-family: monospace;
            font-size: 11px;
            display: none;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        #copyBtn {
            position: fixed;
            top: 10px;
            right: 180px;
            z-index: 9999;
            padding: 10px 20px;
            background-color: #27ae60;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            display: none;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        #copyBtn:hover {
            background-color: #229954;
        }
        #statusMsg {
            position: fixed;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;
            padding: 10px 20px;
            background-color: #27ae60;
            color: white;
            border-radius: 5px;
            font-size: 14px;
            display: none;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
    </style>
    <button id="captureBtn" onclick="capturePositions()">📍 Capture Positions</button>
    <button id="copyBtn" onclick="copyPositions()">📋 Copy to Clipboard</button>
    <div id="positionOutput"></div>
    <div id="statusMsg"></div>
    <script>
        var capturedPositions = null;
        
        function capturePositions() {
            var positions = network.getPositions();
            var result = {};
            
            for (var nodeId in positions) {
                result[nodeId] = {
                    x: Math.round(positions[nodeId].x),
                    y: Math.round(positions[nodeId].y)
                };
            }
            
            capturedPositions = JSON.stringify(result, null, 2);
            
            document.getElementById('positionOutput').innerText = capturedPositions;
            document.getElementById('positionOutput').style.display = 'block';
            document.getElementById('copyBtn').style.display = 'block';
            
            showStatus('✅ Positions captured! Click "Copy to Clipboard"');
        }
        
        function copyPositions() {
            if (capturedPositions) {
                navigator.clipboard.writeText(capturedPositions).then(function() {
                    showStatus('✅ Copied! Paste in the "Position Data" field and click Save');
                }).catch(function(err) {
                    var textarea = document.createElement('textarea');
                    textarea.value = capturedPositions;
                    document.body.appendChild(textarea);
                    textarea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textarea);
                    showStatus('✅ Copied! Paste in the "Position Data" field and click Save');
                });
            }
        }
        
        function showStatus(msg) {
            var statusEl = document.getElementById('statusMsg');
            statusEl.innerText = msg;
            statusEl.style.display = 'block';
            setTimeout(function() {
                statusEl.style.display = 'none';
            }, 4000);
        }
    </script>
    """


def get_fullscreen_js() -> str:
    """
    Get JavaScript for fullscreen functionality.
    
    Returns:
        JavaScript and CSS string to inject
    """
    return """
    <style>
        #fullscreenBtn {
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 9999;
            padding: 10px 18px;
            background-color: #2c3e50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }
        #fullscreenBtn:hover {
            background-color: #34495e;
            transform: scale(1.05);
        }
        
        :fullscreen #mynetwork,
        :-webkit-full-screen #mynetwork,
        :-moz-full-screen #mynetwork,
        :-ms-fullscreen #mynetwork {
            width: 100vw !important;
            height: 100vh !important;
        }
        
        :fullscreen body,
        :-webkit-full-screen body,
        :-moz-full-screen body,
        :-ms-fullscreen body {
            overflow: hidden;
            background: white;
        }
        
        :fullscreen #fullscreenBtn,
        :-webkit-full-screen #fullscreenBtn,
        :-moz-full-screen #fullscreenBtn,
        :-ms-fullscreen #fullscreenBtn {
            position: fixed;
            background-color: #e74c3c;
        }
        
        :fullscreen #fullscreenBtn:hover,
        :-webkit-full-screen #fullscreenBtn:hover,
        :-moz-full-screen #fullscreenBtn:hover,
        :-ms-fullscreen #fullscreenBtn:hover {
            background-color: #c0392b;
        }
        
        #fsHint {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;
            padding: 8px 16px;
            background-color: rgba(0,0,0,0.8);
            color: white;
            border-radius: 5px;
            font-size: 13px;
            display: none;
            pointer-events: none;
        }
        
        :fullscreen #fsHint,
        :-webkit-full-screen #fsHint,
        :-moz-full-screen #fsHint,
        :-ms-fullscreen #fsHint {
            display: block;
        }
    </style>
    <button id="fullscreenBtn" onclick="toggleFullscreen()">⛶ Fullscreen</button>
    <div id="fsHint">Press ESC to exit fullscreen | Use mouse wheel to zoom | Drag to pan</div>
    <script>
        function toggleFullscreen() {
            var elem = document.documentElement;
            var btn = document.getElementById('fullscreenBtn');
            
            if (!document.fullscreenElement && !document.webkitFullscreenElement && 
                !document.mozFullScreenElement && !document.msFullscreenElement) {
                if (elem.requestFullscreen) {
                    elem.requestFullscreen();
                } else if (elem.webkitRequestFullscreen) {
                    elem.webkitRequestFullscreen();
                } else if (elem.mozRequestFullScreen) {
                    elem.mozRequestFullScreen();
                } else if (elem.msRequestFullscreen) {
                    elem.msRequestFullscreen();
                }
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.webkitExitFullscreen) {
                    document.webkitExitFullscreen();
                } else if (document.mozCancelFullScreen) {
                    document.mozCancelFullScreen();
                } else if (document.msExitFullscreen) {
                    document.msExitFullscreen();
                }
            }
        }
        
        function onFullscreenChange() {
            var btn = document.getElementById('fullscreenBtn');
            var isFs = document.fullscreenElement || document.webkitFullscreenElement || 
                       document.mozFullScreenElement || document.msFullscreenElement;
            
            if (isFs) {
                btn.innerHTML = '✕ Exit Fullscreen';
                setTimeout(function() {
                    if (typeof network !== 'undefined' && network) {
                        var width = window.innerWidth;
                        var height = window.innerHeight;
                        network.setSize(width + 'px', height + 'px');
                        network.fit();
                    }
                }, 100);
            } else {
                btn.innerHTML = '⛶ Fullscreen';
                setTimeout(function() {
                    if (typeof network !== 'undefined' && network) {
                        network.setSize('100%', '700px');
                        network.redraw();
                    }
                }, 100);
            }
        }
        
        document.addEventListener('fullscreenchange', onFullscreenChange);
        document.addEventListener('webkitfullscreenchange', onFullscreenChange);
        document.addEventListener('mozfullscreenchange', onFullscreenChange);
        document.addEventListener('MSFullscreenChange', onFullscreenChange);
        
        document.addEventListener('keydown', function(e) {
            if ((e.key === 'f' || e.key === 'F') && 
                !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
                e.preventDefault();
                toggleFullscreen();
            }
        });
    </script>
    """

def get_export_js() -> str:
    """
    Get JavaScript and CSS for the export functionality.
    Includes jspdf library for PDF generation and extracts canvas exactly adjusted to screen resolution.
    
    Returns:
        JavaScript and CSS string to inject
    """
    return """
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <style>
        .export-dropdown {
            position: absolute;
            top: 10px;
            left: 140px;
            z-index: 9999;
            display: inline-block;
        }
        .export-btn {
            padding: 10px 18px;
            background-color: #2ecc71;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }
        .export-btn:hover {
            background-color: #27ae60;
        }
        .export-content {
            display: none;
            position: absolute;
            background-color: #ffffff;
            min-width: 120px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            z-index: 10000;
            border-radius: 5px;
            overflow: hidden;
            margin-top: 5px;
        }
        .export-content a {
            color: #333333;
            padding: 12px 16px;
            text-decoration: none;
            display: block;
            font-family: Arial, sans-serif;
            font-size: 14px;
            cursor: pointer;
        }
        .export-content a:hover {
            background-color: #f1f1f1;
        }
        .export-dropdown:hover .export-content {
            display: block;
        }
    </style>
    <div class="export-dropdown">
        <button class="export-btn">📥 Export</button>
        <div class="export-content">
            <a onclick="exportPNG()">↳ As PNG Image</a>
            <a onclick="exportPDF()">↳ As PDF Document</a>
        </div>
    </div>
    <script>
        function getCanvasDataURL() {
            var srcCanvas = document.querySelector('#mynetwork canvas') || document.querySelector('canvas');
            if(!srcCanvas) return null;
            
            // Create a temporary canvas that precisely matches the display resolution
            var destCanvas = document.createElement('canvas');
            destCanvas.width = srcCanvas.width;
            destCanvas.height = srcCanvas.height;
            var destCtx = destCanvas.getContext('2d');
            
            // Ensure white background so transparency translates properly to export
            destCtx.fillStyle = '#ffffff';
            destCtx.fillRect(0, 0, destCanvas.width, destCanvas.height);
            destCtx.drawImage(srcCanvas, 0, 0);
            
            return {
                dataURL: destCanvas.toDataURL('image/png', 1.0),
                width: srcCanvas.width,
                height: srcCanvas.height
            };
        }

        function exportPNG() {
            var canvasData = getCanvasDataURL();
            if(!canvasData) { alert("Canvas not found!"); return; }
            var a = document.createElement('a');
            a.href = canvasData.dataURL;
            a.download = 'rim_graph_export.png';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }

        function exportPDF() {
            var canvasData = getCanvasDataURL();
            if(!canvasData) { alert("Canvas not found!"); return; }
            
            if(!window.jspdf || !window.jspdf.jsPDF) {
                alert("jsPDF library failed to load");
                return;
            }
            
            var jsPDF = window.jspdf.jsPDF;
            var orientation = canvasData.width > canvasData.height ? 'l' : 'p';
            
            // Create PDF mapped exactly to the high-res canvas pixels (adjusted to screen resolution)
            var pdf = new jsPDF({
                orientation: orientation,
                unit: 'px',
                format: [canvasData.width, canvasData.height]
            });
            
            pdf.addImage(canvasData.dataURL, 'PNG', 0, 0, canvasData.width, canvasData.height);
            pdf.save('rim_graph_export.pdf');
        }
    </script>
    """

def get_focus_mode_js() -> str:
    """
    Get JavaScript and CSS for the interactive focus mode.
    Fades out nodes that are not connected to the clicked node.
    
    Returns:
        JavaScript and CSS string to inject
    """
    return """
    <style>
        .focus-control {
            position: absolute;
            top: 50px;
            left: 10px;
            z-index: 9999;
            background-color: #f8f9fa;
            padding: 8px 12px;
            border-radius: 5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            font-family: Arial, sans-serif;
            font-size: 13px;
            color: #333;
            border: 1px solid #ddd;
            display: flex;
            align-items: center;
        }
        .focus-control input {
            margin-right: 8px;
            cursor: pointer;
        }
        .focus-control label {
            cursor: pointer;
            user-select: none;
        }
    </style>
    <div class="focus-control" title="When checking, clicking a node highlights its entire chain. Unchecked highlights only direct neighbors.">
        <input type="checkbox" id="fullChainToggle">
        <label for="fullChainToggle">Full Chain Focus</label>
    </div>
    <script>
        // Ensure network is ready
        setTimeout(function() {
            if (typeof network === 'undefined' || !network) return;
            
            var originalColors = {};
            var originalNodeOpacities = {};
            var originalEdgeOpacities = {};
            var isFocusModeActive = false;
            
            // Backup original colors and opacities if we haven't
            function backupColors() {
                var nodes = network.body.data.nodes.get();
                var edges = network.body.data.edges.get();
                
                nodes.forEach(function(node) {
                    if (!originalColors[node.id]) {
                        originalColors[node.id] = node.color ? JSON.parse(JSON.stringify(node.color)) : null;
                        originalNodeOpacities[node.id] = node.font ? node.font.color : null;
                    }
                });
                
                edges.forEach(function(edge) {
                    if (!originalColors['edge_' + edge.id]) {
                        originalColors['edge_' + edge.id] = edge.color ? JSON.parse(JSON.stringify(edge.color)) : null;
                    }
                });
            }
            
            // Helper to get rgba string with new alpha
            function setAlpha(colStr, alpha) {
                if (typeof colStr === 'object' && colStr !== null) {
                    // Usually color objects have background, border, highlight etc.
                    var ret = {};
                    for (var k in colStr) {
                        ret[k] = setAlpha(colStr[k], alpha);
                    }
                    return ret;
                }
                
                if (typeof colStr !== 'string') return colStr;
                
                if (colStr.startsWith('rgba')) {
                    return colStr.replace(/rgba\\(([^,]+),([^,]+),([^,]+),[^)]+\\)/, 'rgba($1,$2,$3,' + alpha + ')');
                } else if (colStr.startsWith('#')) {
                    var hex = colStr.replace('#', '');
                    if (hex.length === 3) {
                        hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
                    }
                    var r = parseInt(hex.substring(0, 2), 16);
                    var g = parseInt(hex.substring(2, 4), 16);
                    var b = parseInt(hex.substring(4, 6), 16);
                    return 'rgba(' + r + ',' + g + ',' + b + ',' + alpha + ')';
                }
                // Fallback
                return colStr;
            }
            
            // Get all connected nodes (1-hop)
            function getDirectNeighbors(nodeId) {
                var connected = network.getConnectedNodes(nodeId);
                var set = new Set(connected);
                set.add(nodeId);
                return set;
            }
            
            // Get all reachable nodes (full connected component) - treating edges as undirected for highlighting
            function getFullChain(startNodeId) {
                var edges = network.body.data.edges.get();
                var adj = {};
                
                edges.forEach(function(e) {
                    if (!adj[e.from]) adj[e.from] = [];
                    if (!adj[e.to]) adj[e.to] = [];
                    adj[e.from].push(e.to);
                    adj[e.to].push(e.from);
                });
                
                var visited = new Set();
                var queue = [startNodeId];
                visited.add(startNodeId);
                
                while (queue.length > 0) {
                    var cur = queue.shift();
                    var neighbors = adj[cur] || [];
                    neighbors.forEach(function(n) {
                        if (!visited.has(n)) {
                            visited.add(n);
                            queue.push(n);
                        }
                    });
                }
                
                return visited;
            }
            
            function applyFocusMode(selectedNodeId) {
                backupColors();
                isFocusModeActive = true;
                var isFullChain = document.getElementById('fullChainToggle').checked;
                
                var keepNodes = isFullChain ? getFullChain(selectedNodeId) : getDirectNeighbors(selectedNodeId);
                
                var nodesToUpdate = [];
                var edgesToUpdate = [];
                
                var allNodes = network.body.data.nodes.get();
                var allEdges = network.body.data.edges.get();
                
                // Fade nodes
                allNodes.forEach(function(node) {
                    var origCol = originalColors[node.id];
                    var origFontCol = originalNodeOpacities[node.id] || '#333333';
                    
                    if (keepNodes.has(node.id)) {
                        nodesToUpdate.push({
                            id: node.id,
                            color: origCol,
                            font: { color: origFontCol }
                        });
                    } else {
                        nodesToUpdate.push({
                            id: node.id,
                            color: setAlpha(origCol, 0.1),
                            font: { color: setAlpha(origFontCol, 0.1) }
                        });
                    }
                });
                
                // Fade edges
                allEdges.forEach(function(edge) {
                    var origCol = originalColors['edge_' + edge.id];
                    
                    if (keepNodes.has(edge.from) && keepNodes.has(edge.to)) {
                        edgesToUpdate.push({
                            id: edge.id,
                            color: origCol
                        });
                    } else {
                        edgesToUpdate.push({
                            id: edge.id,
                            color: setAlpha(origCol, 0.1)
                        });
                    }
                });
                
                network.body.data.nodes.update(nodesToUpdate);
                network.body.data.edges.update(edgesToUpdate);
            }
            
            function resetFocusMode() {
                if (!isFocusModeActive) return;
                
                var nodesToUpdate = [];
                var edgesToUpdate = [];
                
                var allNodes = network.body.data.nodes.get();
                var allEdges = network.body.data.edges.get();
                
                allNodes.forEach(function(node) {
                    if (originalColors[node.id]) {
                        nodesToUpdate.push({
                            id: node.id,
                            color: originalColors[node.id],
                            font: { color: originalNodeOpacities[node.id] || '#333333' }
                        });
                    }
                });
                
                allEdges.forEach(function(edge) {
                    if (originalColors['edge_' + edge.id]) {
                        edgesToUpdate.push({
                            id: edge.id,
                            color: originalColors['edge_' + edge.id]
                        });
                    }
                });
                
                network.body.data.nodes.update(nodesToUpdate);
                network.body.data.edges.update(edgesToUpdate);
                isFocusModeActive = false;
            }
            
            network.on("click", function (params) {
                if (params.nodes.length > 0) {
                    var clickedNodeId = params.nodes[0];
                    applyFocusMode(clickedNodeId);
                } else {
                    resetFocusMode();
                }
            });
            
            // Allow re-evaluating focus if toggle is clicked while a node is selected
            document.getElementById('fullChainToggle').addEventListener('change', function() {
                if (isFocusModeActive) {
                    var selectedNodes = network.getSelectedNodes();
                    if (selectedNodes && selectedNodes.length > 0) {
                        applyFocusMode(selectedNodes[0]);
                    }
                }
            });
            
        }, 1000);
    </script>
    """


def get_node_click_postmessage_js() -> str:
    """
    Inject a click handler that posts the clicked node ID to the parent frame.

    When the PyVis graph is embedded inside the graph_click_bridge declare_component
    (as an inner srcdoc iframe), window.parent is the outer component iframe.
    That outer iframe catches this message and forwards it to Streamlit via
    Streamlit.setComponentValue(), closing the JS → Python communication loop.

    The setTimeout delay (1100 ms) is intentionally slightly longer than the
    1000 ms used by get_focus_mode_js() so that both network.on("click") handlers
    register in the correct order without conflict.
    """
    return """
    <script>
    setTimeout(function() {
        if (typeof network !== 'undefined') {
            network.on("click", function(params) {
                if (params.nodes.length > 0) {
                    window.parent.postMessage(
                        {type: "node_selected", node_id: params.nodes[0]}, "*"
                    );
                } else {
                    window.parent.postMessage(
                        {type: "node_selected", node_id: null}, "*"
                    );
                }
            });
        }
    }, 1100);
    </script>
    """
