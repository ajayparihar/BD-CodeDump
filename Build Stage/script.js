let buildCounter = 1;

function addNewBuild() {
    const buildName = prompt('Enter build name:', `Build${buildCounter}`);
    if (!buildName) return;
    
    const container = document.createElement('div');
    container.className = 'container';
    
    const title = document.createElement('div');
    title.className = 'build-title';
    title.innerHTML = `
        <button class="remove-btn" onclick="removeBuild(this)">×</button>
        <span class="build-name" onclick="renameBuild(this)">${buildName}</span>
    `;
    container.appendChild(title);
    
    const stats = document.createElement('div');
    stats.className = 'stats';
    stats.innerHTML = `
        <p>Current Stage: 
            <select class="stageSelect" onchange="updateProgress(this)">
                <option value="">Select Stage</option>
            </select>
        </p>
        <p>Remaining Time: <span class="remainingTime">0:00</span></p>
        <p>Progress: <span class="progressPercent">0%</span></p>
        <div class="progress-container">
            <div class="progress-bar" style="width: 0%"></div>
        </div>
    `;
    container.appendChild(stats);
    
    document.querySelector('.main-container').appendChild(container);
    
    fetchAndProcessCSV(container);
    
    buildCounter++;
}

async function fetchAndProcessCSV(container = document) {
    try {
        const response = await fetch('Build_data.csv');
        const csv = await response.text();
        processCSV(csv, container);
    } catch (error) {
        console.error('Error loading CSV:', error);
    }
}

function filterStages(select) {
    const searchTerm = select.value.toLowerCase();
    const options = Array.from(select.options);
    
    options.forEach(option => {
        if (option.value === "") return; // Skip the "Select Stage" option
        const stageName = option.text.toLowerCase();
        option.style.display = stageName.includes(searchTerm) ? '' : 'none';
    });
}

function processCSV(csv, container = document) {
    const lines = csv.split('\n');
    const allStages = [];
    let totalSeconds = 0;
    
    lines.forEach(line => {
        const columns = line.split(',');
        if (columns.length > 1) {
            const stageName = columns[0].trim();
            const timeValues = columns.slice(1).map(value => {
                const [minutes, seconds] = value.split('.').map(Number);
                return minutes * 60 + (seconds || 0);
            });
            
            const averageTime = timeValues.reduce((sum, time) => sum + time, 0) / timeValues.length;
            
            allStages.push({
                name: stageName,
                time: averageTime
            });
            totalSeconds += averageTime;
        }
    });
    
    const select = container.querySelector('.stageSelect');
    select.innerHTML = '<option value="">Select Stage</option>';
    allStages.forEach((stage, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.text = stage.name;
        option.dataset.time = stage.time;
        select.appendChild(option);
    });
}

function updateProgress(select) {
    const container = select.closest('.container');
    const selectedIndex = select.value;
    const allStages = Array.from(select.options)
        .slice(1)
        .map(option => ({ time: Number(option.dataset.time) }));
    const totalSeconds = allStages.reduce((sum, stage) => sum + stage.time, 0);
    
    if (container.interval) {
        clearInterval(container.interval);
    }
    
    if (selectedIndex === "") {
        container.querySelector('.remainingTime').textContent = formatTime(totalSeconds);
        container.querySelector('.progressPercent').textContent = '0%';
        container.querySelector('.progress-bar').style.width = '0%';
        container.classList.remove('completed'); // Remove completed class
        return;
    }
    
    let completedTime = 0;
    for (let i = 0; i < selectedIndex; i++) {
        completedTime += allStages[i].time;
    }
    
    let remainingSeconds = totalSeconds - completedTime;
    container.querySelector('.remainingTime').textContent = formatTime(remainingSeconds);
    
    // Start countdown specific to this build
    container.interval = setInterval(() => {
        if (remainingSeconds > 0) {
            remainingSeconds--;
            container.querySelector('.remainingTime').textContent = formatTime(remainingSeconds);
            
            // Update progress and check for completion
            const progress = ((totalSeconds - remainingSeconds) / totalSeconds * 100).toFixed(1);
            container.querySelector('.progressPercent').textContent = `${progress}%`;
            container.querySelector('.progress-bar').style.width = `${progress}%`;
            
            if (progress >= 100) {
                container.classList.add('completed');
            } else {
                container.classList.remove('completed'); // Remove completed class if progress < 100%
            }
        } else {
            clearInterval(container.interval);
            container.classList.add('completed');
        }
    }, 1000);
    
    // Initial progress update
    const progress = (completedTime / totalSeconds * 100).toFixed(1);
    container.querySelector('.progressPercent').textContent = `${progress}%`;
    container.querySelector('.progress-bar').style.width = `${progress}%`;
    
    // Set initial completed state
    if (progress >= 100) {
        container.classList.add('completed');
    } else {
        container.classList.remove('completed'); // Remove completed class if progress < 100%
    }
}

function removeBuild(btn) {
    const container = btn.closest('.container');
    if (container) {
        // Clear the interval when removing a build
        if (container.interval) {
            clearInterval(container.interval);
        }
        container.remove();
    }
}

function formatTime(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = Math.floor(totalSeconds % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

// Function to rename build
function renameBuild(span) {
    const newName = prompt('Enter new build name:', span.textContent);
    if (newName && newName.trim() !== '') {
        span.textContent = newName.trim();
    }
} 