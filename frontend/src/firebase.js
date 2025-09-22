// Firebase initialization for the frontend app
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyCKvhr-uE23LlOqhJNLtEx3Gb54vuDbRXs",
  authDomain: "smartnotes-90f68.firebaseapp.com",
  projectId: "smartnotes-90f68",
  storageBucket: "smartnotes-90f68.firebasestorage.app",
  messagingSenderId: "52166002297",
  appId: "1:52166002297:web:a558ae47ebbda3ff6af6a8",
  measurementId: "G-KTXJZSJZPX"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();
export { app, auth, googleProvider };


