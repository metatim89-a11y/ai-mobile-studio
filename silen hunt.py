body {
        font-family: 'Source Sans Pro', sans-serif;
        background-color: #0E1117;
        color: #FAFAFA;
    }

    .st-card {
        background-color: #262730;
        border: 1px solid #41444e;
        border-radius: 0.5rem;
    }

    .st-input {
        background-color: #0E1117;
        border: 1px solid #41444e;
        color: white;
        transition: border-color 0.2s;
    }
    .st-input:focus {
        outline: none;
        border-color: #FF4B4B;
    }

    .st-btn-primary {
        background-color: #FF4B4B;
        color: white;
        transition: background-color 0.2s;
    }
    .st-btn-primary:hover {
        background-color: #FF2B2B;
    }

    .st-btn-secondary {
        background-color: transparent;
        border: 1px solid #41444e;
        color: white;
        transition: background-color 0.2s;
    }
    .st-btn-secondary:hover {
        border-color: #FF4B4B;
        color: #FF4B4B;
    }

    .tab-active {
        border-bottom: 2px solid #FF4B4B;
        color: white;
    }
    .tab-inactive {
        color: #8c8c8c;
        border-bottom: 2px solid transparent;
    }
    .tab-inactive:hover {
        color: #FF4B4B;
        cursor: pointer;
    }

    /* Chart Container Styling */
    .chart-container {
        position: relative;
        width: 100%;
        max-width: 100%;
        height: 300px;
        margin: 0 auto;
    }

    /* Scrollbar styling for tables */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0E1117; 
    }
    ::-webkit-scrollbar-thumb {
        background: #41444e; 
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #555; 
    }
</style>
</head> <body class="min-h-screen flex flex-col p-4 md:p-8">

<!-- Header Section -->
<header class="mb-8">
    <h1 class="text-3xl md:text-4xl font-bold mb-2">📦 Logistics Intelligence Box</h1>
    <p class="text-gray-400 max-w-3xl">
        This interactive dashboard simulates the <strong>Persistent Scraper Engine</strong>. 
        It monitors incoming messages for keywords defined in your Universal Watchlist and logs potential leads automatically.
        Engage the autopilot to simulate the background hunting process.
    </p>
</header>

<!-- Autopilot Control Panel -->
<section class="st-card p-6 mb-8">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
        
        <!-- Status Indicator -->
        <div class="flex flex-col">
            <span class="text-sm text-gray-400 font-semibold uppercase tracking-wider mb-1">System Status</span>
            <div class="flex items-center gap-2">
                <span id="status-icon" class="text-2xl">⚪</span>
                <span id="status-text" class="text-xl font-bold text-gray-300">IDLE</span>
            </div>
        </div>

        <!-- Frequency Selector -->
        <div class="flex flex-col">
            <label class="text-sm text-gray-400 font-semibold uppercase tracking-wider mb-1">Scan Frequency</label>
            <div class="flex gap-2">
                <select id="frequency-select" class="st-input w-full p-2 rounded">
                    <option value="2 min">2 min</option>
                    <option value="5 min">5 min</option>
                    <option value="10 min">10 min</option>
                    <option value="30 min">30 min</option>
                    <option value="1 hour" selected>1 hour</option>
                    <option value="2 hours">2 hours</option>
                    <option value="4 hours">4 hours</option>
                    <option value="8 hours">8 hours</option>
                    <option value="12 hours">12 hours</option>
                    <option value="24 hours">24 hours</option>
                    <option value="28 hours">28 hours</option>
                </select>
                <button onclick="updateFrequency()" class="st-btn-secondary px-3 rounded" title="Update Frequency">↻</button>
            </div>
        </div>

        <!-- Action Button -->
        <div class="flex flex-col justify-end h-full">
            <button id="toggle-btn" onclick="toggleAutopilot()" class="st-btn-primary py-3 px-6 rounded text-lg font-bold shadow-lg">
                🚀 ENGAGE AUTOPILOT
            </button>
        </div>
    </div>
</section>

<!-- Navigation Tabs -->
<nav class="flex gap-8 border-b border-[#41444e] mb-6 text-lg font-semibold">
    <div onclick="switchTab('overview')" id="tab-overview" class="tab-active pb-2 cursor-pointer">📊 Overview</div>
    <div onclick="switchTab('database')" id="tab-database" class="tab-inactive pb-2 cursor-pointer">📚 Lead Database</div>
    <div onclick="switchTab('watchlist')" id="tab-watchlist" class="tab-inactive pb-2 cursor-pointer">🎯 Universal Watchlist</div>
    <div onclick="switchTab('auth')" id="tab-auth" class="tab-inactive pb-2 cursor-pointer">🔑 Session Auth</div>
</nav>

<!-- Content Area -->
<main class="flex-grow">
    
    <!-- Tab: Overview (Visualizations) -->
    <div id="content-overview" class="block animate-fade-in">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Line Chart: Activity -->
            <div class="st-card p-4">
                <h3 class="text-lg font-bold mb-4">📈 Leads Detected Over Time</h3>
                <div class="chart-container">
                    <canvas id="leadsLineChart"></canvas>
                </div>
            </div>

            <!-- Doughnut Chart: Keywords -->
            <div class="st-card p-4">
                <h3 class="text-lg font-bold mb-4">🎯 Keyword Distribution</h3>
                <div class="chart-container">
                    <canvas id="keywordsDoughnutChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Quick Stats Row -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
            <div class="st-card p-4 text-center">
                <h4 class="text-gray-400 text-sm uppercase">Total Leads Found</h4>
                <p id="stat-total-leads" class="text-4xl font-bold text-[#FF4B4B] mt-2">0</p>
            </div>
            <div class="st-card p-4 text-center">
                <h4 class="text-gray-400 text-sm uppercase">Active Keywords</h4>
                <p id="stat-active-keywords" class="text-4xl font-bold text-white mt-2">4</p>
            </div>
            <div class="st-card p-4 text-center">
                <h4 class="text-gray-400 text-sm uppercase">Last Scan</h4>
                <p id="stat-last-scan" class="text-xl font-bold text-gray-300 mt-4">Never</p>
            </div>
        </div>
    </div>

    <!-- Tab: Database (Table) -->
    <div id="content-database" class="hidden">
        <div class="flex justify-between items-center mb-4">
            <input type="text" id="table-search" onkeyup="filterTable()" placeholder="Filter by name or content..." class="st-input p-2 rounded w-1/2 md:w-1/3">
            <button onclick="downloadCSV()" class="st-btn-secondary px-4 py-2 rounded flex items-center gap-2">
                📥 Export CSV
            </button>
        </div>
        <div class="st-card overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-[#31333F] text-gray-300 border-b border-[#41444e]">
                            <th class="p-4 font-semibold">ID</th>
                            <th class="p-4 font-semibold">Time Scanned</th>
                            <th class="p-4 font-semibold">User Profile</th>
                            <th class="p-4 font-semibold">Keyword</th>
                            <th class="p-4 font-semibold">Message Preview</th>
                        </tr>
                    </thead>
                    <tbody id="leads-table-body" class="text-sm">
                        <!-- JS will populate rows here -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Tab: Watchlist (Config) -->
    <div id="content-watchlist" class="hidden">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <!-- Add New Word -->
            <div class="st-card p-6 h-fit">
                <h3 class="text-lg font-bold mb-4">Add Tracking Keyword</h3>
                <p class="text-gray-400 text-sm mb-4">Enter a word or phrase (e.g., "cord", "delivery", "oak"). The scraper uses Regex to find case-insensitive matches.</p>
                <div class="flex flex-col gap-3">
                    <input type="text" id="new-word-input" class="st-input p-3 rounded" placeholder="Type keyword...">
                    <button onclick="addKeyword()" class="st-btn-primary p-2 rounded font-semibold">Add to Watchlist</button>
                </div>
            </div>

            <!-- List of Words -->
            <div class="col-span-1 md:col-span-2 st-card p-6">
                <h3 class="text-lg font-bold mb-4">Active Watchlist</h3>
                <div id="watchlist-container" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <!-- Keywords populated by JS -->
                </div>
            </div>
        </div>
    </div>

    <!-- Tab: Auth -->
    <div id="content-auth" class="hidden">
        <div class="st-card p-6 max-w-2xl mx-auto">
            <h3 class="text-lg font-bold mb-4">Browser Session Management</h3>
            <div class="bg-yellow-900/30 border border-yellow-700/50 p-4 rounded mb-4">
                <p class="text-yellow-200 text-sm">⚠️ Playwright requires a valid <code>fb_auth.json</code> file to bypass login screens. Paste your cookie string below.</p>
            </div>
            <label class="block text-sm text-gray-400 mb-2">Cookie String</label>
            <textarea id="cookie-input" class="st-input w-full rounded p-3 text-xs font-mono mb-4 h-32" placeholder="c_user=123456; xs=..."></textarea>
            <button onclick="updateAuth()" class="st-btn-primary px-6 py-2 rounded w-full">Update Auth Session</button>
        </div>
    </div>

</main>

<!-- JavaScript Logic -->
<script>
    // --- State Management ---
    const state = {
        active: false,
        frequency: '1 hour',
        keywords: ['firewood', 'delivery', 'cord', 'oak'],
        leads: [
            { id: 101, user: "Mike T.", keyword: "firewood", message: "Do you have seasoned firewood available?", time: "2023-10-27 09:30:00" },
            { id: 102, user: "Sarah J.", keyword: "delivery", message: "How much is delivery to downtown?", time: "2023-10-27 10:15:22" },
            { id: 103, user: "Construction Co.", keyword: "cord", message: "Need 5 cords of mixed hardwood.", time: "2023-10-27 11:05:10" }
        ],
        lastScan: null,
        intervalId: null
    };

    // --- Charts Initialization ---
    let lineChart, doughnutChart;

    function initCharts() {
        // Line Chart
        const ctxLine = document.getElementById('leadsLineChart').getContext('2d');
        lineChart = new Chart(ctxLine, {
            type: 'line',
            data: {
                labels: ['09:00', '10:00', '11:00', '12:00', '13:00'],
                datasets: [{
                    label: 'Leads Found',
                    data: [1, 2, 4, 4, 4], // Initial mock data
                    borderColor: '#FF4B4B',
                    backgroundColor: 'rgba(255, 75, 75, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    y: { 
                        beginAtZero: true, 
                        grid: { color: '#41444e' },
                        ticks: { color: '#9ca3af', stepSize: 1 }
                    },
                    x: { 
                        grid: { display: false },
                        ticks: { color: '#9ca3af' }
                    }
                }
            }
        });

        // Doughnut Chart
        const ctxDoughnut = document.getElementById('keywordsDoughnutChart').getContext('2d');
        doughnutChart = new Chart(ctxDoughnut, {
            type: 'doughnut',
            data: {
                labels: state.keywords,
                datasets: [{
                    data: [1, 1, 1, 0], // Matches mock data counts
                    backgroundColor: ['#FF4B4B', '#FFA420', '#00C896', '#3D9DF3'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right', labels: { color: '#fff' } }
                },
                cutout: '70%'
            }
        });
    }

    // --- Core Functions ---

    function toggleAutopilot() {
        state.active = !state.active;
        const btn = document.getElementById('toggle-btn');
        const statusIcon = document.getElementById('status-icon');
        const statusText = document.getElementById('status-text');

        if (state.active) {
            // Engage
            btn.innerText = "🛑 DISENGAGE";
            btn.className = "st-btn-secondary py-3 px-6 rounded text-lg font-bold shadow-lg border-red-500 text-red-500 hover:bg-red-900/20";
            statusIcon.innerText = "🟢";
            statusText.innerText = "ACTIVE";
            statusText.className = "text-xl font-bold text-[#00C896]";
            
            // Start Simulation Loop (Rapid for demo purposes, unrelated to real frequency)
            state.intervalId = setInterval(simulateScan, 3000); 
            simulateScan(); // Run immediate
        } else {
            // Disengage
            btn.innerText = "🚀 ENGAGE AUTOPILOT";
            btn.className = "st-btn-primary py-3 px-6 rounded text-lg font-bold shadow-lg";
            statusIcon.innerText = "⚪";
            statusText.innerText = "IDLE";
            statusText.className = "text-xl font-bold text-gray-300";
            
            clearInterval(state.intervalId);
        }
    }

    function updateFrequency() {
        const select = document.getElementById('frequency-select');
        state.frequency = select.value;
        alert(`System updated. Scans will run every ${state.frequency}.`);
    }

    function simulateScan() {
        // 1. Pick a random keyword from watchlist
        if (state.keywords.length === 0) return;
        const keyword = state.keywords[Math.floor(Math.random() * state.keywords.length)];
        
        // 2. Generate Mock Lead
        const names = ["Local Landscaper", "Homeowner 42", "BBQ Pitmaster", "Campground Owner", "Winter Prep"];
        const msgs = [
            `Looking for prices on a cord of ${keyword}.`,
            `Do you have ${keyword} ready for delivery?`,
            `Need ${keyword} delivered to North End.`,
            `Is the ${keyword} seasoned or green?`
        ];
        
        const newLead = {
            id: state.leads.length + 101,
            user: names[Math.floor(Math.random() * names.length)],
            keyword: keyword,
            message: msgs[Math.floor(Math.random() * msgs.length)],
            time: new Date().toLocaleString()
        };

        // 3. Update State
        state.leads.unshift(newLead); // Add to top
        state.lastScan = new Date().toLocaleTimeString();

        // 4. Update UI
        updateStats();
        renderTable();
        updateCharts();
    }

    function updateStats() {
        document.getElementById('stat-total-leads').innerText = state.leads.length;
        document.getElementById('stat-active-keywords').innerText = state.keywords.length;
        document.getElementById('stat-last-scan').innerText = state.lastScan || "Just now";
    }

    function renderTable() {
        const tbody = document.getElementById('leads-table-body');
        const filter = document.getElementById('table-search').value.toLowerCase();
        
        tbody.innerHTML = ''; // Clear

        state.leads.forEach(lead => {
            if (lead.user.toLowerCase().includes(filter) || lead.message.toLowerCase().includes(filter)) {
                const tr = document.createElement('tr');
                tr.className = "border-b border-[#41444e] hover:bg-[#31333F] transition-colors";
                tr.innerHTML = `
                    <td class="p-4 font-mono text-gray-400">#${lead.id}</td>
                    <td class="p-4 text-gray-300">${lead.time}</td>
                    <td class="p-4 font-bold text-white">${lead.user}</td>
                    <td class="p-4"><span class="bg-[#FF4B4B]/20 text-[#FF4B4B] px-2 py-1 rounded text-xs uppercase font-bold tracking-wide">${lead.keyword}</span></td>
                    <td class="p-4 text-gray-300 italic truncate max-w-xs">${lead.message}</td>
                `;
                tbody.appendChild(tr);
            }
        });
    }

    function filterTable() {
        renderTable();
    }

    function renderWatchlist() {
        const container = document.getElementById('watchlist-container');
        container.innerHTML = '';
        
        state.keywords.forEach((word, index) => {
            const div = document.createElement('div');
            div.className = "flex justify-between items-center bg-[#0E1117] border border-[#41444e] p-3 rounded hover:border-[#FF4B4B] transition-colors";
            div.innerHTML = `
                <div class="flex items-center gap-2">
                    <span class="text-xl">🔍</span>
                    <span class="font-semibold text-lg">${word}</span>
                </div>
                <button onclick="removeKeyword(${index})" class="text-gray-500 hover:text-red-500 transition-colors">🗑️</button>
            `;
            container.appendChild(div);
        });
        document.getElementById('stat-active-keywords').innerText = state.keywords.length;
        updateCharts(); // Update charts when keywords change
    }

    function addKeyword() {
        const input = document.getElementById('new-word-input');
        const word = input.value.trim();
        if (word && !state.keywords.includes(word)) {
            state.keywords.push(word);
            input.value = '';
            renderWatchlist();
        } else if (state.keywords.includes(word)) {
            alert("Word already in watchlist!");
        }
    }

    function removeKeyword(index) {
        state.keywords.splice(index, 1);
        renderWatchlist();
    }

    function updateCharts() {
        // Update Line Chart (Simple increment logic for demo)
        if (lineChart) {
            const data = lineChart.data.datasets[0].data;
            // Just keeping the last 5 data points visual
            const currentVal = data[data.length - 1];
            data.push(currentVal + 1); // Mock increment
            if (data.length > 10) data.shift(); // Keep it moving
            lineChart.data.labels.push(new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}));
            if (lineChart.data.labels.length > 10) lineChart.data.labels.shift();
            lineChart.update();
        }

        // Update Doughnut Chart (Recalculate distribution)
        if (doughnutChart) {
            const counts = state.keywords.map(k => state.leads.filter(l => l.keyword === k).length);
            doughnutChart.data.labels = state.keywords;
            doughnutChart.data.datasets[0].data = counts;
            // Generate colors dynamically if needed
            doughnutChart.update();
        }
    }

    // --- Tab Logic ---
    function switchTab(tabId) {
        // Hide all content
        ['overview', 'database', 'watchlist', 'auth'].forEach(id => {
            document.getElementById(`content-${id}`).classList.add('hidden');
            document.getElementById(`tab-${id}`).className = 'tab-inactive pb-2 cursor-pointer';
        });

        // Show selected
        document.getElementById(`content-${tabId}`).classList.remove('hidden');
        document.getElementById(`tab-${tabId}`).className = 'tab-active pb-2 cursor-pointer';
    }

    function downloadCSV() {
        const headers = ["ID,Time,User,Keyword,Message"];
        const rows = state.leads.map(l => `${l.id},"${l.time}","${l.user}","${l.keyword}","${l.message}"`);
        const csvContent = "data:text/csv;charset=utf-8," + headers.concat(rows).join("\n");
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "leads_export.csv");
        document.body.appendChild(link);
        link.click();
    }

    function updateAuth() {
        const val = document.getElementById('cookie-input').value;
        if (val.length > 10) {
            alert("Auth Updated Successfully! (Simulation)");
            document.getElementById('cookie-input').value = '';
        } else {
            alert("Please enter a valid cookie string.");
        }
    }

    // --- Init ---
    window.onload = function() {
        renderTable();
        renderWatchlist();
        initCharts();
        updateStats();
    };

</script>
</body> </html>