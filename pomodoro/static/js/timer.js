// Pomodoro Timer JavaScript - Step 3
// Basic Timer Display Logic

document.addEventListener('DOMContentLoaded', function() {
    console.log('Pomodoro Timer loaded - Step 3: Timer Display Logic');
    
    // Basic element references
    const startBtn = document.getElementById('startBtn');
    const resetBtn = document.getElementById('resetBtn');
    const timerDisplay = document.querySelector('.timer-text');
    const progressRing = document.querySelector('.progress-ring-progress');
    const timerStatus = document.querySelector('.timer-status');
    
    // Timer configuration
    const POMODORO_DURATION = 25 * 60; // 25 minutes in seconds
    
    // Timer state
    let currentTime = POMODORO_DURATION;
    
    /**
     * Format seconds into MM:SS format
     * @param {number} totalSeconds - Total seconds to format
     * @returns {string} - Formatted time string (MM:SS)
     */
    function formatTime(totalSeconds) {
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        
        // Pad with leading zeros
        const paddedMinutes = minutes.toString().padStart(2, '0');
        const paddedSeconds = seconds.toString().padStart(2, '0');
        
        return `${paddedMinutes}:${paddedSeconds}`;
    }
    
    /**
     * Update the timer display with formatted time
     * @param {number} timeInSeconds - Time in seconds to display
     */
    function updateTimerDisplay(timeInSeconds) {
        if (timerDisplay) {
            const formattedTime = formatTime(timeInSeconds);
            timerDisplay.textContent = formattedTime;
            console.log(`Timer display updated: ${formattedTime}`);
        }
    }
    
    /**
     * Initialize the timer display
     */
    function initializeTimer() {
        updateTimerDisplay(currentTime);
        console.log('Timer initialized with 25:00');
    }
    
    // Test the formatTime function with various inputs
    function testFormatTime() {
        console.log('Testing formatTime function:');
        console.log(`formatTime(1500): ${formatTime(1500)}`); // Should be 25:00
        console.log(`formatTime(660): ${formatTime(660)}`);   // Should be 11:00
        console.log(`formatTime(59): ${formatTime(59)}`);     // Should be 00:59
        console.log(`formatTime(0): ${formatTime(0)}`);       // Should be 00:00
        console.log(`formatTime(3661): ${formatTime(3661)}`); // Should be 61:01
    }
    
    // Basic event listeners (enhanced with display updates)
    if (startBtn) {
        startBtn.addEventListener('click', function() {
            console.log('Start button clicked');
            // For now, just refresh the display
            updateTimerDisplay(currentTime);
        });
    }
    
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            console.log('Reset button clicked');
            // Reset timer to 25 minutes
            currentTime = POMODORO_DURATION;
            updateTimerDisplay(currentTime);
        });
    }
    
    // Initialize the timer when page loads
    initializeTimer();
    
    // Run tests in console
    testFormatTime();
    
    console.log('Timer display logic initialized successfully');
    
    // Expose functions globally for testing (temporary)
    window.pomodoroTimer = {
        formatTime: formatTime,
        updateTimerDisplay: updateTimerDisplay,
        currentTime: currentTime
    };
});
