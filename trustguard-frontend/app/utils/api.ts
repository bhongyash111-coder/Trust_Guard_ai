const API_URL = (process.env.NEXT_PUBLIC_API_URL as string) || 'http://localhost:8081';
// Debug: log the resolved API URL in the browser console for verification
if (typeof window !== 'undefined') {
    // eslint-disable-next-line no-console
    console.debug('TrustGuard API URL:', API_URL);
}

// Type Definitions
export interface AnalyzeResponse {
    trust_score: number;
    label: string;
    reasons: string[];
    recommended_action: string;
}

export interface CompanyInfo {
    domain: string;
    company_name: string;
    description: string;
    emails: string[];
    phones: string[];
    social_media: {
        linkedin: boolean;
        twitter: boolean;
        facebook: boolean;
    };
    has_contact_info: boolean;

    // New enhanced fields
    industry?: string;
    employee_count?: string;
    company_type?: string;
    revenue?: string;
    location?: string;
    founding_year?: string;
    tagline?: string;
    social_media_stats?: Array<{
        platform: string;
        url: string;
        followers: string;
    }>;
    timeline?: Array<{
        year: string;
        event: string;
    }>;
}

export interface CompanyAnalysisResponse {
    success: boolean;
    company_info: CompanyInfo | null;
    company_trust_score: number;
    legitimacy_indicators: Record<string, any>;
    risk_factors: string[];
    recommended_action: string;
}

export interface EnhancedAnalyzeResponse {
    trust_score: number;
    label: string;
    reasons: string[];
    recommended_action: string;
    company_verified: boolean;
    company_trust_score?: number;
    company_name?: string;
    company_risk_factors?: string[];
    combined_trust_score?: number;
    company_info?: CompanyInfo;
}

// API Methods
export const analyzeScam = async (jobUrl: string, jobDescription: string): Promise<AnalyzeResponse> => {
    const formData = new FormData();
    if (jobUrl) formData.append('job_url', jobUrl);
    if (jobDescription) formData.append('job_description', jobDescription);

    const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Analysis failed' }));
        throw new Error(errorData.detail || 'Analysis failed');
    }

    return await response.json();
};

export const analyzeCompany = async (companyUrl: string): Promise<CompanyAnalysisResponse> => {
    const response = await fetch(`${API_URL}/analyze/company`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ company_url: companyUrl }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Company analysis failed' }));
        throw new Error(errorData.detail || 'Company analysis failed');
    }

    return await response.json();
};

export const analyzeEnhanced = async (
    jobUrl: string,
    jobDescription: string,
    companyUrl: string
): Promise<EnhancedAnalyzeResponse> => {
    const formData = new FormData();
    if (jobUrl) formData.append('job_url', jobUrl);
    if (jobDescription) formData.append('job_description', jobDescription);
    if (companyUrl) formData.append('company_url', companyUrl);

    const response = await fetch(`${API_URL}/analyze/enhanced`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Enhanced analysis failed' }));
        throw new Error(errorData.detail || 'Enhanced analysis failed');
    }

    return await response.json();
};

export const checkFirecrawlHealth = async () => {
    const response = await fetch(`${API_URL}/health/firecrawl`);
    return await response.json();
};
