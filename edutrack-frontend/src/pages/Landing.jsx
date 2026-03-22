import React from "react";
import { Link } from "react-router-dom";
import { Zap, CheckCircle, TrendingUp, Users } from "lucide-react";

const features = [
  {
    icon: Zap,
    title: "Document Intelligence",
    desc: "Upload compliance PDFs, run OCR + layout extraction, and generate structured fields.",
  },
  {
    icon: CheckCircle,
    title: "Compliance Engine",
    desc: "Compare extracted content against AICTE/UGC handbook requirements and flag issues.",
  },
  {
    icon: TrendingUp,
    title: "Risk Analytics",
    desc: "Combine DSS trends and metrics to identify risk patterns and anomalies.",
  },
];

const steps = [
  { id: "01", title: "Institution Upload", desc: "Upload mandatory documents and metadata" },
  { id: "02", title: "AI Processing", desc: "System extracts fields and computes scores" },
  { id: "03", title: "Review Queue", desc: "Reviewers verify evidence and approve/reject" },
  { id: "04", title: "Admin Dashboard", desc: "Monitor throughput and system metrics" },
];

export default function Landing() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-950">
      {/* Header Navigation */}
      <nav className="sticky top-0 z-50 bg-slate-900/80 backdrop-blur-xl border-b border-slate-700/40">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-gradient-primary rounded-lg">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">EDUTRACK</span>
          </div>
          <div className="flex gap-4">
            <Link to="/dashboard" className="px-6 py-2.5 border border-slate-600 hover:border-primary/50 text-slate-300 hover:text-white rounded-lg transition">
              Dashboard
            </Link>
            <Link to="/login" className="px-6 py-2.5 text-slate-300 hover:text-white transition">
              Sign In
            </Link>
            <Link to="/dashboard" className="px-6 py-2.5 bg-gradient-primary hover:shadow-lg hover:shadow-primary/50 text-white rounded-lg font-medium transition">
              Evaluate Now
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-20">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-2 mb-6">
            <span className="text-xs font-semibold text-primary">🚀 AI-POWERED INSTITUTIONAL EVALUATION</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
            Institutional Approval<br />
            <span className="text-transparent bg-clip-text bg-gradient-primary">Automated With AI</span>
          </h1>
          
          <p className="text-xl text-slate-300 mb-10 max-w-3xl mx-auto">
            Advanced ML-powered evaluation system for institutional compliance, risk assessment, and performance prediction.
          </p>
          
          <div className="flex gap-4 justify-center">
            <Link to="/dashboard" className="px-8 py-4 border border-slate-600 hover:border-primary/50 text-slate-300 rounded-lg font-semibold transition">
              Open Dashboard
            </Link>
            <Link to="/dashboard" className="px-8 py-4 bg-gradient-primary hover:shadow-lg hover:shadow-primary/50 text-white rounded-lg font-semibold transition">
              Get Started
            </Link>
            <Link to="/" className="px-8 py-4 border border-slate-600 hover:border-primary/50 text-slate-300 rounded-lg font-semibold transition">
              Learn More
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <div key={idx} className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-8 hover:border-primary/50 transition group">
                <div className="p-3 bg-gradient-primary rounded-lg w-fit mb-4 group-hover:shadow-lg group-hover:shadow-primary/50 transition">
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                <p className="text-slate-400">{feature.desc}</p>
              </div>
            );
          })}
        </div>

        {/* Steps Section */}
        <div className="bg-slate-800/20 backdrop-blur-sm border border-slate-700/40 rounded-2xl p-12">
          <h2 className="text-3xl font-bold text-white mb-12 text-center">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {steps.map((step, idx) => (
              <div key={idx} className="relative">
                <div className="bg-gradient-primary rounded-full w-12 h-12 flex items-center justify-center text-white font-bold mb-4">
                  {step.id}
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{step.title}</h3>
                <p className="text-slate-400 text-sm">{step.desc}</p>
                {idx < steps.length - 1 && (
                  <div className="hidden md:block absolute top-6 -right-4 w-8 h-0.5 bg-slate-700"></div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-20 bg-gradient-primary/10 border border-primary/30 rounded-2xl p-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to Evaluate?</h2>
          <p className="text-slate-400 mb-8">Start using our advanced ML models for institutional evaluation</p>
          <Link to="/dashboard" className="inline-block px-8 py-4 bg-gradient-primary hover:shadow-lg hover:shadow-primary/50 text-white rounded-lg font-semibold transition">
            Launch Dashboard
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-700/40 bg-slate-900/50 mt-20 py-8">
        <div className="max-w-7xl mx-auto px-6 text-center text-slate-500 text-sm">
          <p>© 2026 EduTrack. All rights reserved.</p>
        </div>
      </footer>
    </main>
  );
}
