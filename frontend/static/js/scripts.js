function showError(message) {
    const overlay = document.getElementById('overlay');
    const errorMessage = document.getElementById('error-message');
    errorMessage.textContent = message;
    overlay.style.display = 'block';
    errorMessage.style.display = 'block';
}

function hideError() {
    const overlay = document.getElementById('overlay');
    const errorMessage = document.getElementById('error-message');
    overlay.style.display = 'none';
    errorMessage.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function () {

    if (document.getElementById('error-message').textContent.trim() !== '') {
        showError(document.getElementById('error-message').textContent);
    }

    document.getElementById('transform-form').addEventListener('submit', function (event) {
        const submitButton = document.getElementById('submit-button');
        submitButton.disabled = true;
        let dots = 0;
        const originalText = 'Processing';
        submitButton.textContent = originalText;

        const interval = setInterval(() => {
            dots = (dots + 1) % 4;
            submitButton.textContent = originalText + '.'.repeat(dots);
        }, 500);

        // Re-enable the button after form submission is complete
        this.addEventListener('ajaxComplete', function () {
            clearInterval(interval);
            submitButton.disabled = false;
            submitButton.textContent = 'Transform';
        });
    });
});