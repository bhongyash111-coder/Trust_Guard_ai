'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Shield } from 'lucide-react';

interface Particle {
  id: number;
  x: number;
  y: number;
  size: number;
  duration: number;
  delay: number;
}

interface CircleParticle {
  id: number;
  angle: number;
  distance: number;
  size: number;
  delay: number;
}

export default function Welcome() {
  const router = useRouter();
  const [particles, setParticles] = useState<Particle[]>([]);
  const [circleParticles, setCircleParticles] = useState<CircleParticle[]>([]);
  const [showShield, setShowShield] = useState(false);
  const [showTitle, setShowTitle] = useState(false);
  const [showSubtitle, setShowSubtitle] = useState(false);
  const [showButton, setShowButton] = useState(false);

  useEffect(() => {
    // Generate floating particles around the shield
    const newParticles: Particle[] = [];
    for (let i = 0; i < 100; i++) {
      newParticles.push({
        id: i,
        x: (i * 37) % 100,
        y: (i * 73) % 100,
        size: 0.5 + (i % 3) * 1,
        duration: 3 + (i % 3),
        delay: (i % 5) * 0.4,
      });
    }
    setParticles(newParticles);

    // Generate particles orbiting the shield
    const newCircleParticles: CircleParticle[] = [];
    for (let i = 0; i < 40; i++) {
      newCircleParticles.push({
        id: i,
        angle: (i / 40) * Math.PI * 2,
        distance: 120 + (i % 3) * 20,
        size: 1.5 + (i % 2) * 0.5,
        delay: (i % 5) * 0.1,
      });
    }
    setCircleParticles(newCircleParticles);

    // Stagger animations
    const shieldTimer = setTimeout(() => setShowShield(true), 300);
    const titleTimer = setTimeout(() => setShowTitle(true), 2000);
    const subtitleTimer = setTimeout(() => setShowSubtitle(true), 3400);
    const buttonTimer = setTimeout(() => setShowButton(true), 4600);

    return () => {
      clearTimeout(shieldTimer);
      clearTimeout(titleTimer);
      clearTimeout(subtitleTimer);
      clearTimeout(buttonTimer);
    };
  }, []);

  const handleGetStarted = () => {
    router.push('/analyze');
  };

  return (
    <main className="min-h-screen relative overflow-hidden flex items-center justify-center font-sans">
      {/* Dark Background with Grid */}
      <div className="fixed inset-0 z-0 bg-gradient-to-br from-slate-950 via-emerald-950 to-slate-900" />
      
      {/* Grid Pattern Background */}
      <div className="fixed inset-0 z-0 opacity-10">
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#10b981" strokeWidth="0.5"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
      </div>

      {/* Animated Background Orbs */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-1/3 left-1/4 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '8s' }} />
        <div className="absolute bottom-1/4 right-1/3 w-80 h-80 bg-teal-500/5 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '10s', animationDelay: '2s' }} />
      </div>

      {/* Floating Particles Background */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        {particles.map((particle) => (
          <div
            key={`bg-${particle.id}`}
            className="absolute rounded-full"
            style={{
              width: `${particle.size}px`,
              height: `${particle.size}px`,
              left: `${particle.x}%`,
              top: `${particle.y}%`,
              background: `rgba(16, 185, 129, ${0.3 + Math.random() * 0.3})`,
              boxShadow: `0 0 ${particle.size * 3}px rgba(16, 185, 129, 0.5)`,
              animation: `floatParticle ${particle.duration}s ease-in-out ${particle.delay}s infinite`,
            }}
          />
        ))}
      </div>

      {/* Content Container */}
      <div className="relative z-10 max-w-5xl mx-auto px-6 text-center flex flex-col items-center justify-center">
        
        {/* Shield Container with Orbiting Particles */}
        <div className="relative mb-16 h-80 w-80 flex items-center justify-center">
          {/* Orbiting Particles */}
          {circleParticles.map((particle) => {
            return (
              <div
                key={`orbit-${particle.id}`}
                className="absolute rounded-full"
                style={{
                  width: `${particle.size}px`,
                  height: `${particle.size}px`,
                  background: `rgba(16, 185, 129, 0.8)`,
                  boxShadow: `0 0 ${particle.size * 4}px rgba(16, 185, 129, 0.8)`,
                  animation: `orbitParticle 20s linear ${particle.delay}s infinite`,
                  left: '50%',
                  top: '50%',
                  transform: 'translate(-50%, -50%)',
                }}
              />
            );
          })}

          {/* Shield Glow Circle */}
          <div
            className={`absolute rounded-full border-2 transition-all duration-1500 ${
              showShield ? 'opacity-60 scale-100' : 'opacity-0 scale-50'
            }`}
            style={{
              width: '240px',
              height: '240px',
              borderColor: 'rgba(16, 185, 129, 0.4)',
              boxShadow: '0 0 30px rgba(16, 185, 129, 0.3), inset 0 0 30px rgba(16, 185, 129, 0.1)',
            }}
          />

          {/* Shield Icon */}
          <div
            className={`relative transition-all duration-1200 ${
              showShield ? 'opacity-100 scale-100' : 'opacity-0 scale-0'
            }`}
            style={{
              transitionTimingFunction: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
            }}
          >
            <Shield className="w-32 h-32 text-emerald-400" strokeWidth={1} />
            <div className="absolute inset-0 rounded-full bg-emerald-500/10 blur-2xl" />
          </div>
        </div>

        {/* White TRUSTGUARD AI Label */}
        <div
          className={`mb-8 transition-all duration-1200 ${
            showShield ? 'opacity-100' : 'opacity-0'
          }`}
          style={{
            transform: showShield ? 'translateY(0)' : 'translateY(20px)',
          }}
        >
          <p className="text-white font-bold text-lg tracking-widest">🛡 TRUSTGUARD AI</p>
        </div>

        {/* Main Title - "WELCOME TO TRUSTGUARD AI" */}
        <h1
          className={`text-5xl md:text-6xl font-black mb-4 transition-all duration-1400 ${
            showTitle ? 'opacity-100' : 'opacity-0'
          }`}
          style={{
            color: '#ffffff',
            transform: showTitle 
              ? 'translateY(0)' 
              : 'translateY(30px)',
            fontFamily: '"Poppins", sans-serif',
            fontWeight: 900,
            letterSpacing: '0.02em',
            textShadow: '0 0 20px rgba(16, 185, 129, 0.3)',
            lineHeight: '1.2',
          }}
        >
          WELCOME TO <br />
          <span style={{ color: '#10b981' }}>TRUSTGUARD AI</span>
        </h1>

        {/* Subtitle */}
        <h3
          className={`text-xl md:text-2xl font-semibold mb-12 transition-all duration-1200 ${
            showSubtitle ? 'opacity-100' : 'opacity-0'
          }`}
          style={{
            color: '#10b981',
            transform: showSubtitle ? 'translateY(0)' : 'translateY(20px)',
            fontFamily: '"Poppins", sans-serif',
            letterSpacing: '0.05em',
            textShadow: '0 0 10px rgba(16, 185, 129, 0.2)',
          }}
        >
          WE ARE HERE TO SAVE YOU FROM SCAMS
        </h3>

        {/* Get Started Button */}
        <div
          className={`transition-all duration-1000 ${
            showButton ? 'opacity-100 scale-100' : 'opacity-0 scale-75'
          }`}
        >
          <button
            onClick={handleGetStarted}
            className="relative inline-flex items-center justify-center px-8 py-3 font-bold text-slate-950 transition-all duration-300 group hover:scale-110 active:scale-95"
            style={{
              background: '#10b981',
              borderRadius: '6px',
              boxShadow: '0 0 20px rgba(16, 185, 129, 0.5)',
              animation: showButton ? 'buttonBounce 2s ease-in-out infinite' : 'none',
              textTransform: 'uppercase',
              fontSize: '16px',
              fontWeight: 700,
              letterSpacing: '0.1em',
            }}
          >
            <span className="relative z-10">GET STARTED</span>
            
            {/* Hover Glow */}
            <div 
              className="absolute inset-0 rounded-lg bg-emerald-400 opacity-0 group-hover:opacity-40 blur-lg transition-opacity duration-300" 
            />
          </button>
        </div>
      </div>

      {/* CSS Animations */}
      <style>{`
        @keyframes floatParticle {
          0% {
            transform: translateY(0) translateX(0) scale(1);
            opacity: 0;
          }
          10% {
            opacity: 0.6;
          }
          50% {
            opacity: 0.5;
          }
          90% {
            opacity: 0.2;
          }
          100% {
            transform: translateY(-150px) scale(0.2);
            opacity: 0;
          }
        }

        @keyframes orbitParticle {
          0% {
            transform: rotate(0deg) translateX(150px) rotate(0deg);
          }
          100% {
            transform: rotate(360deg) translateX(150px) rotate(-360deg);
          }
        }

        @keyframes buttonBounce {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-12px);
          }
        }

        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;900&display=swap');
      `}</style>
    </main>
  );
}

