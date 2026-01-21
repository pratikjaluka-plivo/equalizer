'use client';

import { motion } from 'framer-motion';
import { AnalysisResult } from '@/lib/api';
import {
  ExternalLink,
  FileText,
  Scale,
  CheckCircle,
  AlertTriangle,
  Gavel,
  TrendingUp,
  Award,
  Users
} from 'lucide-react';

interface Props {
  result: AnalysisResult;
}

export function EvidenceWall({ result }: Props) {
  const verification = result?.verification || { found: false, source: 'Unknown' };
  const evidence = result?.evidence || { evidence_items: [], legal_basis: [], filing_information: { district_forum: {}, state_commission: {}, online_filing: {} } };
  const court_cases = result?.court_cases || { hospital_specific_cases: [], landmark_cases: [], total_cases_found: 0, win_rate: 'N/A', search_url: '' };
  const similar_cases = result?.similar_cases || { cases: [], average_discount_achieved: 0, average_settlement: 0 };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount || 0);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Evidence Wall</h2>
        <p className="text-gray-500">Everything here is verifiable. Click any source to verify.</p>
      </div>

      {/* Hospital Verification */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`rounded-xl p-6 border ${
          verification.found
            ? 'bg-[#00ff88]/10 border-[#00ff88]/30'
            : 'bg-yellow-500/10 border-yellow-500/30'
        }`}
      >
        <div className="flex items-start gap-4">
          {verification.found ? (
            <CheckCircle className="w-8 h-8 text-[#00ff88] flex-shrink-0" />
          ) : (
            <AlertTriangle className="w-8 h-8 text-yellow-500 flex-shrink-0" />
          )}
          <div className="flex-1">
            <h3 className="font-semibold text-lg mb-2">
              {verification.found ? 'Hospital Verified' : 'Hospital Not Found in Registry'}
            </h3>
            {verification.found ? (
              <div className="space-y-2 text-sm">
                <p className="text-gray-400">
                  Status: <span className="text-[#00ff88] font-semibold">{verification.nabh_status || 'NABH Accredited'}</span>
                </p>
                <p className="text-gray-400">
                  {verification.message || 'This hospital appears in the NABH accredited list.'}
                </p>
                <a
                  href={verification.verification_url || 'https://www.nabh.co/frmSearchHospital.aspx'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-[#00ff88] hover:underline mt-2"
                >
                  <ExternalLink className="w-4 h-4" />
                  Search NABH Directory to Verify
                </a>
              </div>
            ) : (
              <div className="space-y-2 text-sm">
                <p className="text-gray-400">{verification.message}</p>
                <a
                  href="https://www.nabh.co/frmSearchHospital.aspx"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-yellow-500 hover:underline mt-2"
                >
                  <ExternalLink className="w-4 h-4" />
                  Search NABH Directory
                </a>
              </div>
            )}
          </div>
        </div>
        <p className="text-xs text-gray-600 mt-4">
          Source: {verification.source}
        </p>
      </motion.div>

      {/* Evidence Items with Sources */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-gray-900/80 border border-gray-800 rounded-xl p-6"
      >
        <div className="flex items-center gap-3 mb-6">
          <FileText className="w-6 h-6 text-[#00d4ff]" />
          <h3 className="font-semibold text-lg">Verifiable Evidence</h3>
        </div>

        <div className="space-y-4">
          {evidence.evidence_items.map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * index }}
              className="bg-black/50 rounded-lg p-4 border border-gray-800"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <p className="font-medium text-white mb-2">{item.claim}</p>
                  <p className="text-sm text-gray-500">
                    {item.document_title || item.source}
                  </p>
                  {item.calculation && (
                    <p className="text-xs text-gray-600 mt-1 font-mono">
                      {item.calculation}
                    </p>
                  )}
                </div>
                {item.source_url && (
                  <a
                    href={item.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-shrink-0 px-3 py-1 bg-[#00d4ff]/20 text-[#00d4ff] rounded-lg text-sm flex items-center gap-2 hover:bg-[#00d4ff]/30 transition-colors"
                  >
                    <ExternalLink className="w-3 h-3" />
                    View Source
                  </a>
                )}
              </div>
              {item.how_to_verify && (
                <p className="text-xs text-gray-600 mt-3 border-t border-gray-800 pt-3">
                  How to verify: {item.how_to_verify}
                </p>
              )}
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Court Cases - THE HOLY SHIT MOMENT */}
      {court_cases.hospital_specific_cases.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-[#ff3366]/10 to-transparent border border-[#ff3366]/30 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Gavel className="w-6 h-6 text-[#ff3366]" />
              <h3 className="font-semibold text-lg">Others Have Fought This Hospital - And Won</h3>
            </div>
            <div className="flex items-center gap-4 text-sm">
              <span className="text-gray-400">
                Cases Found: <span className="text-white font-bold">{court_cases.total_cases_found}</span>
              </span>
              <span className="text-gray-400">
                Win Rate: <span className="text-[#00ff88] font-bold">{court_cases.win_rate}</span>
              </span>
            </div>
          </div>

          <div className="space-y-4">
            {court_cases.hospital_specific_cases.map((case_, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + 0.1 * index }}
                className="bg-black/50 rounded-lg p-4 border border-gray-800"
              >
                <div className="flex items-start justify-between gap-4 mb-3">
                  <div>
                    <h4 className="font-medium text-white">{case_.title}</h4>
                    <p className="text-sm text-gray-500">{case_.court} • {case_.year}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    case_.outcome.includes('WON')
                      ? 'bg-[#00ff88]/20 text-[#00ff88]'
                      : 'bg-gray-500/20 text-gray-400'
                  }`}>
                    {case_.outcome}
                  </span>
                </div>

                <p className="text-sm text-gray-400 mb-3">{case_.summary}</p>

                {case_.amount_awarded && (
                  <div className="flex items-center gap-4 text-sm mb-3">
                    <span className="text-gray-500">
                      Claimed: <span className="text-white">{formatCurrency(case_.amount_claimed || 0)}</span>
                    </span>
                    <span className="text-gray-500">
                      Awarded: <span className="text-[#00ff88] font-bold">{formatCurrency(case_.amount_awarded)}</span>
                    </span>
                  </div>
                )}

                <div className="bg-[#ff3366]/10 rounded-lg p-3 mb-3">
                  <p className="text-sm text-[#ff3366]">
                    <span className="font-semibold">Key Finding:</span> {case_.key_finding}
                  </p>
                </div>

                <a
                  href={case_.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-[#00d4ff] text-sm hover:underline"
                >
                  <ExternalLink className="w-3 h-3" />
                  Read Full Judgment on Indian Kanoon
                </a>
              </motion.div>
            ))}
          </div>

          <a
            href={court_cases.search_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 mt-4 py-3 bg-[#ff3366]/20 text-[#ff3366] rounded-lg hover:bg-[#ff3366]/30 transition-colors"
          >
            <ExternalLink className="w-4 h-4" />
            Search More Cases on Indian Kanoon
          </a>
        </motion.div>
      )}

      {/* Similar Cases - Social Proof */}
      {similar_cases.cases.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gray-900/80 border border-gray-800 rounded-xl p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <Users className="w-6 h-6 text-[#00ff88]" />
            <h3 className="font-semibold text-lg">Similar Cases: What Others Got</h3>
          </div>

          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-[#00ff88]/10 rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-[#00ff88]">
                {similar_cases.average_discount_achieved}%
              </p>
              <p className="text-sm text-gray-400">Average Discount Achieved</p>
            </div>
            <div className="bg-[#00d4ff]/10 rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-[#00d4ff]">
                {formatCurrency(similar_cases.average_settlement || 0)}
              </p>
              <p className="text-sm text-gray-400">Average Final Payment</p>
            </div>
          </div>

          <div className="space-y-2">
            {similar_cases.cases.map((case_, index) => (
              <div
                key={index}
                className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0"
              >
                <div>
                  <span className="text-white">{case_.procedure}</span>
                  <span className="text-gray-500 text-sm ml-2">({case_.year})</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-gray-500 line-through">{formatCurrency(case_.billed)}</span>
                  <span className="text-[#00ff88] font-bold">{formatCurrency(case_.settled)}</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    case_.outcome === 'Consumer Court Win'
                      ? 'bg-[#ff3366]/20 text-[#ff3366]'
                      : 'bg-[#00d4ff]/20 text-[#00d4ff]'
                  }`}>
                    {case_.outcome}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Legal Basis */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-gray-900/80 border border-gray-800 rounded-xl p-6"
      >
        <div className="flex items-center gap-3 mb-6">
          <Scale className="w-6 h-6 text-[#00d4ff]" />
          <h3 className="font-semibold text-lg">Your Legal Rights</h3>
        </div>

        <div className="space-y-4">
          {evidence.legal_basis.map((law, index) => (
            <div key={index} className="flex items-start gap-4">
              <div className="w-2 h-2 rounded-full bg-[#00d4ff] mt-2 flex-shrink-0" />
              <div>
                <p className="font-medium text-white">
                  {law.law} - {law.section}
                </p>
                <p className="text-sm text-gray-400">{law.relevance}</p>
                <a
                  href={law.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-[#00d4ff] text-sm hover:underline mt-1"
                >
                  <ExternalLink className="w-3 h-3" />
                  Read the Law
                </a>
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Filing Information */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-gradient-to-br from-[#00ff88]/10 to-transparent border border-[#00ff88]/30 rounded-xl p-6"
      >
        <div className="flex items-center gap-3 mb-6">
          <Award className="w-6 h-6 text-[#00ff88]" />
          <h3 className="font-semibold text-lg">Where to File Your Complaint</h3>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-black/50 rounded-lg p-4">
            <h4 className="font-medium text-white mb-2">District Forum</h4>
            <p className="text-sm text-gray-400 mb-2">{evidence.filing_information?.district_forum?.where_to_file || 'Contact your local District Consumer Forum'}</p>
            <p className="text-xs text-gray-500 mb-2">For claims up to ₹1 Crore</p>
            <a
              href={evidence.filing_information?.district_forum?.url || 'https://e-jagriti.gov.in/'}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-[#00ff88] text-sm hover:underline"
            >
              <ExternalLink className="w-3 h-3" />
              File on e-Jagriti
            </a>
          </div>

          <div className="bg-black/50 rounded-lg p-4">
            <h4 className="font-medium text-white mb-2">File Online</h4>
            <p className="text-sm text-gray-400 mb-2">{evidence.filing_information?.online_filing?.portal || 'e-Jagriti Portal'}</p>
            <p className="text-xs text-gray-500 mb-2">{evidence.filing_information?.online_filing?.description || 'File consumer complaints online across all states'}</p>
            <a
              href={evidence.filing_information?.online_filing?.url || 'https://e-jagriti.gov.in/'}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-[#00ff88] text-sm hover:underline"
            >
              <ExternalLink className="w-3 h-3" />
              e-Jagriti Portal
            </a>
          </div>
        </div>
      </motion.div>

      {/* Disclaimer */}
      <p className="text-xs text-gray-600 text-center">
        All sources are publicly available. Click any link to verify independently.
        Court case information is from Indian Kanoon (indiankanoon.org).
        Government rates are from official CGHS and PMJAY portals.
      </p>
    </div>
  );
}
