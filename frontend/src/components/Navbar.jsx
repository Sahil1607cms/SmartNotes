import React from "react";
import {  Plus } from "lucide-react";

const Navbar = () => {
  return (
    <nav className="h-16 flex items-center justify-between px-3 sm:px-6 border-b border-gray-700 bg-[#0f1117] text-white">
      <h2 className="text-lg sm:text-xl md:text-2xl ml-0 sm:ml-3 font-bold text-yellow-400">Dashboard</h2>
      <div className="flex items-center gap-2 sm:gap-4">
        
        <button className="flex items-center gap-1 sm:gap-2 cursor-pointer bg-blue-600 px-2 sm:px-4 py-2 rounded-lg text-sm sm:text-base">
          <Plus size={16} className="sm:w-[18px] sm:h-[18px]" /> 
          <span className="hidden sm:inline">New Summary</span>
          <span className="sm:hidden">New</span>
        </button>
        
      </div>
    </nav>
  );
};

export default Navbar;
