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
                "multi": "html",
                "bold": {{"color": "#333333", "size": 18}},
                "vadjust": -5
            }},
            "borderWidth": 2,
            "shadow": true,
            "widthConstraint": {{
                "minimum": 50,
                "maximum": 180
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
                "gravitationalConstant": -150,
                "centralGravity": 0.01,
                "springLength": 300,
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
