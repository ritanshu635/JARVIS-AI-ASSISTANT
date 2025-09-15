$(document).ready(function () {

    // Initialize Socket.IO connection
    var socket = io();
    var jarvisRunning = false;

    $('.text').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "bounceIn",
        },
        out: {
            effect: "bounceOut",
        },

    });

    // Siri configuration
    var siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: 800,
        height: 200,
        style: "ios9",
        amplitude: "1",
        speed: "0.30",
        autostart: true
      });

    // Siri message animation
    $('.siri-message').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "fadeInUp",
            sync: true,
        },
        out: {
            effect: "fadeOutUp",
            sync: true,
        },

    });

    // Socket.IO event handlers
    socket.on('connect', function() {
        console.log('Connected to JARVIS Web Server');
        updateWishMessage('Connected to JARVIS Web Interface');
    });

    socket.on('jarvis_status', function(data) {
        console.log('JARVIS Status:', data);
        handleJarvisStatus(data.status, data.message);
    });

    socket.on('speaking_animation', function(data) {
        if (data.active && jarvisRunning) {
            triggerSpeakingAnimation();
        }
    });

    // Start JARVIS button click
    $(document).on('click', '#StartJarvis', function() {
        console.log('Starting JARVIS...');
        socket.emit('start_jarvis');
        updateWishMessage('Starting JARVIS...');
        showStartupSequence();
    });

    function handleJarvisStatus(status, message) {
        switch(status) {
            case 'starting':
                jarvisRunning = false;
                updateWishMessage('Starting JARVIS...');
                showStartupSequence();
                break;
            case 'running':
                jarvisRunning = true;
                updateWishMessage('JARVIS Online - Ready for Commands');
                showJarvisInterface();
                break;
            case 'stopping':
                updateWishMessage('Stopping JARVIS...');
                break;
            case 'stopped':
                jarvisRunning = false;
                updateWishMessage('JARVIS Offline - Click Start to Begin');
                showStartScreen();
                break;
            case 'error':
                jarvisRunning = false;
                updateWishMessage('Error: ' + message);
                showStartScreen();
                break;
        }
    }

    function showStartupSequence() {
        $("#Start").attr("hidden", false);
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", true);
        
        // Show startup animations
        setTimeout(function() {
            $("#Loader").attr("hidden", true);
            $("#FaceAuth").attr("hidden", false);
        }, 2000);
        
        setTimeout(function() {
            $("#FaceAuth").attr("hidden", true);
            $("#FaceAuthSuccess").attr("hidden", false);
        }, 4000);
        
        setTimeout(function() {
            $("#FaceAuthSuccess").attr("hidden", true);
            $("#HelloGreet").attr("hidden", false);
        }, 6000);
        
        setTimeout(function() {
            showJarvisInterface();
        }, 8000);
    }

    function showJarvisInterface() {
        $("#Start").attr("hidden", true);
        $("#Oval").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
    }

    function showStartScreen() {
        $("#Start").attr("hidden", false);
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", true);
        
        // Reset to loader
        $("#Loader").attr("hidden", false);
        $("#FaceAuth").attr("hidden", true);
        $("#FaceAuthSuccess").attr("hidden", true);
        $("#HelloGreet").attr("hidden", true);
    }

    function updateWishMessage(message) {
        $("#WishMessage").text(message);
        $('.siri-message').textillate('start');
    }

    function triggerSpeakingAnimation() {
        // Add speaking animation to the main interface
        $("#JarvisHood").addClass('speaking-animation');
        $(".svg-frame").addClass('speaking-animation');
        
        setTimeout(function() {
            $("#JarvisHood").removeClass('speaking-animation');
            $(".svg-frame").removeClass('speaking-animation');
        }, 1000);
    }

    // mic button click event (only works when JARVIS is running)
    $("#MicBtn").click(function () { 
        if (jarvisRunning) {
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            updateWishMessage("Listening...");
        } else {
            updateWishMessage("Please start JARVIS first");
        }
    });

    function doc_keyUp(e) {
        // Keyboard shortcut to activate JARVIS
        if (e.key === 'j' && e.metaKey && jarvisRunning) {
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            updateWishMessage("Listening...");
        }
    }
    document.addEventListener('keyup', doc_keyUp, false);

    // Initialize with start screen
    showStartScreen();
    updateWishMessage('Click Start to Initialize JARVIS');

});