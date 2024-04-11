jQuery(document).ready(function($) {
    function fetchData() {
        // Send the AJAX request to fetch temperature and humidity data from Flask API
        $.ajax({
            url: 'http://192.168.32.58:5000/raspberrypi/temperature',
            type: 'GET', // Assuming the Flask API returns temperature and humidity data via a GET request
            dataType: 'json',
            success: function(data) {
                // Log the retrieved temperature and humidity data to the console
                console.log('Temperature:', data.temperature + '°C');
                console.log('Humidity:', data.humidity + '%');

                // Update HTML elements with temperature and humidity data received from Flask API
                $('#temperature').text('Temperature: ' + data.temperature + '°C');
                $('#humidity').text('Humidity: ' + data.humidity + '%');
            },
            error: function(xhr, status, error) {
                console.error('Error fetching data from API:', error);
            }
        });
    }

    // Fetch data initially when the page loads
    fetchData();

    // Fetch data periodically every 5 seconds (adjust as needed)
    setInterval(fetchData, 5000);
});