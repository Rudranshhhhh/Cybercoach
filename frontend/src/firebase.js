import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
    apiKey: "AIzaSyARreUp7-9UmcTMXHT1WLJ9da1DSZTOK1o",
    authDomain: "oauth-17201.firebaseapp.com",
    projectId: "oauth-17201",
    storageBucket: "oauth-17201.firebasestorage.app",
    messagingSenderId: "289030963719",
    appId: "1:289030963719:web:5cd6e4bfdd9e0dd659a0a2"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// ✅ ADD THESE TWO LINES
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
