importScripts("https://www.gstatic.com/firebasejs/7.16.1/firebase-app.js");
importScripts("https://www.gstatic.com/firebasejs/7.16.1/firebase-messaging.js");


// Initialize the Firebase app in the service worker by passing in the
// messagingSenderId.
var firebaseConfig = {
    apiKey: "AIzaSyAfENGprdd5Lc3VWzgdz1414M4SovPK08o",
    authDomain: "foodfall.firebaseapp.com",
    projectId: "foodfall",
    storageBucket: "foodfall.appspot.com",
    messagingSenderId: "996053764178",
    appId: "1:996053764178:web:a0bb76984848ea60ea778b",
    measurementId: "G-7CFHLSW4LJ"
};
// Initialize Firebase
firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

messaging.setBackgroundMessageHandler(function(payload) {
    console.log(
        "[firebase-messaging-sw.js] Received background message ",
        payload,
    );
    // Customize notification here
    const notificationTitle = "Background Message Title";
    const notificationOptions = {
        body: "Background Message body.",
        // icon: "/itwonders-web-logo.png",
    };

    return self.registration.showNotification(
        notificationTitle,
        notificationOptions,
    );
});