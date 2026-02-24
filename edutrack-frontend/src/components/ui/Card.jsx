import React from "react";

export default function Card({ children, className = "" }) {
  return (
    <section className={`bg-gray-900/20 border border-gray-800 rounded-xl p-4 ${className}`}>
      {children}
    </section>
  );
}
