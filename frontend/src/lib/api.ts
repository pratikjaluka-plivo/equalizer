const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface BillInput {
  hospital_name: string;
  hospital_city: string;
  hospital_state: string;
  procedure_description: string;
  total_amount: number;
  itemized_charges?: Record<string, number>;
  patient_income?: number;
  patient_state: string;
}

export interface AnalysisResult {
  bill_data: {
    hospital_name: string;
    hospital_city: string;
    hospital_state: string;
    procedure_description: string;
    total_amount: number;
    patient_income?: number;
  };
  price_comparison: {
    billed_amount: number;
    procedure_identified: string;
    procedure_description: string;
    cghs_rate_nabh: number;
    cghs_rate_non_nabh: number;
    pmjay_rate: number;
    fair_market_low: number;
    fair_market_high: number;
    fair_market_mid: number;
    overcharge_vs_cghs: number;
    overcharge_percentage: number;
    assessment: string;
    assessment_detail: string;
    dispute_recommended: boolean;
    potential_savings: number;
    target_low: number;
    target_high: number;
    target_realistic: number;
  };
  hospital_intel: {
    hospital_profile: {
      name: string;
      city: string;
      state: string;
      type: string;
      ownership: string;
      beds: number;
    };
    accreditation: {
      nabh_accredited: boolean;
      nabh_valid_until: string;
      cghs_empanelled: boolean;
      pmjay_empanelled: boolean;
    };
    complaint_history: {
      consumer_complaints_last_year: number;
      medical_council_complaints: number;
      known_issues: string[];
      recent_violations: string[];
    };
    charity_obligations: {
      has_charity_policy: boolean;
      income_limit: number;
      ews_quota: string;
      is_charitable_trust: boolean;
    };
    vulnerability_analysis: {
      score: number;
      level: string;
      points: string[];
    };
  };
  leverage_points: {
    total_score: number;
    level: string;
    summary: string;
    points: Array<{
      type: string;
      severity: string;
      score: number;
      title: string;
      detail: string;
      evidence: string;
      action: string;
    }>;
    top_3: Array<{
      type: string;
      severity: string;
      score: number;
      title: string;
      detail: string;
      evidence: string;
      action: string;
    }>;
  };
  recommended_strategy: {
    primary_strategy: {
      name: string;
      description: string;
      success_rate: number;
      typical_discount: number;
      time_to_resolution: string;
      effort_level: string;
      steps: string[];
    };
    alternative_strategies: Array<{
      name: string;
      description: string;
      success_rate: number;
    }>;
    expected_outcome: {
      original_bill: number;
      expected_discount_percentage: number;
      expected_savings: number;
      expected_final_amount: number;
      success_probability: number;
    };
    recommendation: string;
  };
  scripts: {
    email_to_billing: {
      subject: string;
      body: string;
    };
    email_to_administrator: {
      subject: string;
      body: string;
    };
    phone_script: {
      opening: string;
      key_points: string[];
      responses_to_pushback: Record<string, string>;
      closing: string;
    };
    consumer_complaint_draft: {
      forum: string;
      subject: string;
      key_allegations: string[];
      relief_sought: string[];
      legal_sections: string[];
    };
    social_media_post: {
      platform: string;
      post: string;
    };
  };
  predicted_outcome: {
    success_probability: number;
    confidence: string;
    confidence_explanation: string;
    expected_discount: {
      percentage: number;
      amount: number;
    };
    expected_final_amount: {
      low: number;
      mid: number;
      high: number;
    };
    target_amount: number;
    original_bill: number;
    savings_estimate: {
      minimum: number;
      expected: number;
      maximum: number;
    };
    time_estimate: string;
    recommendation: string;
  };
  // NEW: Bulletproof evidence
  verification: {
    found: boolean;
    verified?: boolean;
    nabh_status?: string;
    nabh_certificate?: string;
    valid_until?: string;
    verification_url?: string;
    source: string;
    source_url?: string;
    message?: string;
  };
  evidence: {
    summary: {
      billed: number;
      cghs_rate: number;
      pmjay_rate: number;
      overcharge_amount: number;
      overcharge_percentage: number;
    };
    evidence_items: Array<{
      claim: string;
      source: string;
      source_url?: string;
      document_title?: string;
      verifiable: boolean;
      how_to_verify?: string;
      calculation?: string;
    }>;
    legal_basis: Array<{
      law: string;
      section: string;
      relevance: string;
      source_url: string;
    }>;
    filing_information: {
      district_forum: {
        jurisdiction: string;
        where_to_file: string;
        fee: string;
        url: string;
      };
      state_commission: {
        jurisdiction: string;
        where_to_file: string;
        fee: string;
        url: string;
      };
      online_filing: {
        portal: string;
        url: string;
        description: string;
      };
    };
  };
  court_cases: {
    hospital_specific_cases: Array<{
      title: string;
      court: string;
      year: number;
      outcome: string;
      amount_claimed?: number;
      amount_awarded?: number;
      summary: string;
      url: string;
      key_finding: string;
    }>;
    landmark_cases: Array<{
      title: string;
      court: string;
      year: number;
      outcome: string;
      summary: string;
      url: string;
      key_finding: string;
    }>;
    total_cases_found: number;
    win_rate: string;
    average_recovery: number;
    search_url: string;
    source: string;
  };
  similar_cases: {
    cases: Array<{
      procedure: string;
      billed: number;
      settled: number;
      year: number;
      outcome: string;
    }>;
    total_similar_cases: number;
    average_discount_achieved?: number;
    average_settlement?: number;
    win_rate?: string;
    message: string;
  };
  // Financial assistance for valid bills
  financial_assistance?: {
    bill_assessment: {
      amount: number;
      assessment: string;
      message: string;
    };
    ngos_in_city: Array<{
      name: string;
      description: string;
      contact: string;
      website: string;
      covers: string[];
      eligibility: string;
    }>;
    government_schemes: Array<{
      name: string;
      description: string;
      eligibility: string;
      coverage: number | string;
      website: string;
      how_to_apply: string;
      covers: string[];
      recommendation?: string;
    }>;
    hospital_programs: {
      name: string;
      description: string;
      options: string[];
      contact: string;
    };
    insurance_recommendations: Array<{
      type: string;
      name: string;
      plans: Array<{
        name: string;
        coverage: string;
        premium_starts: string;
      }>;
      website: string;
      features: string[];
      why_recommended?: string;
    }>;
    crowdfunding_options: Array<{
      platform: string;
      website: string;
      description: string;
      success_rate: string;
    }>;
    immediate_actions: string[];
    future_protection: {
      message: string;
      recommendations: Array<{
        type: string;
        name: string;
        plans: Array<{
          name: string;
          coverage: string;
          premium_starts: string;
        }>;
        website: string;
        features: string[];
        why_recommended?: string;
      }>;
      tax_benefits: string;
    };
  };
}

export async function analyzeBill(bill: BillInput): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(bill),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/`);
    return response.ok;
  } catch {
    return false;
  }
}
