document.addEventListener('DOMContentLoaded', () => {
    const controls = document.querySelector('.controls');
    const loaderWrappers = document.querySelectorAll('.loader-wrapper');
    const controlButtons = document.querySelectorAll('.control-btn');

    controls.addEventListener('click', (e) => {
        if (!e.target.classList.contains('control-btn')) return;

        const loaderName = e.target.dataset.loader;

        // Deactivate all wrappers and buttons
        loaderWrappers.forEach(wrapper => wrapper.classList.remove('active'));
        controlButtons.forEach(button => button.classList.remove('active'));

        // Activate the selected one
        const targetWrapper = document.getElementById(loaderName);
        if (targetWrapper) {
            targetWrapper.classList.add('active');
        }
        e.target.classList.add('active');
        
        // Special handling for progress bars to restart animation
        if (loaderName.startsWith('bar')) {
            const progressBar = targetWrapper.querySelector('.progress-bar');
            if (progressBar) {
                // Reset animation
                progressBar.style.transition = 'none';
                progressBar.style.width = '0%';
                // Trigger reflow
                progressBar.offsetHeight; // eslint-disable-line no-unused-expressions
                // Re-apply animation
                progressBar.style.transition = 'width 2s ease-out';
                progressBar.style.width = '100%';
            }
        }
    });

    // Set initial state (optional, can show placeholder)
    document.getElementById('loader-placeholder').classList.add('active');
});