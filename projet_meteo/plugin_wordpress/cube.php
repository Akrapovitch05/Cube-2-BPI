<?php
/*
Plugin Name: Cube
Description: This is a custom WordPress plugin.
Version: 1.0
Author: Oleksii
Author URI: Your Website
*/
add_action('wp_enqueue_scripts', 'enqueue_custom_scripts');

function enqueue_custom_scripts() {
    // Enqueue jQuery
    wp_enqueue_script('jquery');

    // Enqueue custom JavaScript file
    wp_enqueue_script('cube-script', plugin_dir_url(__FILE__) . 'cube.js', array('jquery'), '1.0', true);

    // Pass the base URL of your Flask API to JavaScript
    wp_localize_script('cube-script', 'apiSettings', array(
        'apiBaseUrl' => 'http://192.168.32.58:5000/raspberrypi/temperature' // Adjust the URL as per your Flask API endpoint
    ));
}
?> 