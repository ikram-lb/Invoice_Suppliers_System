$(document).ready(function() {
    // Ensure handleChangeSingleArticle function is available
    window.handleChangeSingleArticle = function(id) {
        let productId = id.split('-')[1];
        let idQty = `#qty-${productId}`;
        let unitId = `#unit-${productId}`;
        let totalIdLine = `#total-a-${productId}`;
        let totalLine = parseFloat($(idQty).val()) * parseFloat($(unitId).val()) || 0;
        $(totalIdLine).val(totalLine);
        let total = 0;
        $('[id^=total-a-]').each(function() {
            total += parseFloat($(this).val()) || 0;
        });
        $('#total').val(total);
    };

    // Click to add new line item
    $(document).on('click', '#btn-add', function() {
        if ($('#wrapper').length) {
            var number = $('#wrapper').children().length + 1;
            let formAdd = `
                <div class="form-row">
                    <div class="form-group col-md-4">
                        <label for="product-${number}">#${number} Product </label>
                        <input required name="product" type="text" class="form-control" id="product-${number}">
                    </div>
                    <div class="form-group col-md-2">
                        <label for="qty-${number}"> Quantity </label>
                        <input required name="qty" type="number" min="1" step="0.1" class="form-control" id="qty-${number}">
                    </div>
                    <div class="form-group col-md-3">
                        <label for="unit-${number}"> Unit Price </label>
                        <input required name="unit" type="number" min="1" step="0.1" onchange="handleChangeSingleArticle(this.id)" class="form-control" id="unit-${number}">
                    </div>
                    <div class="form-group col-md-3">
                        <label for="total-a-${number}"> Total </label>
                        <input required name="total-a" type="number" min="1" step="0.1" readonly class="form-control" id="total-a-${number}">
                    </div>
                </div>
            `;
            $("#wrapper").append(formAdd);
        } else {
            console.error("Element with ID 'wrapper' not found.");
        }
    });

    // Remove last item line
    $(document).on('click', '#btn-remove', function() {
        if ($('#wrapper').children().length) {
            $("#wrapper").children().last().remove();
        } else {
            console.error("No item lines to remove.");
        }
    });

    // Ensure search functionality is working
    $("#search").on("keyup", function() {
        var value = $(this).val().toLowerCase();
        $("#myTable tr").filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
    });

    // Ensure modal handlers are working
    $(document).on('click', '#btn-invoice-modify', function() {
        let invoice_id = $(this).data('id');
        $('#id_modified').val(invoice_id);
    });

    $(document).on('click', '#btn-invoice-delete', function() {
        let invoice_id = $(this).data('id');
        $('#id_supprimer').val(invoice_id);
    });
});
