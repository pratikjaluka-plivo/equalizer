'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  CheckCircle,
  Heart,
  Building,
  Shield,
  CreditCard,
  Phone,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Sparkles,
  HandHeart,
  Landmark,
  PiggyBank,
} from 'lucide-react';

interface NGO {
  name: string;
  description: string;
  contact: string;
  website: string;
  covers: string[];
  eligibility: string;
}

interface GovernmentScheme {
  name: string;
  description: string;
  eligibility: string;
  coverage: number | string;
  website: string;
  how_to_apply: string;
  covers: string[];
  recommendation?: string;
}

interface InsurancePlan {
  name: string;
  coverage: string;
  premium_starts: string;
}

interface InsuranceOption {
  type: string;
  name: string;
  plans: InsurancePlan[];
  website: string;
  features: string[];
  why_recommended?: string;
}

interface CrowdfundingOption {
  platform: string;
  website: string;
  description: string;
  success_rate: string;
}

interface FinancialAssistance {
  bill_assessment: {
    amount: number;
    assessment: string;
    message: string;
  };
  ngos_in_city: NGO[];
  government_schemes: GovernmentScheme[];
  hospital_programs: {
    name: string;
    description: string;
    options: string[];
    contact: string;
  };
  insurance_recommendations: InsuranceOption[];
  crowdfunding_options: CrowdfundingOption[];
  immediate_actions: string[];
  future_protection: {
    message: string;
    recommendations: InsuranceOption[];
    tax_benefits: string;
  };
}

interface Props {
  hospitalName: string;
  procedure: string;
  billedAmount: number;
  fairAmount: number;
  city: string;
  financialAssistance: FinancialAssistance;
  assessmentDetail: string;
}

export function ValidBillAssistance({
  hospitalName,
  procedure,
  billedAmount,
  fairAmount,
  city,
  financialAssistance,
  assessmentDetail,
}: Props) {
  const [expandedSection, setExpandedSection] = useState<string | null>('ngos');

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gray-900 rounded-2xl border border-gray-800 overflow-hidden"
    >
      {/* Header - Good News! */}
      <div className="p-6 bg-gradient-to-r from-[#00ff88]/20 to-[#00d4ff]/20 border-b border-gray-800">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-[#00ff88] rounded-2xl flex items-center justify-center">
            <CheckCircle className="w-8 h-8 text-black" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-[#00ff88]">Good News! Your Bill is Fair</h2>
            <p className="text-gray-400">{assessmentDetail}</p>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="bg-black/30 rounded-xl p-4">
            <p className="text-sm text-gray-500">Billed Amount</p>
            <p className="text-xl font-bold text-white">₹{billedAmount.toLocaleString()}</p>
          </div>
          <div className="bg-black/30 rounded-xl p-4">
            <p className="text-sm text-gray-500">CGHS Rate</p>
            <p className="text-xl font-bold text-[#00d4ff]">₹{fairAmount.toLocaleString()}</p>
          </div>
          <div className="bg-black/30 rounded-xl p-4">
            <p className="text-sm text-gray-500">Status</p>
            <p className="text-xl font-bold text-[#00ff88]">FAIR PRICING</p>
          </div>
        </div>
      </div>

      {/* Help Message */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-start gap-3 p-4 bg-[#00d4ff]/10 border border-[#00d4ff]/30 rounded-xl">
          <Heart className="w-6 h-6 text-[#00d4ff] flex-shrink-0 mt-1" />
          <div>
            <h3 className="font-semibold text-[#00d4ff]">We Can Still Help You</h3>
            <p className="text-gray-400 text-sm mt-1">
              While this bill is fairly priced, medical expenses can still be challenging.
              Here are resources to help cover the cost and protect yourself in the future.
            </p>
          </div>
        </div>
      </div>

      {/* Immediate Actions */}
      <div className="p-6 border-b border-gray-800">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-yellow-500" />
          Immediate Steps to Take
        </h3>
        <div className="space-y-2">
          {financialAssistance.immediate_actions.map((action, index) => (
            <div key={index} className="flex items-start gap-3 p-3 bg-gray-800/50 rounded-lg">
              <span className="w-6 h-6 bg-yellow-500/20 text-yellow-500 rounded-full flex items-center justify-center text-sm font-bold">
                {index + 1}
              </span>
              <span className="text-gray-300">{action}</span>
            </div>
          ))}
        </div>
      </div>

      {/* NGOs Section */}
      <div className="border-b border-gray-800">
        <button
          onClick={() => toggleSection('ngos')}
          className="w-full p-6 flex items-center justify-between hover:bg-gray-800/50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#ff6b3d]/20 rounded-lg flex items-center justify-center">
              <HandHeart className="w-5 h-5 text-[#ff6b3d]" />
            </div>
            <div className="text-left">
              <h3 className="font-semibold">NGOs & Charitable Organizations</h3>
              <p className="text-sm text-gray-500">{financialAssistance.ngos_in_city.length} organizations in {city}</p>
            </div>
          </div>
          {expandedSection === 'ngos' ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </button>

        {expandedSection === 'ngos' && (
          <div className="px-6 pb-6 space-y-3">
            {financialAssistance.ngos_in_city.map((ngo, index) => (
              <div key={index} className="p-4 bg-gray-800/50 rounded-xl">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-semibold text-white">{ngo.name}</h4>
                  <a
                    href={ngo.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[#00d4ff] hover:underline text-sm flex items-center gap-1"
                  >
                    Visit <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
                <p className="text-sm text-gray-400 mb-2">{ngo.description}</p>
                <div className="flex flex-wrap gap-2 mb-2">
                  {ngo.covers.map((item, i) => (
                    <span key={i} className="px-2 py-1 bg-[#ff6b3d]/20 text-[#ff6b3d] text-xs rounded">
                      {item}
                    </span>
                  ))}
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <span className="flex items-center gap-1 text-gray-500">
                    <Phone className="w-3 h-3" /> {ngo.contact}
                  </span>
                  <span className="text-gray-500">Eligibility: {ngo.eligibility}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Government Schemes Section */}
      <div className="border-b border-gray-800">
        <button
          onClick={() => toggleSection('schemes')}
          className="w-full p-6 flex items-center justify-between hover:bg-gray-800/50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#00ff88]/20 rounded-lg flex items-center justify-center">
              <Landmark className="w-5 h-5 text-[#00ff88]" />
            </div>
            <div className="text-left">
              <h3 className="font-semibold">Government Health Schemes</h3>
              <p className="text-sm text-gray-500">Free/subsidized healthcare coverage</p>
            </div>
          </div>
          {expandedSection === 'schemes' ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </button>

        {expandedSection === 'schemes' && (
          <div className="px-6 pb-6 space-y-3">
            {financialAssistance.government_schemes.map((scheme, index) => (
              <div key={index} className="p-4 bg-gray-800/50 rounded-xl">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-semibold text-white">{scheme.name}</h4>
                  <span className="px-2 py-1 bg-[#00ff88]/20 text-[#00ff88] text-xs rounded">
                    Up to ₹{typeof scheme.coverage === 'number' ? (scheme.coverage / 100000).toFixed(0) + 'L' : scheme.coverage}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mb-2">{scheme.description}</p>
                {scheme.recommendation && (
                  <p className="text-sm text-[#00d4ff] mb-2">{scheme.recommendation}</p>
                )}
                <div className="text-sm text-gray-500 space-y-1">
                  <p><span className="text-gray-400">Eligibility:</span> {scheme.eligibility}</p>
                  <p><span className="text-gray-400">How to Apply:</span> {scheme.how_to_apply}</p>
                </div>
                <a
                  href={scheme.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-2 inline-flex items-center gap-1 text-[#00d4ff] hover:underline text-sm"
                >
                  Apply Now <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Insurance Section */}
      <div className="border-b border-gray-800">
        <button
          onClick={() => toggleSection('insurance')}
          className="w-full p-6 flex items-center justify-between hover:bg-gray-800/50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#00d4ff]/20 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-[#00d4ff]" />
            </div>
            <div className="text-left">
              <h3 className="font-semibold">Future Protection - Insurance</h3>
              <p className="text-sm text-gray-500">Protect yourself from future medical expenses</p>
            </div>
          </div>
          {expandedSection === 'insurance' ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </button>

        {expandedSection === 'insurance' && (
          <div className="px-6 pb-6">
            <div className="p-4 bg-[#00ff88]/10 border border-[#00ff88]/30 rounded-xl mb-4">
              <p className="text-sm text-[#00ff88]">
                <strong>Tax Benefit:</strong> {financialAssistance.future_protection.tax_benefits}
              </p>
            </div>
            <div className="space-y-3">
              {financialAssistance.insurance_recommendations.slice(0, 4).map((insurance, index) => (
                <div key={index} className="p-4 bg-gray-800/50 rounded-xl">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-semibold text-white">{insurance.name}</h4>
                      <span className="text-xs text-gray-500 uppercase">{insurance.type.replace('_', ' ')}</span>
                    </div>
                    <a
                      href={insurance.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#00d4ff] hover:underline text-sm flex items-center gap-1"
                    >
                      Get Quote <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                  <div className="space-y-2 mb-2">
                    {insurance.plans.map((plan, i) => (
                      <div key={i} className="flex justify-between text-sm">
                        <span className="text-gray-400">{plan.name}</span>
                        <span className="text-gray-300">{plan.coverage} | From {plan.premium_starts}</span>
                      </div>
                    ))}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {insurance.features.slice(0, 3).map((feature, i) => (
                      <span key={i} className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded">
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Crowdfunding Section */}
      <div className="border-b border-gray-800">
        <button
          onClick={() => toggleSection('crowdfunding')}
          className="w-full p-6 flex items-center justify-between hover:bg-gray-800/50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
              <PiggyBank className="w-5 h-5 text-purple-500" />
            </div>
            <div className="text-left">
              <h3 className="font-semibold">Crowdfunding Options</h3>
              <p className="text-sm text-gray-500">Raise funds from community support</p>
            </div>
          </div>
          {expandedSection === 'crowdfunding' ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </button>

        {expandedSection === 'crowdfunding' && (
          <div className="px-6 pb-6 space-y-3">
            {financialAssistance.crowdfunding_options.map((option, index) => (
              <div key={index} className="p-4 bg-gray-800/50 rounded-xl flex items-center justify-between">
                <div>
                  <h4 className="font-semibold text-white">{option.platform}</h4>
                  <p className="text-sm text-gray-400">{option.description}</p>
                  <p className="text-xs text-purple-400 mt-1">{option.success_rate}</p>
                </div>
                <a
                  href={option.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 bg-purple-500/20 text-purple-400 rounded-lg hover:bg-purple-500/30 transition-colors text-sm"
                >
                  Start Campaign
                </a>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Hospital Payment Plans */}
      <div className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-gray-700 rounded-lg flex items-center justify-center">
            <Building className="w-5 h-5 text-gray-400" />
          </div>
          <div>
            <h3 className="font-semibold">{financialAssistance.hospital_programs.name}</h3>
            <p className="text-sm text-gray-500">{financialAssistance.hospital_programs.description}</p>
          </div>
        </div>
        <div className="space-y-2">
          {financialAssistance.hospital_programs.options.map((option, index) => (
            <div key={index} className="flex items-center gap-2 text-sm text-gray-400">
              <CreditCard className="w-4 h-4 text-gray-500" />
              {option}
            </div>
          ))}
        </div>
        <p className="text-sm text-gray-500 mt-3">
          Contact: {financialAssistance.hospital_programs.contact}
        </p>
      </div>
    </motion.div>
  );
}
