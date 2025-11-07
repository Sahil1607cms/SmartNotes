import React from "react";
import { NavLink } from "react-router-dom";
import { Home, Youtube, FileText, Clock, AudioLines } from "lucide-react";
import logo from "../assets/logo.png";
import { useAuth } from "../context/AuthContext.jsx";
import { useNavigate } from "react-router-dom";

const Sidebar = () => {
  const linkClasses = ({ isActive }) =>
    `flex items-center gap-3 p-2 rounded-lg cursor-pointer ${
      isActive ? "bg-blue-600 text-white" : "hover:bg-gray-800"
    }`;

  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  const getInitials = (nameOrEmail) => {
    if (!nameOrEmail) return "U";
    const parts = nameOrEmail.split(" ");
    if (parts.length === 1) {
      return parts[0][0].toUpperCase();
    }
    return (parts[0][0] + parts[1][0]).toUpperCase();
  };

  const displayName = user?.displayName || user?.email || "User";
  const initials = getInitials(displayName);

  return (
    <aside className="bg-black text-white p-4 h-screen flex flex-col justify-between">
  {/* Top section (Logo + Menu) */}
  <div>
    {/* Logo */}
    <div className="flex items-center gap-3 mb-8">
      <img src={logo} alt="App Logo" className="w-10 h-10 rounded-full" />
      <h1 className="text-2xl font-bold">SmartNotes</h1>
    </div>

    {/* Menu Items */}
    <ul className="space-y-4 text-gray-400">
      <li>
        <NavLink to="/yt" className={linkClasses}>
          <Youtube size={20} /> YouTube
        </NavLink>
      </li>
      <li>
        <NavLink to="/audio-video" className={linkClasses}>
          <AudioLines size={20} /> Audio/Media
        </NavLink>
      </li>
      <li>
        <NavLink to="/pdf-text" className={linkClasses}>
          <FileText size={20} /> PDF/Text
        </NavLink>
      </li>
      <li>
        <NavLink to="/history" className={linkClasses}>
          <Clock size={20} /> History
        </NavLink>
      </li>
    </ul>
  </div>

  {/* Bottom section (User info + Logout) */}
  <div className="flex items-center gap-3 p-2 rounded-lg bg-[#0f1117] border border-gray-800 mt-8">
    {user?.photoURL ? (
      <img src={user.photoURL} alt="profile" className="w-10 h-10 rounded-full" />
    ) : (
      <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold">
        {initials}
      </div>
    )}

    <div className="flex-1 min-w-0">
      <p className="text-sm text-white truncate">{displayName}</p>
      <button
        onClick={handleLogout}
        className="mt-1 text-xs text-red-400 hover:text-red-300"
      >
        Logout
      </button>
    </div>
  </div>
</aside>
  );
};

export default Sidebar;
