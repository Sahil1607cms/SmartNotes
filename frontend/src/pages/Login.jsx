import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import logo from "../assets/logo.png"; 

export default function Login() {
  const { loginWithGoogle } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/";

  const handleLogin = async () => {
    try {
      await loginWithGoogle();
      navigate(from, { replace: true });
    } catch (err) {
      const message = err?.code
        ? `${err.code}: ${err.message}`
        : "Login failed. Please try again.";
      alert(message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-gray-900 to-black text-white px-4">
      <div className="w-full max-w-sm p-6 sm:p-8 rounded-2xl border border-gray-800 bg-[#0f1117] shadow-lg">
        {/* Logo + Title */}
        <div className="flex flex-col items-center mb-8">
          <img src={logo} alt="App Logo" className="w-12 h-12 sm:w-14 sm:h-14 rounded-full mb-3" />
          <h1 className="text-2xl sm:text-3xl font-bold">SmartNotes</h1>
          <p className="text-gray-400 text-xs sm:text-sm mt-1">Sign in to continue</p>
        </div>

        {/* Google Button */}
        <button
          onClick={handleLogin}
          className="w-full flex items-center justify-center gap-2 sm:gap-3 bg-white text-gray-800 font-medium py-2.5 rounded-lg shadow hover:bg-gray-100 transition text-sm sm:text-base"
        >
          {/* Google "G" logo */}
          <svg
            className="w-4 h-4 sm:w-5 sm:h-5"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 488 512"
          >
            <path
              fill="#4285F4"
              d="M488 261.8c0-17.4-1.6-34.1-4.6-50.4H249v95.5h134.6c-5.9 31.6-23.7 58.3-50.3 76.1v63.4h81.2c47.5-43.7 73.5-108.1 73.5-184.6z"
            />
            <path
              fill="#34A853"
              d="M249 492c67.6 0 124.3-22.4 165.7-61l-81.2-63.4c-22.5 15.2-51.1 24.3-84.5 24.3-64.9 0-119.8-43.8-139.4-102.7H25.4v64.5C66.8 445.7 151.3 492 249 492z"
            />
            <path
              fill="#FBBC05"
              d="M109.6 289.2c-4.8-14.4-7.6-29.8-7.6-45.6s2.7-31.2 7.6-45.6V133.5H25.4C9.1 169.1 0 208.2 0 249s9.1 79.9 25.4 115.5l84.2-64.5z"
            />
            <path
              fill="#EA4335"
              d="M249 97.7c36.8 0 69.8 12.7 95.9 37.6l71.9-71.9C373.2 23.2 316.5 0 249 0 151.3 0 66.8 46.3 25.4 133.5l84.2 64.5C129.2 141.5 184.1 97.7 249 97.7z"
            />
          </svg>
          Continue with Google
        </button>
      </div>
    </div>
  );
}
