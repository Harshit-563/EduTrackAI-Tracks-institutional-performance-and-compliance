import React, { useState, useEffect } from "react";
import { ml } from "../api/api";
import MetricsCard from "../components/MetricsCard";
import RiskIndicator from "../components/RiskIndicator";
import PerformanceChart from "../components/PerformanceChart";
import { AlertCircle, Loader, TrendingUp, Zap, Target, Shield, BarChart3 } from "lucide-react";

export default function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [institutionData, setInstitutionData] = useState({
    college_name: "Sample Institute",
    state: "Delhi",
    city: "New Delhi",
    college_type: "Public",
    total_students: 3500,
    total_faculty: 250,
    placement_rate: 85,
    infrastructure_quality: 85,
    student_faculty_ratio: 14,
    faculty_adequacy: 92,
    financial_efficiency: 75,
    fund_utilization: 82,
    missing_doc_count: 2,
    avg_doc_dss: 78,
    dss: 78,
  });

  const [predictions, setPredictions] = useState(null);
  const [basicHealth, setBasicHealth] = useState(false);

  useEffect(() => {
    checkAPIHealth();
  }, []);

  const checkAPIHealth = async () => {
    try {
      const response = await ml.checkHealth();
      if (response.data.status === "ok") {
        setBasicHealth(true);
      }
    } catch (err) {
      setError("Failed to connect to API server");
    }
  };

  const handleEvaluate = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await ml.evaluateInstitution(institutionData);
      setPredictions(result.data);
    } catch (err) {
      setError(err.message || "Failed to evaluate institution");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setInstitutionData({
      ...institutionData,
      [name]: isNaN(value) ? value : parseFloat(value),
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-950">
      {/* Header Section */}
      <div className="sticky top-0 z-40 bg-slate-900/80 backdrop-blur-xl border-b border-slate-700/40 px-6 py-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-gradient-primary rounded-lg">
                  <Target className="w-6 h-6 text-white" />
                </div>
                <h1 className="text-3xl font-bold text-white">Institutional Evaluation</h1>
              </div>
              <p className="text-slate-400 text-sm">AI-powered risk assessment & performance prediction</p>
            </div>
            {basicHealth && (
              <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-lg px-4 py-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-green-400 text-sm font-medium">API Connected</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="px-6 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Error Alert */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 mb-8 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
              <span className="text-red-300">{error}</span>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Input Panel */}
            <div className="lg:col-span-1">
              <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6 sticky top-32">
                <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-primary" />
                  Institution Metrics
                </h2>

                <div className="space-y-5">
                  {/* College Name */}
                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-2">
                      College Name
                    </label>
                    <input
                      type="text"
                      name="college_name"
                      value={institutionData.college_name}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2.5 bg-slate-700/40 border border-slate-600/40 rounded-lg text-white text-sm focus:outline-none focus:border-primary/60 focus:ring-2 focus:ring-primary/20"
                    />
                  </div>

                  {/* State */}
                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-2">
                      State
                    </label>
                    <input
                      type="text"
                      name="state"
                      value={institutionData.state}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2.5 bg-slate-700/40 border border-slate-600/40 rounded-lg text-white text-sm focus:outline-none focus:border-primary/60 focus:ring-2 focus:ring-primary/20"
                    />
                  </div>

                  {/* City */}
                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-2">
                      City
                    </label>
                    <input
                      type="text"
                      name="city"
                      value={institutionData.city}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2.5 bg-slate-700/40 border border-slate-600/40 rounded-lg text-white text-sm focus:outline-none focus:border-primary/60 focus:ring-2 focus:ring-primary/20"
                    />
                  </div>

                  {/* College Type */}
                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-2">
                      College Type
                    </label>
                    <select
                      name="college_type"
                      value={institutionData.college_type}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2.5 bg-slate-700/40 border border-slate-600/40 rounded-lg text-white text-sm focus:outline-none focus:border-primary/60 focus:ring-2 focus:ring-primary/20"
                    >
                      <option value="Public">Public</option>
                      <option value="Private">Private</option>
                      <option value="Deemed">Deemed</option>
                      <option value="Technical">Technical</option>
                    </select>
                  </div>

                  {/* Sliders */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <label className="text-sm font-semibold text-slate-300">Students</label>
                      <span className="text-primary font-bold">{institutionData.total_students}</span>
                    </div>
                    <input
                      type="range"
                      name="total_students"
                      min="100"
                      max="10000"
                      step="100"
                      value={institutionData.total_students}
                      onChange={handleInputChange}
                      className="w-full h-2 bg-slate-700/40 rounded-lg appearance-none cursor-pointer"
                    />
                    <div className="flex justify-between text-xs text-slate-500 mt-1">
                      <span>100</span>
                      <span>10K</span>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <label className="text-sm font-semibold text-slate-300">Faculty</label>
                      <span className="text-primary font-bold">{institutionData.total_faculty}</span>
                    </div>
                    <input
                      type="range"
                      name="total_faculty"
                      min="10"
                      max="1000"
                      step="10"
                      value={institutionData.total_faculty}
                      onChange={handleInputChange}
                      className="w-full h-2 bg-slate-700/40 rounded-lg appearance-none cursor-pointer"
                    />
                    <div className="flex justify-between text-xs text-slate-500 mt-1">
                      <span>10</span>
                      <span>1K</span>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <label className="text-sm font-semibold text-slate-300">Placement Rate</label>
                      <span className="text-primary font-bold">{institutionData.placement_rate}%</span>
                    </div>
                    <input
                      type="range"
                      name="placement_rate"
                      min="0"
                      max="100"
                      step="1"
                      value={institutionData.placement_rate}
                      onChange={handleInputChange}
                      className="w-full h-2 bg-slate-700/40 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <label className="text-sm font-semibold text-slate-300">DSS Score</label>
                      <span className="text-primary font-bold">{institutionData.dss}</span>
                    </div>
                    <input
                      type="range"
                      name="dss"
                      min="0"
                      max="100"
                      step="1"
                      value={institutionData.dss}
                      onChange={handleInputChange}
                      className="w-full h-2 bg-slate-700/40 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <label className="text-sm font-semibold text-slate-300">Infrastructure</label>
                      <span className="text-primary font-bold">{institutionData.infrastructure_quality}%</span>
                    </div>
                    <input
                      type="range"
                      name="infrastructure_quality"
                      min="0"
                      max="100"
                      step="1"
                      value={institutionData.infrastructure_quality}
                      onChange={handleInputChange}
                      className="w-full h-2 bg-slate-700/40 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <label className="text-sm font-semibold text-slate-300">Financial Efficiency</label>
                      <span className="text-primary font-bold">{institutionData.financial_efficiency}%</span>
                    </div>
                    <input
                      type="range"
                      name="financial_efficiency"
                      min="0"
                      max="100"
                      step="1"
                      value={institutionData.financial_efficiency}
                      onChange={handleInputChange}
                      className="w-full h-2 bg-slate-700/40 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>

                  {/* Evaluate Button */}
                  <button
                    onClick={handleEvaluate}
                    disabled={loading || !basicHealth}
                    className="w-full mt-8 px-4 py-3 bg-gradient-primary text-white font-semibold rounded-lg hover:shadow-lg hover:shadow-primary/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <>
                        <Loader className="w-4 h-4 animate-spin" />
                        Evaluating...
                      </>
                    ) : (
                      <>
                        <BarChart3 className="w-4 h-4" />
                        Evaluate Institution
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Results Panel */}
            <div className="lg:col-span-2 space-y-6">
              {predictions ? (
                <>
                  {/* Risk Assessment */}
                  {predictions.risk_assessment && (
                    <RiskIndicator
                      risk={predictions.risk_assessment}
                      title="Risk Assessment"
                    />
                  )}

                  {/* Performance & Score Row */}
                  <div className="grid grid-cols-2 gap-6">
                    {/* Performance Prediction */}
                    {predictions.performance_prediction && (
                      <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
                        <div className="flex items-center gap-2 mb-4">
                          <Target className="w-5 h-5 text-primary" />
                          <h3 className="text-lg font-bold text-white">Performance</h3>
                        </div>
                        <div className="space-y-4">
                          <div>
                            <p className="text-xs text-slate-400 font-semibold uppercase mb-2">Tier</p>
                            <p className="text-2xl font-bold text-primary">
                              {predictions.performance_prediction.tier}
                            </p>
                          </div>
                          <div className="h-1 bg-slate-700/40 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-primary"
                              style={{
                                width: `${Math.min(predictions.performance_prediction.confidence, 100)}%`,
                              }}
                            ></div>
                          </div>
                          <p className="text-sm text-slate-400">
                            <span className="font-semibold text-primary">
                              {predictions.performance_prediction.confidence.toFixed(0)}%
                            </span>{" "}
                            confidence
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Comprehensive Score */}
                    {predictions.comprehensive_score && (
                      <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
                        <div className="flex items-center gap-2 mb-4">
                          <Shield className="w-5 h-5 text-secondary" />
                          <h3 className="text-lg font-bold text-white">Overall Score</h3>
                        </div>
                        <div className="text-center mt-6">
                          <p className={`text-5xl font-bold ${
                            predictions.comprehensive_score.score >= 85
                              ? "text-green-400"
                              : predictions.comprehensive_score.score >= 70
                              ? "text-blue-400"
                              : predictions.comprehensive_score.score >= 55
                              ? "text-yellow-400"
                              : "text-red-400"
                          }`}>
                            {predictions.comprehensive_score.score.toFixed(1)}
                          </p>
                          <p className="text-sm text-slate-400 mt-2">out of 100</p>
                          <div className="mt-4 h-1 bg-slate-700/40 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${
                                predictions.comprehensive_score.score >= 85
                                  ? "bg-gradient-to-r from-green-500 to-green-400"
                                  : predictions.comprehensive_score.score >= 70
                                  ? "bg-gradient-to-r from-blue-500 to-blue-400"
                                  : predictions.comprehensive_score.score >= 55
                                  ? "bg-gradient-to-r from-yellow-500 to-yellow-400"
                                  : "bg-gradient-to-r from-red-500 to-red-400"
                              }`}
                              style={{
                                width: `${(predictions.comprehensive_score.score / 100) * 100}%`,
                              }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Anomaly Detection */}
                  {predictions.anomaly_detection && (
                    <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
                      <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                        <Zap className="w-5 h-5" />
                        Anomaly Detection
                      </h3>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span
                            className={`inline-block w-4 h-4 rounded-full ${
                              predictions.anomaly_detection.is_anomaly
                                ? "bg-red-500 animate-pulse"
                                : "bg-green-500"
                            }`}
                          ></span>
                          <span className="text-slate-300">
                            {predictions.anomaly_detection.is_anomaly
                              ? "Anomalous Profile Detected"
                              : "Normal Institution Profile"}
                          </span>
                        </div>
                        <span className="text-sm text-slate-400">
                          Score: {(predictions.anomaly_detection.anomaly_score).toFixed(2)}
                        </span>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-12 text-center">
                  <div className="flex justify-center mb-4">
                    <div className="p-4 bg-primary/10 rounded-lg">
                      <TrendingUp className="w-8 h-8 text-primary" />
                    </div>
                  </div>
                  <p className="text-slate-300 font-medium">Ready to evaluate</p>
                  <p className="text-slate-500 text-sm mt-1">
                    Adjust institution metrics and click "Evaluate Institution"
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
