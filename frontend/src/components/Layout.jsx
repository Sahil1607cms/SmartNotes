import React from "react";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";
import { Outlet } from "react-router-dom";

export default function Layout() {
  return (
    <div className="grid grid-cols-[250px_1fr] h-screen">
      {/* Sidebar (Left Grid) */}
      <Sidebar/>

      {/* Right Side (Navbar + Main Content) */}
      <div className="flex flex-col bg-[#0f1117] text-white h-screen">

        {/* Main Content */}
        <main className="flex-1 bg-black px-2 pb-1 h-[calc(100vh-0px)] overflow-y-hidden">
          <Outlet/>
        </main>
      </div>
    </div>
  );
}
