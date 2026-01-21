'use client';

import { motion } from 'framer-motion';
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  TrendingDown,
  Scale,
  FileText,
  MessageSquare,
  ChevronRight,
  Copy,
  ExternalLink,
  IndianRupee,
  Building2,
  Activity,
  Shield,
  Target,
  Info
} from 'lucide-react';
import { useState } from 'react';

interface SmartAnalysisResultProps {
  result: {
    bill: {
      hospital_name: string;
      hospital_city: string;
      hospital_state: string;
      hospital_type: string;
      patient_name: string | null;
      primary_diagnosis: string;
      primary_procedure: string;
      total_amount: number;
      itemized_charges: Record<string, number>;
      billing_errors: Array<{ item: string; issue: string; amount: number }>;
      duplicate_charges: Array<{ item: string; occurrences: number; total_overcharge: number }>;
      suspicious_items: Array<{ item: string; concern: string; amount: number }>;
    };
    fair_price: {
      pmjay_rate: number | null;
      insurance_typical_rate: number | null;
      market_average_low: number;
      market_average_mid: number;
      market_average_high: number;
      recommended_fair_price: number;
      maximum_reasonable_price: number;
      sources: Array<{ name: string; rate: number; note: string }>;
      confidence: string;
    };
    analysis: {
      overcharge_amount: number;
      overcharge_percentage: number;
      severity: string;
      dispute_recommended: boolean;
      key_issues: Array<{ type: string; description: string; item: string; impact: number }>;
      negotiation_points: string[];
      suggested_settlement: number;
      legal_references: Array<{ act: string; relevance: string; action: string }>;
      next_steps: string[];
    };
    summary: {
      hospital: string;
      procedure: string;
      billed: number;
      fair_price: number;
      overcharge: number;
      savings_potential: number;
      action_required: boolean;
    };
  };
  onNewAnalysis: () => void;
}

export function SmartAnalysisResult({ result, onNewAnalysis }: SmartAnalysisResultProps) {
  const [copiedText, setCopiedText] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'issues' | 'action'>('overview');

  const { bill, fair_price, analysis, summary } = result;

  const severityColors: Record<string, { bg: string; text: string; border: string }> = {
    none: { bg: 'bg-green-500/10', text: 'text-green-400', border: 'border-green-500/30' },
    minor: { bg: 'bg-yellow-500/10', text: 'text-yellow-400', border: 'border-yellow-500/30' },
    moderate: { bg: 'bg-orange-500/10', text: 'text-orange-400', border: 'border-orange-500/30' },
    severe: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/30' },
    extreme: { bg: 'bg-red-600/20', text: 'text-red-300', border: 'border-red-500/50' }
  };

  const severityStyle = severityColors[analysis.severity] || severityColors.moderate;

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(label);
    setTimeout(() => setCopiedText(null), 2000);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8"
        >
          <div>
            <h1 className="text-3xl font-bold mb-2">Bill Analysis Complete</h1>
            <p className="text-gray-400">
              {bill.hospital_name} • {bill.primary_procedure}
            </p>
          </div>
          <button
            onClick={onNewAnalysis}
            className="px-4 py-2 border border-gray-700 rounded-lg hover:bg-gray-900 transition-colors"
          >
            New Analysis
          </button>
        </motion.div>

        {/* Summary Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8"
        >
          {/* Bill Amount */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
            <div className="flex items-center gap-2 text-gray-400 mb-2">
              <IndianRupee className="w-4 h-4" />
              <span className="text-sm">Your Bill</span>
            </div>
            <p className="text-2xl font-bold text-white">
              {formatCurrency(summary.billed)}
            </p>
          </div>

          {/* Fair Price */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
            <div className="flex items-center gap-2 text-gray-400 mb-2">
              <Target className="w-4 h-4" />
              <span className="text-sm">Fair Price</span>
            </div>
            <p className="text-2xl font-bold text-[#00ff88]">
              {formatCurrency(summary.fair_price)}
            </p>
          </div>

          {/* Overcharge */}
          <div className={`${severityStyle.bg} border ${severityStyle.border} rounded-xl p-4`}>
            <div className="flex items-center gap-2 text-gray-400 mb-2">
              <TrendingDown className="w-4 h-4" />
              <span className="text-sm">Overcharge</span>
            </div>
            <p className={`text-2xl font-bold ${severityStyle.text}`}>
              {formatCurrency(summary.overcharge)}
            </p>
            <p className={`text-sm ${severityStyle.text}`}>
              {analysis.overcharge_percentage.toFixed(0)}% above fair price
            </p>
          </div>

          {/* Severity */}
          <div className={`${severityStyle.bg} border ${severityStyle.border} rounded-xl p-4`}>
            <div className="flex items-center gap-2 text-gray-400 mb-2">
              <Activity className="w-4 h-4" />
              <span className="text-sm">Severity</span>
            </div>
            <p className={`text-2xl font-bold capitalize ${severityStyle.text}`}>
              {analysis.severity}
            </p>
            <p className="text-sm text-gray-400">
              {analysis.dispute_recommended ? 'Action recommended' : 'Bill is fair'}
            </p>
          </div>
        </motion.div>

        {/* Action Required Banner */}
        {analysis.dispute_recommended && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="bg-gradient-to-r from-red-500/20 to-orange-500/20 border border-red-500/30 rounded-xl p-6 mb-8"
          >
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-red-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
                <AlertTriangle className="w-6 h-6 text-red-400" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-2">
                  You are being overcharged by {formatCurrency(summary.overcharge)}
                </h3>
                <p className="text-gray-300 mb-4">
                  Based on PMJAY rates and market data, you should pay around{' '}
                  <span className="text-[#00ff88] font-semibold">
                    {formatCurrency(analysis.suggested_settlement)}
                  </span>
                  {' '}for this procedure.
                </p>
                <div className="flex flex-wrap gap-2">
                  <span className="px-3 py-1 bg-red-500/20 rounded-full text-sm text-red-300">
                    {analysis.key_issues.length} issues found
                  </span>
                  <span className="px-3 py-1 bg-orange-500/20 rounded-full text-sm text-orange-300">
                    {analysis.negotiation_points.length} negotiation points
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* No Action Required Banner */}
        {!analysis.dispute_recommended && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-xl p-6 mb-8"
          >
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
                <CheckCircle className="w-6 h-6 text-green-400" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-2">
                  Your bill appears to be fairly priced
                </h3>
                <p className="text-gray-300">
                  The charges are within the expected range for {bill.primary_procedure} at a {bill.hospital_type} hospital in {bill.hospital_city}.
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          {(['overview', 'issues', 'action'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors capitalize ${
                activeTab === tab
                  ? 'bg-[#00ff88] text-black'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {tab === 'overview' && 'Price Comparison'}
              {tab === 'issues' && `Issues (${analysis.key_issues.length})`}
              {tab === 'action' && 'What To Do'}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-6"
        >
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <>
              <div className="lg:col-span-2 space-y-6">
                {/* Price Comparison */}
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Scale className="w-5 h-5 text-[#00d4ff]" />
                    Price Comparison
                  </h3>

                  <div className="space-y-4">
                    {/* Your Bill */}
                    <div className="flex justify-between items-center py-3 border-b border-gray-800">
                      <span className="text-gray-400">Your Bill</span>
                      <span className="text-xl font-bold text-white">
                        {formatCurrency(summary.billed)}
                      </span>
                    </div>

                    {/* PMJAY Rate */}
                    {fair_price.pmjay_rate && (
                      <div className="flex justify-between items-center py-3 border-b border-gray-800">
                        <div>
                          <span className="text-gray-400">PMJAY (Ayushman Bharat) Rate</span>
                          <p className="text-xs text-gray-500">Government insurance baseline</p>
                        </div>
                        <span className="text-lg font-semibold text-blue-400">
                          {formatCurrency(fair_price.pmjay_rate)}
                        </span>
                      </div>
                    )}

                    {/* Market Rates */}
                    <div className="py-3 border-b border-gray-800">
                      <span className="text-gray-400 block mb-3">Market Rates</span>
                      <div className="grid grid-cols-3 gap-4">
                        <div className="text-center p-3 bg-gray-800/50 rounded-lg">
                          <p className="text-xs text-gray-500 mb-1">Budget</p>
                          <p className="font-semibold text-green-400">
                            {formatCurrency(fair_price.market_average_low)}
                          </p>
                        </div>
                        <div className="text-center p-3 bg-[#00ff88]/10 rounded-lg border border-[#00ff88]/30">
                          <p className="text-xs text-gray-500 mb-1">Standard</p>
                          <p className="font-semibold text-[#00ff88]">
                            {formatCurrency(fair_price.market_average_mid)}
                          </p>
                        </div>
                        <div className="text-center p-3 bg-gray-800/50 rounded-lg">
                          <p className="text-xs text-gray-500 mb-1">Premium</p>
                          <p className="font-semibold text-yellow-400">
                            {formatCurrency(fair_price.market_average_high)}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Recommended Fair Price */}
                    <div className="flex justify-between items-center py-3 bg-[#00ff88]/10 rounded-lg px-4">
                      <div>
                        <span className="text-[#00ff88] font-semibold">Recommended Fair Price</span>
                        <p className="text-xs text-gray-400">What you should pay</p>
                      </div>
                      <span className="text-2xl font-bold text-[#00ff88]">
                        {formatCurrency(fair_price.recommended_fair_price)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Itemized Charges */}
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <FileText className="w-5 h-5 text-[#00d4ff]" />
                    Bill Breakdown
                  </h3>
                  <div className="space-y-2">
                    {Object.entries(bill.itemized_charges).map(([category, amount]) => (
                      <div key={category} className="flex justify-between items-center py-2 border-b border-gray-800 last:border-0">
                        <span className="text-gray-400">{category}</span>
                        <span className="font-medium">{formatCurrency(amount)}</span>
                      </div>
                    ))}
                    <div className="flex justify-between items-center py-3 bg-gray-800 rounded-lg px-3 mt-4">
                      <span className="font-semibold">Total</span>
                      <span className="text-xl font-bold">{formatCurrency(bill.total_amount)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Side Panel */}
              <div className="space-y-6">
                {/* Hospital Info */}
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Building2 className="w-5 h-5 text-[#00d4ff]" />
                    Hospital Details
                  </h3>
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm text-gray-500">Name</p>
                      <p className="font-medium">{bill.hospital_name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Location</p>
                      <p className="font-medium">{bill.hospital_city}, {bill.hospital_state}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Type</p>
                      <p className="font-medium capitalize">{bill.hospital_type}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Procedure</p>
                      <p className="font-medium">{bill.primary_procedure}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Diagnosis</p>
                      <p className="font-medium">{bill.primary_diagnosis}</p>
                    </div>
                  </div>
                </div>

                {/* Price Sources */}
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Info className="w-5 h-5 text-[#00d4ff]" />
                    Price Sources
                  </h3>
                  <div className="space-y-3">
                    {fair_price.sources.map((source, index) => (
                      <div key={index} className="p-3 bg-gray-800/50 rounded-lg">
                        <div className="flex justify-between items-start">
                          <p className="font-medium text-sm">{source.name}</p>
                          <p className="text-[#00ff88] font-semibold">
                            {formatCurrency(source.rate)}
                          </p>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">{source.note}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </>
          )}

          {/* Issues Tab */}
          {activeTab === 'issues' && (
            <>
              <div className="lg:col-span-2 space-y-4">
                {analysis.key_issues.length === 0 ? (
                  <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-6 text-center">
                    <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold mb-2">No Major Issues Found</h3>
                    <p className="text-gray-400">Your bill appears to be clean with no obvious errors or overcharges.</p>
                  </div>
                ) : (
                  analysis.key_issues.map((issue, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`border rounded-xl p-4 ${
                        issue.type === 'overcharge'
                          ? 'bg-red-500/10 border-red-500/30'
                          : issue.type === 'duplicate_charge'
                          ? 'bg-orange-500/10 border-orange-500/30'
                          : issue.type === 'billing_error'
                          ? 'bg-yellow-500/10 border-yellow-500/30'
                          : 'bg-blue-500/10 border-blue-500/30'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                          issue.type === 'overcharge' ? 'bg-red-500/20' :
                          issue.type === 'duplicate_charge' ? 'bg-orange-500/20' :
                          issue.type === 'billing_error' ? 'bg-yellow-500/20' : 'bg-blue-500/20'
                        }`}>
                          {issue.type === 'overcharge' && <TrendingDown className="w-5 h-5 text-red-400" />}
                          {issue.type === 'duplicate_charge' && <XCircle className="w-5 h-5 text-orange-400" />}
                          {issue.type === 'billing_error' && <AlertTriangle className="w-5 h-5 text-yellow-400" />}
                          {issue.type === 'suspicious' && <Info className="w-5 h-5 text-blue-400" />}
                        </div>
                        <div className="flex-1">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-semibold capitalize">{issue.item}</p>
                              <p className="text-sm text-gray-400">{issue.description}</p>
                            </div>
                            {issue.impact > 0 && (
                              <span className="text-red-400 font-bold">
                                +{formatCurrency(issue.impact)}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))
                )}
              </div>

              {/* Billing Errors & Suspicious Items */}
              <div className="space-y-6">
                {bill.billing_errors.length > 0 && (
                  <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                    <h3 className="text-lg font-semibold mb-4 text-yellow-400">Billing Errors</h3>
                    <div className="space-y-3">
                      {bill.billing_errors.map((error, index) => (
                        <div key={index} className="p-3 bg-yellow-500/10 rounded-lg">
                          <p className="font-medium">{error.item}</p>
                          <p className="text-sm text-gray-400">{error.issue}</p>
                          {error.amount > 0 && (
                            <p className="text-yellow-400 font-semibold mt-1">
                              Impact: {formatCurrency(error.amount)}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {bill.duplicate_charges.length > 0 && (
                  <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                    <h3 className="text-lg font-semibold mb-4 text-orange-400">Duplicate Charges</h3>
                    <div className="space-y-3">
                      {bill.duplicate_charges.map((dup, index) => (
                        <div key={index} className="p-3 bg-orange-500/10 rounded-lg">
                          <p className="font-medium">{dup.item}</p>
                          <p className="text-sm text-gray-400">Charged {dup.occurrences} times</p>
                          <p className="text-orange-400 font-semibold mt-1">
                            Overcharge: {formatCurrency(dup.total_overcharge)}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </>
          )}

          {/* Action Tab */}
          {activeTab === 'action' && (
            <>
              <div className="lg:col-span-2 space-y-6">
                {/* Negotiation Points */}
                {analysis.negotiation_points.length > 0 && (
                  <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="text-lg font-semibold flex items-center gap-2">
                        <MessageSquare className="w-5 h-5 text-[#00ff88]" />
                        What To Say (Negotiation Points)
                      </h3>
                      <button
                        onClick={() => copyToClipboard(analysis.negotiation_points.join('\n\n'), 'points')}
                        className="text-sm text-gray-400 hover:text-white flex items-center gap-1"
                      >
                        <Copy className="w-4 h-4" />
                        {copiedText === 'points' ? 'Copied!' : 'Copy All'}
                      </button>
                    </div>
                    <div className="space-y-4">
                      {analysis.negotiation_points.map((point, index) => (
                        <div key={index} className="p-4 bg-[#00ff88]/10 border border-[#00ff88]/30 rounded-lg">
                          <div className="flex items-start gap-3">
                            <span className="w-6 h-6 bg-[#00ff88] text-black rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                              {index + 1}
                            </span>
                            <p className="text-gray-200">{point}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Next Steps */}
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <ChevronRight className="w-5 h-5 text-[#00d4ff]" />
                    Next Steps
                  </h3>
                  <div className="space-y-3">
                    {analysis.next_steps.map((step, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-gray-800/50 rounded-lg">
                        <span className="w-6 h-6 bg-[#00d4ff] text-black rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                          {index + 1}
                        </span>
                        <p className="text-gray-300">{step}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Legal References */}
              <div className="space-y-6">
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Shield className="w-5 h-5 text-[#00d4ff]" />
                    Legal References
                  </h3>
                  <div className="space-y-4">
                    {analysis.legal_references.map((ref, index) => (
                      <div key={index} className="p-3 bg-gray-800/50 rounded-lg">
                        <p className="font-semibold text-[#00d4ff]">{ref.act}</p>
                        <p className="text-sm text-gray-400 mt-1">{ref.relevance}</p>
                        <p className="text-sm text-[#00ff88] mt-2">{ref.action}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Suggested Settlement */}
                <div className="bg-gradient-to-br from-[#00ff88]/20 to-[#00d4ff]/20 border border-[#00ff88]/30 rounded-xl p-6">
                  <h3 className="text-lg font-semibold mb-2">Target Settlement</h3>
                  <p className="text-3xl font-bold text-[#00ff88] mb-2">
                    {formatCurrency(analysis.suggested_settlement)}
                  </p>
                  <p className="text-sm text-gray-400">
                    This is what you should aim to pay based on fair market prices
                  </p>
                </div>

                {/* Quick Links */}
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                  <h3 className="text-lg font-semibold mb-4">File Complaint</h3>
                  <div className="space-y-2">
                    <a
                      href="https://consumerhelpline.gov.in/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between p-3 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors"
                    >
                      <span>National Consumer Helpline</span>
                      <ExternalLink className="w-4 h-4" />
                    </a>
                    <a
                      href="https://edaakhil.nic.in/edaakhil/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between p-3 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors"
                    >
                      <span>e-Jagriti (Consumer Court)</span>
                      <ExternalLink className="w-4 h-4" />
                    </a>
                    <a
                      href="https://pgportal.gov.in/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between p-3 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors"
                    >
                      <span>CPGRAMS (Grievance Portal)</span>
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              </div>
            </>
          )}
        </motion.div>
      </div>
    </div>
  );
}
