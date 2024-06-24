$(document).ready(function() {
    $('#recommendForm').submit(function(event) {
        event.preventDefault();
        var query = $('#query').val();
        $('#loadingSpinner').show(); // Show loading spinner
        $.ajax({
            type: 'POST',
            url: '/recommend',
            contentType: 'application/json',
            data: JSON.stringify({'query': query}),
            success: function(response) {
                $('#loadingSpinner').hide(); // Hide loading spinner
                var resultsHtml = '';
                var totalResults = response.flipkart.length + response.amazon.length;
                resultsHtml += '<h2>Total Results Found: ' + totalResults + '</h2>';
                resultsHtml += '<h2>Flipkart Results:</h2>';
                $.each(response.flipkart, function(index, product) {
                    resultsHtml += '<div class="product"><p><strong>' + product.name + '</strong>: Rs. ' + product.price + '</p></div>';
                });
                resultsHtml += '<h2>Amazon Results:</h2>';
                $.each(response.amazon, function(index, product) {
                    resultsHtml += '<div class="product"><p><strong>' + product.name + '</strong>: Rs. ' + product.price + '</p></div>';
                });
                $('#results').html(resultsHtml);
            }
        });
    });
});
