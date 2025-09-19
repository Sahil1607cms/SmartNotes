import React from "react";
import { NavLink } from "react-router-dom";
import { Home, Youtube, FileText, Clock ,AudioLines} from "lucide-react";
import logo from "../assets/logo.png"
const Sidebar = () => {
  const linkClasses = ({ isActive }) =>
    `flex items-center gap-3 p-2 rounded-lg cursor-pointer ${
      isActive ? "bg-blue-600 text-white" : "hover:bg-gray-800"
    }`;

  return (
    <aside className="bg-[#12141c] text-white p-4 h-screen">
      <div className="flex items-center gap-3 mb-8">
        <img
          src={logo}
          alt="App Logo"
          className="w-10 h-10 rounded-full"
        />
        <h1 className="text-2xl font-bold ">SmartNotes</h1>
      </div>

      {/* Menu Items */}
      <div className="flex flex-col gap-90">
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
          <NavLink to="/meeting" className={linkClasses}>
            <Clock size={20} /> History
          </NavLink>
        </li>
      </ul>

      <div className="flex items-center ml-2 gap-4">
        <img
          src="https://i.pravatar.cc/40"
          alt="profile"
          className="w-10 h-10 rounded-full"
        />
        <p className="text-gray-300">Sahil Srivastava</p>
      </div>
      </div>
    </aside>
  );
};

export default Sidebar;
