'use client';
import { useState, useEffect } from 'react';
import { analyzeEnhanced, type EnhancedAnalyzeResponse } from '../utils/api';
import TrustScore from '@/components/TrustScore';
import { ShieldCheck, AlertTriangle, ArrowRight, Building2 } from 'lucide-react';
import clsx from 'clsx';

interface Particle {
  id: number;
  x: number;
  y: number;
  size: number;
  duration: number;
  delay: number;
}

export default function Analyze() {
  const [jobUrl, setJobUrl] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [companyUrl, setCompanyUrl] = useState('');
  const [result, setResult] = useState<EnhancedAnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [particles, setParticles] = useState<Particle[]>([]);

  useEffect(() => {
    const particleArray = Array.from({ length: 80 }, (_, i) => ({
      id: i,
      x: (i * 37) % 100,
      y: (i * 73) % 100,
      size: 0.5 + (i % 3) * 1,
      duration: 3 + (i % 3),
      delay: (i % 5) * 0.4,
    }));
    setParticles(particleArray);
  }, []);

  const handleAnalyze = async () => {
    // 1. Validate Job Input
    if (!jobUrl && !jobDescription) {
      setError("Please provide either a Post/Message Link or Description.");
      return;
    }

    // 2. Validate Job Description Length
    if (jobDescription && jobDescription.length < 50) {
      setError("Description is too short. Please provide at least 50 characters for accurate analysis.");
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await analyzeEnhanced(jobUrl, jobDescription, companyUrl);
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950 text-white font-sans selection:bg-emerald-400/30 overflow-hidden relative">
      {/* Animated Particles Background */}
      <style>{`
        @keyframes floatParticle {
          0% { transform: translateY(0) scale(1); opacity: 0; }
          10% { opacity: 1; }
          50% { opacity: 0.8; }
          90% { opacity: 0.5; }
          100% { transform: translateY(-150px) scale(0.2); opacity: 0; }
        }

        .particle {
          position: fixed;
          border-radius: 50%;
          pointer-events: none;
          background: radial-gradient(circle at 30% 30%, rgba(16, 185, 129, 1), rgba(6, 182, 212, 0.8));
          box-shadow: 0 0 20px rgba(16, 185, 129, 1), 0 0 40px rgba(6, 182, 212, 1), 0 0 60px rgba(16, 185, 129, 0.8);
        }
      `}</style>

      {/* Floating Particles */}
      {particles.map((particle) => (
        <div
          key={particle.id}
          className="particle"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            width: `${particle.size}px`,
            height: `${particle.size}px`,
            animation: `floatParticle ${particle.duration}s ease-in ${particle.delay}s infinite`,
          }}
        />
      ))}

      <div className="relative z-10 max-w-5xl mx-auto px-6 py-12">
        {/* Header */}
        <header className="text-center mb-16 space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/20 border border-emerald-400/60 backdrop-blur-sm mb-4">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <span className="text-sm font-medium text-emerald-200">AI-Powered Scam Detection</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-emerald-100 to-emerald-400">
            TrustGuard AI
          </h1>
          <p className="text-lg text-slate-300 max-w-2xl mx-auto">
            Analyze job postings, messages, and websites instantly. Detect scams, hidden fees, and phishing attempts with advanced AI.
          </p>
        </header>

        {/* Main Input Section */}
        <div className="grid grid-cols-1 gap-8 mb-12">
          {/* Check for Scams Card */}
          <div className="group relative">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-emerald-400 to-cyan-400 rounded-2xl opacity-30 group-hover:opacity-50 transition duration-500 blur"></div>
            <div className="relative bg-slate-800/60 backdrop-blur-xl border border-emerald-500/30 rounded-2xl p-8 h-full shadow-xl shadow-emerald-500/20">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-lg bg-emerald-500/20">
                  <ShieldCheck className="w-6 h-6 text-emerald-400" />
                </div>
                <h2 className="text-xl font-semibold text-white">Check for Scams</h2>
              </div>

              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-emerald-200 mb-2">Online Post/Message Link</label>
                  <input
                    type="text"
                    placeholder="https://linkedin.com/posts/... or paste message link"
                    className="w-full bg-slate-900/50 border border-emerald-500/40 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/60 transition-all"
                    value={jobUrl}
                    onChange={(e) => setJobUrl(e.target.value)}
                  />
                  <p className="text-xs text-slate-400 mt-2 ml-1">Paste the link to the online post or message.</p>
                </div>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-emerald-500/20"></div>
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-slate-800/60 px-2 text-emerald-300 font-medium">OR</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-emerald-200 mb-2">Description of the Job/Post/Message</label>
                  <textarea
                    rows={5}
                    placeholder="Paste the full description here..."
                    className="w-full bg-slate-900/50 border border-emerald-500/40 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/60 transition-all resize-none"
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                  />
                  <p className="text-xs text-slate-400 mt-2 ml-1">
                    {jobDescription.length < 50 && jobDescription.length > 0 ? (
                      <span className="text-red-400">Too short ({jobDescription.length}/50 chars)</span>
                    ) : (
                      "Paste the text if you don't have a URL."
                    )}
                  </p>
                </div>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-emerald-500/20"></div>
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-slate-800/60 px-2 text-emerald-300 font-medium">OPTIONAL</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-emerald-200 mb-2 flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-emerald-400" />
                    Website URL
                  </label>
                  <input
                    type="text"
                    placeholder="https://company.com"
                    className="w-full bg-slate-900/50 border border-emerald-500/40 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/60 transition-all"
                    value={companyUrl}
                    onChange={(e) => setCompanyUrl(e.target.value)}
                  />
                  <p className="text-xs text-slate-400 mt-2 ml-1">
                    {companyUrl ? (
                      <span className="text-emerald-400">✓ Website will be verified via web analysis</span>
                    ) : (
                      "Add website URL to enable deeper verification"
                    )}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="flex flex-col items-center gap-4 mb-16">
          {error && (
            <div className="flex items-center gap-2 text-red-300 bg-red-500/20 px-4 py-2 rounded-lg border border-red-500/40 animate-in fade-in slide-in-from-top-2">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className={clsx(
              "group relative px-8 py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-xl font-semibold text-white shadow-lg shadow-emerald-500/50 transition-all hover:shadow-emerald-500/70 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:pointer-events-none",
              loading && "animate-pulse"
            )}
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Analyzing...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                Analyze Job
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </span>
            )}
          </button>
        </div>

        {/* Results Section */}
        {result && (
          <div className="animate-in fade-in slide-in-from-bottom-8 duration-700">
            <TrustScore result={result} />
          </div>
        )}
      </div>
    </main>
  );
}
