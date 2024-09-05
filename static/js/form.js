document.addEventListener('DOMContentLoaded', function() {
    const productsContainer = document.getElementById('products-container');
    const fournisseurSelect = document.getElementById('fournisseur');
    let productCount = document.querySelectorAll('.product-row').length || 1;

    function updateTotalAmount() {
        let totalAmount = 0;
        document.querySelectorAll('.product-row').forEach(row => {
            const productSelect = row.querySelector('select[name="products[]"]');
            const quantityInput = row.querySelector('input[name="quantities[]"]');
            const price = parseFloat(productSelect.options[productSelect.selectedIndex].dataset.price) || 0;
            const quantity = parseInt(quantityInput.value) || 0;
            totalAmount += price * quantity;
        });
        document.getElementById('total-amount').value = totalAmount.toFixed(2);
    }

    function fetchProducts(fournisseurId) {
        fetch(`/fetch-products/${fournisseurId}/`)
            .then(response => response.json())
            .then(data => {
                const productSelects = document.querySelectorAll('.product-select');
                productSelects.forEach(select => {
                    select.innerHTML = ''; // Clear existing options
                    data.products.forEach(product => {
                        const option = document.createElement('option');
                        option.value = product.id;
                        option.dataset.price = product.prix;
                        option.textContent = product.nom;
                        select.appendChild(option);
                    });
                });
                updateTotalAmount(); // Update total amount after fetching products
            })
            .catch(error => {
                console.error('Error fetching products:', error);
                alert('Failed to fetch products.');
            });
    }

    fournisseurSelect.addEventListener('change', function() {
        const fournisseurId = this.value;
        fetchProducts(fournisseurId);
    });

    document.getElementById('add-product').addEventListener('click', function() {
        productCount++;
        const newRow = document.createElement('div');
        newRow.classList.add('product-row', 'flex', 'space-x-4', 'mb-2');
        newRow.innerHTML = `
            <div class="flex-1">
                <label for="product_${productCount}" class="block text-gray-600">Product</label>
                <select name="products[]" id="product_${productCount}" class="product-select form-control form-control-sm w-full border border-gray-300 rounded-md">
                    <!-- Options will be added dynamically -->
                </select>
            </div>
            <div class="flex-1">
                <label for="quantity_${productCount}" class="block text-gray-600">Quantity</label>
                <input type="number" name="quantities[]" id="quantity_${productCount}" class="form-control form-control-sm w-full border border-gray-300 rounded-md" min="1">
            </div>
            <button type="button" class="remove-product bg-red-600 text-white px-4 py-2 rounded-md">Remove</button>
        `;
        productsContainer.appendChild(newRow);
        fetchProducts(fournisseurSelect.value); // Fetch products for the new row
        updateTotalAmount();
    });

    productsContainer.addEventListener('click', function(event) {
        if (event.target.classList.contains('remove-product')) {
            if (confirm('Are you sure you want to remove this product?')) {
                event.target.parentElement.remove();
                updateTotalAmount();
            }
        }
    });

    productsContainer.addEventListener('change', updateTotalAmount);
    document.getElementById('commande-form').addEventListener('input', updateTotalAmount);

    // Fetch initial products for the selected fournisseur
    fetchProducts(fournisseurSelect.value);
});
