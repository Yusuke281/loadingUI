document.addEventListener('DOMContentLoaded', () => {

    // --- Progress Bar Animation ---
    function animateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            // Reset animation
            bar.style.width = '0%';
            // Trigger animation after a short delay
            setTimeout(() => {
                bar.style.width = '100%';
            }, 100);
        });
    }

    // Animate on load
    animateProgressBars();

    // Re-run animation every 4 seconds for demonstration
    setInterval(animateProgressBars, 4000);


    // --- Copy to Clipboard Logic ---
    const copyButtons = document.querySelectorAll('.copy-btn');

    copyButtons.forEach(button => {
        button.addEventListener('click', () => {
            const codeBlock = button.nextElementSibling; // The <pre> element
            const codeToCopy = codeBlock.querySelector('code').innerText;

            navigator.clipboard.writeText(codeToCopy).then(() => {
                // Success feedback
                button.textContent = 'Copied!';
                button.classList.add('copied');
                
                // Revert back after 2 seconds
                setTimeout(() => {
                    button.textContent = 'Copy';
                    button.classList.remove('copied');
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy text: ', err);
                button.textContent = 'Error';
            });
        });
    });

});
