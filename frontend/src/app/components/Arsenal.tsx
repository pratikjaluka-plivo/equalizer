'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { AnalysisResult } from '@/lib/api';
import { Mail, Phone, Scale, Twitter, Copy, Check, ChevronDown, ChevronUp, Zap, AlertTriangle } from 'lucide-react';
import { LiveEscalation } from './LiveEscalation';

interface Props {
  result: AnalysisResult;
}

type TabType = 'email_billing' | 'email_admin' | 'phone' | 'legal' | 'social';

export function Arsenal({ result }: Props) {
  const [activeTab, setActiveTab] = useState<TabType>('email_billing');
  const [copied, setCopied] = useState(false);
  const [expandedPushback, setExpandedPushback] = useState<string | null>(null);
  const [showLiveEscalation, setShowLiveEscalation] = useState(false);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const tabs = [
    { id: 'email_billing' as TabType, label: 'Email to Billing', icon: Mail },
    { id: 'email_admin' as TabType, label: 'Escalation Email', icon: Mail },
    { id: 'phone' as TabType, label: 'Phone Script', icon: Phone },
    { id: 'legal' as TabType, label: 'Consumer Court', icon: Scale },
    { id: 'social' as TabType, label: 'Social Media', icon: Twitter },
  ];

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              activeTab === tab.id
                ? 'bg-[#00ff88] text-black'
                : 'bg-gray-900 text-gray-400 hover:bg-gray-800'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            <span className="text-sm font-medium">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-900/80 border border-gray-800 rounded-xl overflow-hidden"
      >
        {/* Email to Billing */}
        {activeTab === 'email_billing' && (
          <div>
            <div className="p-4 border-b border-gray-800 flex justify-between items-center">
              <div>
                <p className="text-sm text-gray-500">Subject:</p>
                <p className="font-medium">{result.scripts.email_to_billing.subject}</p>
              </div>
              <button
                onClick={() => copyToClipboard(
                  `Subject: ${result.scripts.email_to_billing.subject}\n\n${result.scripts.email_to_billing.body}`
                )}
                className="flex items-center gap-2 px-4 py-2 bg-[#00ff88]/20 text-[#00ff88] rounded-lg hover:bg-[#00ff88]/30 transition-colors"
              >
                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                {copied ? 'Copied!' : 'Copy Email'}
              </button>
            </div>
            <div className="p-6">
              <pre className="whitespace-pre-wrap text-sm text-gray-300 font-sans leading-relaxed">
                {result.scripts.email_to_billing.body}
              </pre>
            </div>
          </div>
        )}

        {/* Email to Administrator */}
        {activeTab === 'email_admin' && (
          <div>
            <div className="p-4 border-b border-gray-800 flex justify-between items-center">
              <div>
                <p className="text-sm text-gray-500">Subject:</p>
                <p className="font-medium">{result.scripts.email_to_administrator.subject}</p>
              </div>
              <button
                onClick={() => copyToClipboard(
                  `Subject: ${result.scripts.email_to_administrator.subject}\n\n${result.scripts.email_to_administrator.body}`
                )}
                className="flex items-center gap-2 px-4 py-2 bg-[#00ff88]/20 text-[#00ff88] rounded-lg hover:bg-[#00ff88]/30 transition-colors"
              >
                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                {copied ? 'Copied!' : 'Copy Email'}
              </button>
            </div>
            <div className="p-6">
              <pre className="whitespace-pre-wrap text-sm text-gray-300 font-sans leading-relaxed">
                {result.scripts.email_to_administrator.body}
              </pre>
            </div>
          </div>
        )}

        {/* Phone Script */}
        {activeTab === 'phone' && (
          <div className="p-6 space-y-6">
            {/* Opening */}
            <div>
              <h4 className="text-sm font-semibold text-[#00d4ff] mb-2">OPENING</h4>
              <p className="text-gray-300 bg-black/50 p-4 rounded-lg">
                &quot;{result.scripts.phone_script.opening}&quot;
              </p>
            </div>

            {/* Key Points */}
            <div>
              <h4 className="text-sm font-semibold text-[#00ff88] mb-2">KEY POINTS TO MAKE</h4>
              <ul className="space-y-2">
                {result.scripts.phone_script.key_points.map((point, index) => (
                  <li key={index} className="flex items-start gap-3 text-gray-300">
                    <span className="text-[#00ff88] font-bold">{index + 1}.</span>
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Pushback Responses */}
            <div>
              <h4 className="text-sm font-semibold text-[#ff3366] mb-2">IF THEY SAY...</h4>
              <div className="space-y-2">
                {Object.entries(result.scripts.phone_script.responses_to_pushback).map(([pushback, response]) => (
                  <div key={pushback} className="bg-black/50 rounded-lg overflow-hidden">
                    <button
                      onClick={() => setExpandedPushback(expandedPushback === pushback ? null : pushback)}
                      className="w-full p-4 flex justify-between items-center text-left"
                    >
                      <span className="text-[#ff3366]">&quot;{pushback}&quot;</span>
                      {expandedPushback === pushback ? (
                        <ChevronUp className="w-4 h-4 text-gray-500" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-gray-500" />
                      )}
                    </button>
                    {expandedPushback === pushback && (
                      <div className="px-4 pb-4 text-gray-300 border-t border-gray-800 pt-4">
                        <span className="text-[#00ff88]">You say:</span> &quot;{response}&quot;
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Closing */}
            <div>
              <h4 className="text-sm font-semibold text-[#00d4ff] mb-2">CLOSING</h4>
              <p className="text-gray-300 bg-black/50 p-4 rounded-lg">
                &quot;{result.scripts.phone_script.closing}&quot;
              </p>
            </div>
          </div>
        )}

        {/* Consumer Court */}
        {activeTab === 'legal' && (
          <div className="p-6 space-y-6">
            <div className="bg-[#ff3366]/10 border border-[#ff3366]/30 rounded-lg p-4">
              <p className="text-[#ff3366] font-semibold mb-2">File Complaint At:</p>
              <p className="text-gray-300">{result.scripts.consumer_complaint_draft.forum}</p>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-gray-400 mb-2">COMPLAINT SUBJECT</h4>
              <p className="text-white font-medium">{result.scripts.consumer_complaint_draft.subject}</p>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-[#ff3366] mb-2">KEY ALLEGATIONS</h4>
              <ul className="space-y-2">
                {result.scripts.consumer_complaint_draft.key_allegations.map((allegation, index) => (
                  <li key={index} className="flex items-start gap-3 text-gray-300">
                    <span className="text-[#ff3366]">•</span>
                    <span>{allegation}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-[#00ff88] mb-2">RELIEF SOUGHT</h4>
              <ul className="space-y-2">
                {result.scripts.consumer_complaint_draft.relief_sought.map((relief, index) => (
                  <li key={index} className="flex items-start gap-3 text-gray-300">
                    <span className="text-[#00ff88]">•</span>
                    <span>{relief}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-[#00d4ff] mb-2">LEGAL SECTIONS TO CITE</h4>
              <ul className="space-y-2">
                {result.scripts.consumer_complaint_draft.legal_sections.map((section, index) => (
                  <li key={index} className="text-gray-400 text-sm">
                    {section}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Social Media */}
        {activeTab === 'social' && (
          <div>
            <div className="p-4 border-b border-gray-800 flex justify-between items-center">
              <div>
                <p className="text-sm text-gray-500">Platform:</p>
                <p className="font-medium">{result.scripts.social_media_post.platform}</p>
              </div>
              <button
                onClick={() => copyToClipboard(result.scripts.social_media_post.post)}
                className="flex items-center gap-2 px-4 py-2 bg-[#00ff88]/20 text-[#00ff88] rounded-lg hover:bg-[#00ff88]/30 transition-colors"
              >
                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                {copied ? 'Copied!' : 'Copy Post'}
              </button>
            </div>
            <div className="p-6">
              <div className="bg-black/50 rounded-lg p-4">
                <pre className="whitespace-pre-wrap text-sm text-gray-300 font-sans">
                  {result.scripts.social_media_post.post}
                </pre>
              </div>
              <p className="text-xs text-gray-600 mt-4">
                Tip: Use this as a last resort or as leverage during negotiation.
                Mention that you&apos;re prepared to post this if they don&apos;t cooperate.
              </p>
            </div>
          </div>
        )}
      </motion.div>

      {/* NUCLEAR OPTION - Auto Escalation */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative overflow-hidden bg-gradient-to-r from-[#ff3366]/20 via-[#ff6633]/20 to-[#ff3366]/20 border-2 border-[#ff3366]/50 rounded-xl p-6"
      >
        {/* Animated background pulse */}
        <div className="absolute inset-0 bg-gradient-to-r from-[#ff3366]/10 to-transparent animate-pulse" />

        <div className="relative flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-[#ff3366]/30 rounded-full flex items-center justify-center animate-pulse">
              <Zap className="w-8 h-8 text-[#ff3366]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-xl font-bold text-[#ff3366]">NUCLEAR OPTION</h3>
                <span className="px-2 py-0.5 bg-[#ff3366]/30 text-[#ff3366] text-xs font-bold rounded">LIVE</span>
              </div>
              <p className="text-gray-400 text-sm mt-1">
                Launch automated escalation pipeline - emails, WhatsApp, legal filings
              </p>
              <p className="text-gray-500 text-xs mt-1 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" />
                Real actions will be taken. Watch it happen live.
              </p>
            </div>
          </div>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowLiveEscalation(true)}
            className="px-8 py-4 bg-gradient-to-r from-[#ff3366] to-[#ff6633] text-white font-bold rounded-xl shadow-lg shadow-[#ff3366]/30 hover:shadow-[#ff3366]/50 transition-all"
          >
            <span className="flex items-center gap-2">
              <Zap className="w-5 h-5" />
              LAUNCH ESCALATION
            </span>
          </motion.button>
        </div>
      </motion.div>

      {/* Recommended Strategy */}
      <div className="bg-gradient-to-r from-[#00d4ff]/10 to-[#00ff88]/10 border border-[#00d4ff]/30 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4">Recommended Approach</h3>
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 bg-[#00ff88]/20 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-2xl font-bold text-[#00ff88]">1</span>
          </div>
          <div>
            <h4 className="font-semibold text-[#00ff88]">{result.recommended_strategy.primary_strategy.name}</h4>
            <p className="text-gray-400 text-sm mt-1">{result.recommended_strategy.primary_strategy.description}</p>
            <div className="flex gap-4 mt-3 text-sm">
              <span className="text-gray-500">
                Success: <span className="text-white">{result.recommended_strategy.primary_strategy.success_rate}%</span>
              </span>
              <span className="text-gray-500">
                Time: <span className="text-white">{result.recommended_strategy.primary_strategy.time_to_resolution}</span>
              </span>
            </div>
          </div>
        </div>

        {result.recommended_strategy.alternative_strategies.length > 0 && (
          <div className="mt-6 pt-6 border-t border-gray-800">
            <p className="text-sm text-gray-500 mb-3">If that doesn&apos;t work:</p>
            <div className="flex flex-wrap gap-3">
              {result.recommended_strategy.alternative_strategies.map((strategy, index) => (
                <div key={index} className="bg-black/50 px-4 py-2 rounded-lg text-sm">
                  <span className="text-gray-400">{index + 2}.</span>{' '}
                  <span className="text-white">{strategy.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Live Escalation Modal */}
      {showLiveEscalation && (
        <LiveEscalation
          hospitalName={result.hospital_intel.hospital_profile.name}
          hospitalCity={result.hospital_intel.hospital_profile.city}
          procedure={result.bill_data.procedure_description}
          billedAmount={result.bill_data.total_amount}
          fairAmount={result.price_comparison.cghs_rate_nabh || result.price_comparison.fair_market_mid}
          onClose={() => setShowLiveEscalation(false)}
        />
      )}
    </div>
  );
}
