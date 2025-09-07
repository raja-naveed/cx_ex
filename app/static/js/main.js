// Auto-refresh price data every 5 seconds when market is open
function refreshPrices() {
    if (document.querySelector('.market-open')) {
        const priceElements = document.querySelectorAll('[data-stock-id]');
        if (priceElements.length > 0) {
            fetch('/market/prices')
                .then(response => response.json())
                .then(data => {
                    priceElements.forEach(element => {
                        const stockId = element.dataset.stockId;
                        const priceData = data[stockId];
                        if (priceData) {
                            element.textContent = '$' + parseFloat(priceData.last_price).toFixed(2);
                            // Add price change indication
                            element.className = element.className.replace(/price-(up|down)/, '');
                            if (priceData.change > 0) {
                                element.classList.add('price-up');
                            } else if (priceData.change < 0) {
                                element.classList.add('price-down');
                            }
                        }
                    });
                })
                .catch(error => console.log('Price update failed:', error));
        }
    }
}

// Start price refresh interval
if (document.querySelector('[data-stock-id]')) {
    setInterval(refreshPrices, 5000);
}

// Confirm order cancellation
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('cancel-order')) {
        if (!confirm('Are you sure you want to cancel this order?')) {
            e.preventDefault();
        }
    }
});

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) {
            setTimeout(() => {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            }, 5000);
        }
    });
});