// static/js/validate_numero.js
document.addEventListener('DOMContentLoaded', () => {
    const numeroInput = document.getElementById('numero');
    const errorDiv = document.getElementById('numero-error');

    numeroInput.addEventListener('blur', () => {
        const numero = numeroInput.value;

        if (numero) {
            fetch(`/check_numero/?numero=${encodeURIComponent(numero)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.exists) {
                        errorDiv.classList.remove('hidden');
                    } else {
                        errorDiv.classList.add('hidden');
                    }
                })
                .catch(error => console.error('Error checking numero:', error));
        }
    });
});
