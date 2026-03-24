// Chart instances
let tempHumChart = null;
let aqiPhChart = null;
let currentLocation = 'Global';
let fetchInterval = null;

// Frontend history state for charts
const MAX_HISTORY = 20;
let historyData = {
    timestamps: [],
    temperature: [],
    humidity: [],
    aqi: [],
    ph: []
};

// Initialization
document.addEventListener("DOMContentLoaded", () => {
    initCharts();
    setupEventListeners();
    fetchData(); // Initial fetch

    // Start global polling
    startPolling();
});

function startPolling() {
    if (fetchInterval) clearInterval(fetchInterval);
    fetchInterval = setInterval(fetchData, 3000);
}

function stopPolling() {
    if (fetchInterval) clearInterval(fetchInterval);
}

function setupEventListeners() {
    const btn = document.getElementById('search-btn');
    const input = document.getElementById('location-input');

    btn.addEventListener('click', () => {
        changeLocation(input.value);
    });

    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') changeLocation(input.value);
    });
}

function changeLocation(newLocation) {
    if (!newLocation.trim()) return;
    currentLocation = newLocation.trim();

    if (currentLocation.toLowerCase() === 'global') {
        startPolling();
    } else {
        stopPolling(); // Pause refresh for specific location search
    }

    document.getElementById('page-title').textContent = `Fetching data for ${currentLocation}...`;

    // Clear history to avoid weird line connecting old location to new location
    historyData = {
        timestamps: [],
        temperature: [],
        humidity: [],
        aqi: [],
        ph: []
    };

    tempHumChart.data.labels = [];
    tempHumChart.data.datasets.forEach(ds => ds.data = []);
    tempHumChart.update();

    aqiPhChart.data.labels = [];
    aqiPhChart.data.datasets.forEach(ds => ds.data = []);
    aqiPhChart.update();

    fetchData(); // Fetch new location immediately
}

function initCharts() {
    // Chart defaults for light theme
    Chart.defaults.color = '#656d76';
    Chart.defaults.borderColor = 'rgba(31, 35, 40, 0.1)';

    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 500,
            easing: 'easeOutQuart'
        },
        plugins: {
            legend: {
                position: 'top',
                labels: { font: { family: 'Inter', weight: 600 } }
            }
        },
        scales: {
            x: {
                grid: { display: false }
            }
        }
    };

    // Temp & Hum Chart
    const ctxTempHum = document.getElementById('tempHumChart').getContext('2d');
    tempHumChart = new Chart(ctxTempHum, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: [],
                    borderColor: '#f0883e',
                    backgroundColor: 'rgba(240, 136, 62, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Humidity (%)',
                    data: [],
                    borderColor: '#58a6ff',
                    backgroundColor: 'rgba(88, 166, 255, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: commonOptions
    });

    // AQI & pH Chart
    const ctxAqiPh = document.getElementById('aqiPhChart').getContext('2d');
    aqiPhChart = new Chart(ctxAqiPh, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'AQI',
                    data: [],
                    borderColor: '#d29922',
                    backgroundColor: 'rgba(210, 153, 34, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    yAxisID: 'y'
                },
                {
                    label: 'pH Level',
                    data: [],
                    borderColor: '#a371f7',
                    backgroundColor: 'rgba(163, 113, 247, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });
}

async function fetchData() {
    try {
        const url = `/api/data?location=${encodeURIComponent(currentLocation)}`;
        const response = await fetch(url);
        const data = await response.json();

        // Update title based on backend resolution
        let titleSuffix = data.location_name;
        if (data.is_random) {
            titleSuffix = `Global Cycle: ${data.location_name}`;
        }
        document.getElementById('page-title').textContent = `Environmental Monitoring - ${titleSuffix}`;

        updateCards(data.current, data.status);
        updateAlerts(data.alerts);

        // Update history data on the frontend
        const now = new Date();
        const timeString = now.getHours().toString().padStart(2, '0') + ':' +
            now.getMinutes().toString().padStart(2, '0') + ':' +
            now.getSeconds().toString().padStart(2, '0');

        historyData.timestamps.push(timeString);
        historyData.temperature.push(data.current.temperature);
        historyData.humidity.push(data.current.humidity);
        historyData.aqi.push(data.current.aqi);
        historyData.ph.push(data.current.ph);

        if (historyData.timestamps.length > MAX_HISTORY) {
            historyData.timestamps.shift();
            historyData.temperature.shift();
            historyData.humidity.shift();
            historyData.aqi.shift();
            historyData.ph.shift();
        }

        updateCharts(historyData);

    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

function updateCards(current, status) {
    const parameters = ['temperature', 'humidity', 'aqi', 'ph'];

    parameters.forEach(param => {
        // Update values
        document.getElementById(`val-${param}`).textContent = current[param];

        // Update badge text and class
        const badge = document.getElementById(`badge-${param}`);
        badge.textContent = status[param].toUpperCase();
        badge.className = `status-badge ${status[param]}`;

        // Update card border class
        const card = document.getElementById(`card-${param}`);
        card.className = `card border-${status[param]}`;
    });
}

function updateAlerts(alerts) {
    const container = document.getElementById('alerts-container');
    container.innerHTML = ''; // Clear current alerts

    alerts.forEach(alertText => {
        const div = document.createElement('div');

        if (alertText.includes('CRITICAL')) {
            div.className = 'alert-item danger';
        } else if (alertText.includes('WARNING')) {
            div.className = 'alert-item warning';
        } else {
            div.className = 'alert-item safe';
        }

        div.innerHTML = `<span>${alertText}</span>`;
        container.appendChild(div);
    });
}

function updateCharts(history) {
    // Update Temp/Hum Chart
    tempHumChart.data.labels = [...history.timestamps];
    tempHumChart.data.datasets[0].data = [...history.temperature];
    tempHumChart.data.datasets[1].data = [...history.humidity];
    tempHumChart.update('none'); // Update without animation to prevent choppiness

    // Update AQI/pH Chart
    aqiPhChart.data.labels = [...history.timestamps];
    aqiPhChart.data.datasets[0].data = [...history.aqi];
    aqiPhChart.data.datasets[1].data = [...history.ph];
    aqiPhChart.update('none');
}
