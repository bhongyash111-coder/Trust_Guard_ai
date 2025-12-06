import React from 'react';
import { EnhancedAnalyzeResponse } from '@/app/utils/api';
import {
    ShieldCheck, ShieldAlert, ShieldX, AlertTriangle, Building2,
    MapPin, Calendar, Users, DollarSign, Briefcase, Globe,
    Linkedin, Twitter, Facebook, Link as LinkIcon
} from 'lucide-react';
import clsx from 'clsx';

interface TrustScoreProps {
    result: EnhancedAnalyzeResponse;
}

export default function TrustScore({ result }: TrustScoreProps) {
    const {
        trust_score,
        label,
        reasons,
        recommended_action,
        company_verified,
        company_trust_score,
        company_name,
        company_risk_factors,
        combined_trust_score,
        company_info
    } = result;

    // Use combined score if available, otherwise use job score
    const displayScore = combined_trust_score ?? trust_score;

    let colorClass = 'text-red-500';
    let bgClass = 'bg-red-500/10 border-red-500/20';
    let Icon = ShieldX;

    if (displayScore >= 60) {
        colorClass = 'text-green-500';
        bgClass = 'bg-green-500/10 border-green-500/20';
        Icon = ShieldCheck;
    } else if (displayScore >= 30) {
        colorClass = 'text-yellow-500';
        bgClass = 'bg-yellow-500/10 border-yellow-500/20';
        Icon = ShieldAlert;
    }

    return (
        <div className="w-full max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Main Score Card */}
            <div className={clsx("p-8 rounded-2xl border backdrop-blur-sm shadow-xl", bgClass)}>
                <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                    <div className="flex items-center gap-6">
                        <div className={clsx("p-5 rounded-full bg-slate-950/50 ring-1 ring-inset ring-white/10", colorClass)}>
                            <Icon size={56} strokeWidth={1.5} />
                        </div>
                        <div>
                            <h2 className="text-4xl font-bold text-slate-100 tracking-tight">
                                {displayScore}/100
                                {company_verified && combined_trust_score && (
                                    <span className="text-sm ml-3 font-medium text-cyan-400 bg-cyan-400/10 px-2 py-0.5 rounded-full border border-cyan-400/20">Verified Analysis</span>
                                )}
                            </h2>
                            <p className={clsx("text-xl font-medium mt-1", colorClass)}>{label}</p>
                            {company_verified && company_name && (
                                <p className="text-slate-400 mt-2 flex items-center gap-2 text-sm">
                                    <Building2 size={16} className="text-slate-500" />
                                    Verified: <span className="text-slate-200 font-medium">{company_name}</span>
                                </p>
                            )}
                        </div>
                    </div>
                    <div className="w-full md:w-auto text-center md:text-right">
                        <p className="text-xs text-slate-500 uppercase tracking-widest font-bold mb-2">Risk Level</p>
                        <div className="h-3 w-full md:w-48 bg-slate-900/50 rounded-full overflow-hidden border border-slate-800">
                            <div
                                className={clsx("h-full transition-all duration-1000 ease-out", colorClass.replace('text-', 'bg-'))}
                                style={{ width: `${displayScore}%` }}
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Company Profile Section */}
            {company_verified && company_info && (
                <div className="space-y-6">
                    <div className="flex items-center justify-between">
                        <h3 className="text-xl font-semibold text-slate-100 flex items-center gap-2">
                            <Building2 className="text-cyan-400" />
                            Company Profile
                        </h3>
                        {company_trust_score !== undefined && (
                            <div className="flex items-center gap-2 bg-slate-900/50 px-3 py-1.5 rounded-lg border border-slate-800">
                                <span className="text-sm text-slate-400">Trust Score:</span>
                                <span className={clsx(
                                    "font-bold",
                                    company_trust_score >= 70 ? "text-green-400" :
                                        company_trust_score >= 50 ? "text-yellow-400" : "text-red-400"
                                )}>{company_trust_score}/100</span>
                            </div>
                        )}
                    </div>

                    {/* Overview Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div className="bg-slate-900/40 border border-slate-800 p-4 rounded-xl">
                            <div className="flex items-center gap-2 text-slate-400 mb-1 text-xs uppercase tracking-wider font-semibold">
                                <Briefcase size={14} /> Industry
                            </div>
                            <div className="text-slate-200 font-medium truncate">{company_info.industry || 'Unknown'}</div>
                        </div>
                        <div className="bg-slate-900/40 border border-slate-800 p-4 rounded-xl">
                            <div className="flex items-center gap-2 text-slate-400 mb-1 text-xs uppercase tracking-wider font-semibold">
                                <MapPin size={14} /> Location
                            </div>
                            <div className="text-slate-200 font-medium truncate">{company_info.location || 'Unknown'}</div>
                        </div>
                        <div className="bg-slate-900/40 border border-slate-800 p-4 rounded-xl">
                            <div className="flex items-center gap-2 text-slate-400 mb-1 text-xs uppercase tracking-wider font-semibold">
                                <Calendar size={14} /> Founded
                            </div>
                            <div className="text-slate-200 font-medium">{company_info.founding_year || 'Unknown'}</div>
                        </div>
                        <div className="bg-slate-900/40 border border-slate-800 p-4 rounded-xl">
                            <div className="flex items-center gap-2 text-slate-400 mb-1 text-xs uppercase tracking-wider font-semibold">
                                <Users size={14} /> Employees
                            </div>
                            <div className="text-slate-200 font-medium">{company_info.employee_count || 'Unknown'}</div>
                        </div>
                        <div className="bg-slate-900/40 border border-slate-800 p-4 rounded-xl">
                            <div className="flex items-center gap-2 text-slate-400 mb-1 text-xs uppercase tracking-wider font-semibold">
                                <DollarSign size={14} /> Revenue
                            </div>
                            <div className="text-slate-200 font-medium">{company_info.revenue || 'Unknown'}</div>
                        </div>
                        <div className="bg-slate-900/40 border border-slate-800 p-4 rounded-xl">
                            <div className="flex items-center gap-2 text-slate-400 mb-1 text-xs uppercase tracking-wider font-semibold">
                                <Globe size={14} /> Website
                            </div>
                            <a href={`https://${company_info.domain}`} target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:underline truncate block">
                                {company_info.domain}
                            </a>
                        </div>
                    </div>

                    {/* Tagline */}
                    {company_info.tagline && (
                        <div className="bg-slate-900/30 border border-slate-800/50 p-4 rounded-xl text-center italic text-slate-400">
                            "{company_info.tagline}"
                        </div>
                    )}

                    <div className="grid md:grid-cols-2 gap-6">
                        {/* Social Media Stats */}
                        {company_info.social_media_stats && company_info.social_media_stats.length > 0 && (
                            <div className="bg-slate-900/40 border border-slate-800 rounded-xl overflow-hidden">
                                <div className="px-4 py-3 border-b border-slate-800 bg-slate-900/60">
                                    <h4 className="font-semibold text-slate-200 text-sm">Social Media Presence</h4>
                                </div>
                                <div className="divide-y divide-slate-800/50">
                                    {company_info.social_media_stats.map((stat: { platform: string; url: string; followers: string }, idx: number) => (
                                        <div key={idx} className="flex items-center justify-between px-4 py-3 hover:bg-slate-800/30 transition-colors">
                                            <div className="flex items-center gap-3">
                                                {stat.platform.toLowerCase().includes('linkedin') ? <Linkedin size={16} className="text-[#0077b5]" /> :
                                                    stat.platform.toLowerCase().includes('twitter') ? <Twitter size={16} className="text-[#1da1f2]" /> :
                                                        stat.platform.toLowerCase().includes('facebook') ? <Facebook size={16} className="text-[#1877f2]" /> :
                                                            <LinkIcon size={16} className="text-slate-500" />}
                                                <a href={stat.url} target="_blank" rel="noopener noreferrer" className="text-sm text-slate-300 hover:text-white transition-colors">
                                                    {stat.platform}
                                                </a>
                                            </div>
                                            <span className="text-xs font-mono text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                                                {stat.followers || 'N/A'}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Company Timeline */}
                        {company_info.timeline && company_info.timeline.length > 0 && (
                            <div className="bg-slate-900/40 border border-slate-800 rounded-xl overflow-hidden">
                                <div className="px-4 py-3 border-b border-slate-800 bg-slate-900/60">
                                    <h4 className="font-semibold text-slate-200 text-sm">Company Timeline</h4>
                                </div>
                                <div className="p-4 space-y-4 max-h-[300px] overflow-y-auto custom-scrollbar">
                                    {company_info.timeline.map((event: { year: string; event: string }, idx: number) => (
                                        <div key={idx} className="relative pl-4 border-l border-slate-700">
                                            <div className="absolute -left-[5px] top-1.5 w-2.5 h-2.5 rounded-full bg-slate-800 border border-slate-600"></div>
                                            <div className="text-xs font-bold text-cyan-400 mb-0.5">{event.year}</div>
                                            <div className="text-sm text-slate-300 leading-snug">{event.event}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Analysis Report & Recommendation */}
            <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
                        <AlertTriangle className="text-yellow-500" size={20} />
                        Risk Analysis
                    </h3>
                    <ul className="space-y-3">
                        {reasons.map((reason: string, idx: number) => (
                            <li key={idx} className="flex items-start gap-2 text-slate-300 text-sm group">
                                <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-yellow-500/50 group-hover:bg-yellow-400 transition-colors shrink-0" />
                                <span>{reason}</span>
                            </li>
                        ))}
                        {company_risk_factors?.map((factor: string, idx: number) => (
                            <li key={`risk-${idx}`} className="flex items-start gap-2 text-orange-300 text-sm group">
                                <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-orange-500/50 group-hover:bg-orange-400 transition-colors shrink-0" />
                                <span>{factor}</span>
                            </li>
                        ))}
                        {reasons.length === 0 && (!company_risk_factors || company_risk_factors.length === 0) && (
                            <li className="text-slate-400 italic">No specific threats detected.</li>
                        )}
                    </ul>
                </div>

                <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 flex flex-col">
                    <h3 className="text-lg font-semibold text-slate-200 mb-4">Recommendation</h3>
                    <div className="flex-1 flex items-center justify-center text-center p-6 bg-slate-950/30 rounded-lg border border-slate-800/50">
                        <p className="text-slate-100 font-medium leading-relaxed text-lg">
                            {recommended_action}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
