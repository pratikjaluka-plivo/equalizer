'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BillInput } from './components/BillInput';
import { AsymmetryReveal } from './components/AsymmetryReveal';
import { Arsenal } from './components/Arsenal';
import { PredictionPanel } from './components/PredictionPanel';
import { EvidenceWall } from './components/EvidenceWall';
import { ValidBillAssistance } from './components/ValidBillAssistance';
import { NegotiationArena } from './components/NegotiationArena';
import { SmartBillUpload } from './components/SmartBillUpload';
import { SmartAnalysisResult } from './components/SmartAnalysisResult';
import { analyzeBill, AnalysisResult, BillInput as BillInputType } from '@/lib/api';
import { Shield, Zap, Target, FileCheck, Swords, Heart, Video } from 'lucide-react';

type Stage = 'intro' | 'input' | 'analyzing' | 'reveal' | 'arsenal' | 'smart-upload' | 'smart-result';
type ArsenalTab = 'evidence' | 'weapons';

export default function Home() {
  const [stage, setStage] = useState<Stage>('intro');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [smartResult, setSmartResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [arsenalTab, setArsenalTab] = useState<ArsenalTab>('evidence');
  const [showNegotiationArena, setShowNegotiationArena] = useState(false);

  const handleStartClick = () => {
    setStage('input');
  };

  const handleBillSubmit = async (bill: BillInputType) => {
    setStage('analyzing');
    setError(null);

    try {
      const result = await analyzeBill(bill);
      setAnalysisResult(result);

      // Dramatic pause before reveal
      setTimeout(() => {
        setStage('reveal');
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
      setStage('input');
    }
  };

  const handleRevealComplete = () => {
    setStage('arsenal');
  };

  const handleReset = () => {
    setStage('intro');
    setAnalysisResult(null);
    setSmartResult(null);
    setError(null);
  };

  const handleSmartUploadClick = () => {
    setStage('smart-upload');
  };

  const handleSmartAnalysisComplete = (result: any) => {
    setSmartResult(result);
    setStage('smart-result');
  };

  return (
    <main className="min-h-screen bg-black text-white overflow-hidden">
      <AnimatePresence mode="wait">
        {/* INTRO STAGE */}
        {stage === 'intro' && (
          <motion.div
            key="intro"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="min-h-screen flex flex-col items-center justify-center px-4"
          >
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-center max-w-4xl"
            >
              {/* Stats */}
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="text-gray-500 text-lg mb-8 tracking-wider"
              >
                INDIAN HEALTHCARE SYSTEM
              </motion.p>

              {/* Dramatic stat */}
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.8, duration: 0.5 }}
                className="mb-8"
              >
                <span className="text-6xl md:text-8xl font-bold text-[#ff3366]">
                  ₹47,000 Cr
                </span>
              </motion.div>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.2 }}
                className="text-xl md:text-2xl text-gray-400 mb-4"
              >
                Lost to medical overcharging every year
              </motion.p>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.5 }}
                className="text-lg text-gray-500 mb-16"
              >
                The #1 cause of debt in India
              </motion.p>

              {/* Title */}
              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.8 }}
                className="text-5xl md:text-7xl font-bold mb-6"
              >
                THE <span className="text-[#00ff88]">EQUALIZER</span>
              </motion.h1>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 2.1 }}
                className="text-xl text-gray-400 mb-12"
              >
                Every negotiation you&apos;ve lost, you lost because they knew more than you.
                <br />
                <span className="text-white font-semibold">Not anymore.</span>
              </motion.p>

              {/* Features */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 2.4 }}
                className="flex flex-wrap justify-center gap-8 mb-12"
              >
                <div className="flex items-center gap-2 text-gray-400">
                  <Shield className="w-5 h-5 text-[#00ff88]" />
                  <span>CGHS/PMJAY Rates</span>
                </div>
                <div className="flex items-center gap-2 text-gray-400">
                  <Zap className="w-5 h-5 text-[#00d4ff]" />
                  <span>Hospital Vulnerabilities</span>
                </div>
                <div className="flex items-center gap-2 text-gray-400">
                  <Target className="w-5 h-5 text-[#ff3366]" />
                  <span>Negotiation Scripts</span>
                </div>
              </motion.div>

              {/* CTA */}
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 2.7 }}
              >
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleStartClick}
                  className="px-12 py-4 bg-[#00ff88] text-black font-bold text-xl rounded-lg glow-green hover:bg-[#00dd77] transition-colors"
                >
                  ANALYZE YOUR BILL →
                </motion.button>
              </motion.div>
            </motion.div>
          </motion.div>
        )}

        {/* INPUT STAGE */}
        {stage === 'input' && (
          <motion.div
            key="input"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="min-h-screen flex items-center justify-center px-4 py-12"
          >
            <div className="w-full max-w-2xl">
              <motion.h2
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-3xl font-bold mb-2 text-center"
              >
                Enter Your Bill Details
              </motion.h2>
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="text-gray-500 text-center mb-8"
              >
                We&apos;ll find everything they don&apos;t want you to know
              </motion.p>

              {error && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="bg-red-900/30 border border-red-500 text-red-300 px-4 py-3 rounded-lg mb-6"
                >
                  {error}
                </motion.div>
              )}

              <BillInput onSubmit={handleBillSubmit} />
            </div>
          </motion.div>
        )}

        {/* ANALYZING STAGE */}
        {stage === 'analyzing' && (
          <motion.div
            key="analyzing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="min-h-screen flex flex-col items-center justify-center"
          >
            <motion.div
              animate={{
                scale: [1, 1.2, 1],
                opacity: [1, 0.5, 1],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
              className="w-24 h-24 rounded-full border-4 border-[#00ff88] mb-8"
            />
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-2xl text-gray-400 mb-6"
            >
              Building your case...
            </motion.p>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="text-center space-y-3"
            >
              <motion.p
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className="text-gray-500 flex items-center gap-2"
              >
                <span className="text-[#00ff88]">✓</span> Verifying hospital with NABH registry...
              </motion.p>
              <motion.p
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.8 }}
                className="text-gray-500 flex items-center gap-2"
              >
                <span className="text-[#00ff88]">✓</span> Comparing CGHS & PMJAY government rates...
              </motion.p>
              <motion.p
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1.1 }}
                className="text-gray-500 flex items-center gap-2"
              >
                <span className="text-[#00ff88]">✓</span> Searching Indian Kanoon for court cases...
              </motion.p>
              <motion.p
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1.4 }}
                className="text-gray-500 flex items-center gap-2"
              >
                <span className="text-[#00ff88]">✓</span> Finding similar case outcomes...
              </motion.p>
              <motion.p
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1.7 }}
                className="text-gray-500 flex items-center gap-2"
              >
                <span className="text-[#00ff88]">✓</span> Building bulletproof evidence package...
              </motion.p>
            </motion.div>
          </motion.div>
        )}

        {/* REVEAL STAGE */}
        {stage === 'reveal' && analysisResult && (
          <motion.div
            key="reveal"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="min-h-screen"
          >
            <AsymmetryReveal
              result={analysisResult}
              onComplete={handleRevealComplete}
            />
          </motion.div>
        )}

        {/* ARSENAL STAGE */}
        {stage === 'arsenal' && analysisResult && (
          <motion.div
            key="arsenal"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="min-h-screen p-4 md:p-8"
          >
            <div className="max-w-7xl mx-auto">
              {/* Check if bill is valid/fair - show assistance instead of weapons */}
              {!analysisResult.price_comparison.dispute_recommended ? (
                <>
                  {/* Header for valid bills */}
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-[#00ff88]/20 rounded-xl flex items-center justify-center">
                        <Heart className="w-6 h-6 text-[#00ff88]" />
                      </div>
                      <div>
                        <h1 className="text-2xl font-bold">Bill Analysis Complete</h1>
                        <p className="text-gray-500">Your bill is fairly priced - here&apos;s how we can help</p>
                      </div>
                    </div>
                    <button
                      onClick={handleReset}
                      className="px-4 py-2 border border-gray-700 rounded-lg hover:bg-gray-900 transition-colors"
                    >
                      New Analysis
                    </button>
                  </div>

                  {/* Valid Bill Assistance Component */}
                  {analysisResult.financial_assistance && (
                    <ValidBillAssistance
                      hospitalName={analysisResult.bill_data.hospital_name}
                      procedure={analysisResult.bill_data.procedure_description}
                      billedAmount={analysisResult.price_comparison.billed_amount}
                      fairAmount={analysisResult.price_comparison.cghs_rate_nabh}
                      city={analysisResult.bill_data.hospital_city}
                      financialAssistance={analysisResult.financial_assistance}
                      assessmentDetail={analysisResult.price_comparison.assessment_detail}
                    />
                  )}
                </>
              ) : (
                <>
                  {/* Header with main tabs - for bills needing dispute */}
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
                    <div className="flex gap-2">
                      <button
                        onClick={() => setArsenalTab('evidence')}
                        className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
                          arsenalTab === 'evidence'
                            ? 'bg-[#00ff88] text-black'
                            : 'bg-gray-900 text-gray-400 hover:bg-gray-800'
                        }`}
                      >
                        <FileCheck className="w-5 h-5" />
                        Evidence Wall
                      </button>
                      <button
                        onClick={() => setArsenalTab('weapons')}
                        className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
                          arsenalTab === 'weapons'
                            ? 'bg-[#00d4ff] text-black'
                            : 'bg-gray-900 text-gray-400 hover:bg-gray-800'
                        }`}
                      >
                        <Swords className="w-5 h-5" />
                        Your Weapons
                      </button>
                    </div>
                    <button
                      onClick={handleReset}
                      className="px-4 py-2 border border-gray-700 rounded-lg hover:bg-gray-900 transition-colors"
                    >
                      New Analysis
                    </button>
                  </div>

                  {/* Evidence Wall Tab */}
                  {arsenalTab === 'evidence' && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="grid lg:grid-cols-3 gap-8"
                    >
                      <div className="lg:col-span-2">
                        <EvidenceWall result={analysisResult} />
                      </div>
                      <div>
                        <PredictionPanel result={analysisResult} />
                        <div className="mt-6 bg-gradient-to-br from-[#00d4ff]/10 to-transparent border border-[#00d4ff]/30 rounded-xl p-6">
                          <h3 className="font-semibold text-lg mb-4">Ready to Fight?</h3>
                          <p className="text-gray-400 text-sm mb-4">
                            All evidence above is verifiable. Click any link to verify independently.
                            When you&apos;re ready, proceed to your weapons.
                          </p>
                          <button
                            onClick={() => setArsenalTab('weapons')}
                            className="w-full py-3 bg-[#00d4ff] text-black font-semibold rounded-lg hover:bg-[#00bbee] transition-colors flex items-center justify-center gap-2"
                          >
                            <Swords className="w-5 h-5" />
                            View Your Weapons
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {/* Weapons Tab */}
                  {arsenalTab === 'weapons' && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="grid lg:grid-cols-3 gap-8"
                    >
                      <div className="lg:col-span-2">
                        <Arsenal result={analysisResult} />
                      </div>
                      <div>
                        <PredictionPanel result={analysisResult} />
                      </div>
                    </motion.div>
                  )}
                </>
              )}
            </div>
          </motion.div>
        )}

        {/* SMART UPLOAD STAGE */}
        {stage === 'smart-upload' && (
          <SmartBillUpload
            onAnalysisComplete={handleSmartAnalysisComplete}
            onBack={handleReset}
          />
        )}

        {/* SMART RESULT STAGE */}
        {stage === 'smart-result' && smartResult && (
          <SmartAnalysisResult
            result={smartResult}
            onNewAnalysis={handleReset}
          />
        )}
      </AnimatePresence>

      {/* Negotiation Arena Modal */}
      {showNegotiationArena && (
        <NegotiationArena onClose={() => setShowNegotiationArena(false)} />
      )}
    </main>
  );
}
