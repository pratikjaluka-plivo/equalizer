'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnalysisResult } from '@/lib/api';
import { AlertTriangle, CheckCircle, Building2, TrendingDown, Heart, ThumbsUp } from 'lucide-react';

interface Props {
  result: AnalysisResult;
  onComplete: () => void;
}

type RevealStage = 'your_bill' | 'what_they_know' | 'leverage' | 'target' | 'complete';
type ValidBillStage = 'your_bill' | 'good_news' | 'complete';

export function AsymmetryReveal({ result, onComplete }: Props) {
  const [stage, setStage] = useState<RevealStage>('your_bill');
  const [validStage, setValidStage] = useState<ValidBillStage>('your_bill');

  const isValidBill = !result.price_comparison.dispute_recommended;

  // Effect for valid bills (shorter flow)
  useEffect(() => {
    if (!isValidBill) return;

    const timings: Record<ValidBillStage, number> = {
      your_bill: 2500,
      good_news: 3500,
      complete: 0,
    };

    if (validStage !== 'complete') {
      const timer = setTimeout(() => {
        const stages: ValidBillStage[] = ['your_bill', 'good_news', 'complete'];
        const currentIndex = stages.indexOf(validStage);
        if (currentIndex < stages.length - 1) {
          setValidStage(stages[currentIndex + 1]);
        }
      }, timings[validStage]);

      return () => clearTimeout(timer);
    } else {
      setTimeout(onComplete, 1500);
    }
  }, [validStage, onComplete, isValidBill]);

  // Effect for overcharged bills (full flow)
  useEffect(() => {
    if (isValidBill) return;

    const timings: Record<RevealStage, number> = {
      your_bill: 2500,
      what_they_know: 4000,
      leverage: 3500,
      target: 3000,
      complete: 0,
    };

    if (stage !== 'complete') {
      const timer = setTimeout(() => {
        const stages: RevealStage[] = ['your_bill', 'what_they_know', 'leverage', 'target', 'complete'];
        const currentIndex = stages.indexOf(stage);
        if (currentIndex < stages.length - 1) {
          setStage(stages[currentIndex + 1]);
        }
      }, timings[stage]);

      return () => clearTimeout(timer);
    } else {
      setTimeout(onComplete, 1500);
    }
  }, [stage, onComplete, isValidBill]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // VALID BILL FLOW - Different UI for fair pricing
  if (isValidBill) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-4 py-8">
        <div className="w-full max-w-6xl">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center mb-12"
          >
            <p className="text-gray-500 mb-2">
              {result.bill_data.hospital_name} • {result.bill_data.procedure_description}
            </p>
          </motion.div>

          {/* Split Screen - Your Bill + Good News */}
          <div className="grid md:grid-cols-2 gap-8">
            {/* LEFT: Your Bill */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-gray-900/80 border border-gray-700 rounded-2xl p-8"
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="w-3 h-3 rounded-full bg-gray-500" />
                <h3 className="text-xl font-semibold text-gray-400">YOUR BILL</h3>
              </div>

              <div className="space-y-6">
                <div>
                  <p className="text-gray-500 text-sm mb-1">AMOUNT DUE</p>
                  <motion.p
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 }}
                    className="text-5xl font-bold text-white"
                  >
                    {formatCurrency(result.bill_data.total_amount)}
                  </motion.p>
                </div>

                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.6 }}
                  className="pt-6 border-t border-gray-800"
                >
                  <p className="text-gray-600 text-sm">
                    {result.bill_data.hospital_city}, {result.bill_data.hospital_state}
                  </p>
                </motion.div>
              </div>
            </motion.div>

            {/* RIGHT: Good News */}
            <AnimatePresence>
              {(validStage !== 'your_bill') && (
                <motion.div
                  initial={{ opacity: 0, x: 50 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="bg-gray-900/80 border border-[#00ff88] rounded-2xl p-8 glow-green"
                >
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-3 h-3 rounded-full bg-[#00ff88] animate-pulse" />
                    <h3 className="text-xl font-semibold text-[#00ff88]">GOOD NEWS!</h3>
                  </div>

                  <div className="space-y-4">
                    {/* Fair Pricing Badge */}
                    <motion.div
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.2 }}
                      className="flex items-center justify-center py-4"
                    >
                      <div className="flex items-center gap-3 px-6 py-3 bg-[#00ff88]/20 rounded-xl">
                        <ThumbsUp className="w-8 h-8 text-[#00ff88]" />
                        <span className="text-2xl font-bold text-[#00ff88]">FAIR PRICING</span>
                      </div>
                    </motion.div>

                    {/* CGHS Rate Comparison */}
                    <motion.div
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.4 }}
                      className="flex justify-between items-center py-3 border-b border-gray-800"
                    >
                      <div>
                        <p className="text-gray-400 text-sm">CGHS Rate (Govt. Rate)</p>
                        <p className="text-xs text-gray-600">Benchmark reference</p>
                      </div>
                      <p className="text-2xl font-bold text-[#00d4ff]">
                        {formatCurrency(result.price_comparison.cghs_rate_nabh)}
                      </p>
                    </motion.div>

                    {/* Your Bill vs CGHS */}
                    <motion.div
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 }}
                      className="flex justify-between items-center py-3 border-b border-gray-800"
                    >
                      <div>
                        <p className="text-gray-400 text-sm">Your Bill Compared to CGHS</p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-[#00ff88]">
                          {result.price_comparison.overcharge_percentage <= 0 ? 'BELOW' : `+${result.price_comparison.overcharge_percentage.toFixed(0)}%`}
                        </p>
                        <p className="text-sm text-[#00ff88]">Within fair range</p>
                      </div>
                    </motion.div>

                    {/* Assessment */}
                    <motion.div
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.8 }}
                      className="flex items-start gap-3 py-3 bg-[#00ff88]/10 rounded-lg px-4"
                    >
                      <CheckCircle className="w-5 h-5 text-[#00ff88] mt-0.5" />
                      <div>
                        <p className="text-[#00ff88] font-semibold">NO OVERCHARGING DETECTED</p>
                        <p className="text-sm text-gray-400">
                          {result.price_comparison.assessment_detail}
                        </p>
                      </div>
                    </motion.div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Help Message */}
          <AnimatePresence>
            {(validStage === 'good_news' || validStage === 'complete') && (
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-8 bg-gradient-to-r from-[#00d4ff]/20 to-[#00ff88]/20 border border-[#00d4ff] rounded-2xl p-8 text-center"
              >
                <Heart className="w-12 h-12 text-[#00d4ff] mx-auto mb-4" />
                <h3 className="text-2xl font-bold mb-2">We Can Still Help You</h3>
                <p className="text-gray-400 max-w-2xl mx-auto">
                  While your bill is fairly priced, medical expenses can still be challenging.
                  We&apos;ll help you find NGOs, government schemes, and insurance options to cover the cost
                  and protect yourself for the future.
                </p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Continue Button */}
          <AnimatePresence>
            {validStage === 'complete' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-8 text-center"
              >
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={onComplete}
                  className="px-12 py-4 bg-[#00ff88] text-black font-bold text-xl rounded-lg glow-green"
                >
                  GET ASSISTANCE OPTIONS →
                </motion.button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    );
  }

  // OVERCHARGED BILL FLOW - Original UI
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-8">
      <div className="w-full max-w-6xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center mb-12"
        >
          <p className="text-gray-500 mb-2">
            {result.bill_data.hospital_name} • {result.bill_data.procedure_description}
          </p>
        </motion.div>

        {/* Split Screen Comparison */}
        <div className="grid md:grid-cols-2 gap-8">
          {/* LEFT: What You See */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-gray-900/80 border border-gray-700 rounded-2xl p-8"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-3 h-3 rounded-full bg-gray-500" />
              <h3 className="text-xl font-semibold text-gray-400">WHAT YOU SEE</h3>
            </div>

            <div className="space-y-6">
              <div>
                <p className="text-gray-500 text-sm mb-1">AMOUNT DUE</p>
                <motion.p
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.3 }}
                  className="text-5xl font-bold text-white"
                >
                  {formatCurrency(result.bill_data.total_amount)}
                </motion.p>
              </div>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6 }}
                className="pt-6 border-t border-gray-800"
              >
                <p className="text-gray-600 text-sm">
                  &quot;Payment due within 30 days to avoid collections&quot;
                </p>
              </motion.div>
            </div>
          </motion.div>

          {/* RIGHT: What They Know */}
          <AnimatePresence>
            {(stage !== 'your_bill') && (
              <motion.div
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-gray-900/80 border border-[#ff3366] rounded-2xl p-8 glow-red"
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-3 h-3 rounded-full bg-[#ff3366] animate-pulse" />
                  <h3 className="text-xl font-semibold text-[#ff3366]">WHAT THEY KNOW</h3>
                </div>

                <div className="space-y-4">
                  {/* CGHS Rate */}
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                    className="flex justify-between items-center py-3 border-b border-gray-800"
                  >
                    <div>
                      <p className="text-gray-400 text-sm">CGHS Rate (Govt. Rate)</p>
                      <p className="text-xs text-gray-600">What they accept from govt. employees</p>
                    </div>
                    <p className="text-2xl font-bold text-[#00ff88]">
                      {formatCurrency(result.price_comparison.cghs_rate_nabh)}
                    </p>
                  </motion.div>

                  {/* PMJAY Rate */}
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 }}
                    className="flex justify-between items-center py-3 border-b border-gray-800"
                  >
                    <div>
                      <p className="text-gray-400 text-sm">Ayushman Bharat Rate</p>
                      <p className="text-xs text-gray-600">What they accept under PMJAY</p>
                    </div>
                    <p className="text-2xl font-bold text-[#00ff88]">
                      {formatCurrency(result.price_comparison.pmjay_rate)}
                    </p>
                  </motion.div>

                  {/* Overcharge */}
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 }}
                    className="flex justify-between items-center py-3 border-b border-gray-800"
                  >
                    <div>
                      <p className="text-gray-400 text-sm">OVERCHARGE vs CGHS</p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-[#ff3366]">
                        +{result.price_comparison.overcharge_percentage.toFixed(0)}%
                      </p>
                      <p className="text-sm text-[#ff3366]">
                        {formatCurrency(result.price_comparison.overcharge_vs_cghs)} excess
                      </p>
                    </div>
                  </motion.div>

                  {/* Hospital Type */}
                  {result.hospital_intel.charity_obligations.is_charitable_trust && (
                    <motion.div
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.8 }}
                      className="flex items-start gap-3 py-3 bg-[#ff3366]/10 rounded-lg px-4"
                    >
                      <AlertTriangle className="w-5 h-5 text-[#ff3366] mt-0.5" />
                      <div>
                        <p className="text-[#ff3366] font-semibold">CHARITABLE TRUST</p>
                        <p className="text-sm text-gray-400">
                          Must provide subsidized care to maintain tax-exempt status
                        </p>
                      </div>
                    </motion.div>
                  )}

                  {/* CGHS Empanelled */}
                  {result.hospital_intel.accreditation.cghs_empanelled && (
                    <motion.div
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 1.0 }}
                      className="flex items-start gap-3 py-3 bg-[#00ff88]/10 rounded-lg px-4"
                    >
                      <CheckCircle className="w-5 h-5 text-[#00ff88] mt-0.5" />
                      <div>
                        <p className="text-[#00ff88] font-semibold">CGHS EMPANELLED</p>
                        <p className="text-sm text-gray-400">
                          Already accepts govt. rates for same procedures
                        </p>
                      </div>
                    </motion.div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Leverage Points */}
        <AnimatePresence>
          {(stage === 'leverage' || stage === 'target' || stage === 'complete') && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 bg-gray-900/80 border border-gray-700 rounded-2xl p-8"
            >
              <div className="flex items-center gap-3 mb-6">
                <Building2 className="w-6 h-6 text-[#00d4ff]" />
                <h3 className="text-xl font-semibold">YOUR LEVERAGE</h3>
                <span className={`ml-auto px-3 py-1 rounded-full text-sm font-bold ${
                  result.leverage_points.level === 'MAXIMUM' ? 'bg-[#00ff88]/20 text-[#00ff88]' :
                  result.leverage_points.level === 'HIGH' ? 'bg-[#00d4ff]/20 text-[#00d4ff]' :
                  'bg-yellow-500/20 text-yellow-500'
                }`}>
                  {result.leverage_points.level} LEVERAGE
                </span>
              </div>

              <div className="grid md:grid-cols-3 gap-4">
                {result.leverage_points.top_3.map((point, index) => (
                  <motion.div
                    key={point.type}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.2 }}
                    className="bg-black/50 rounded-xl p-4 border border-gray-800"
                  >
                    <div className={`text-xs font-bold mb-2 ${
                      point.severity === 'HIGH' ? 'text-[#ff3366]' : 'text-[#00d4ff]'
                    }`}>
                      {point.severity} SEVERITY
                    </div>
                    <h4 className="font-semibold mb-2">{point.title}</h4>
                    <p className="text-sm text-gray-500">{point.action}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Target Amount */}
        <AnimatePresence>
          {(stage === 'target' || stage === 'complete') && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-8 bg-gradient-to-r from-[#00ff88]/20 to-[#00d4ff]/20 border border-[#00ff88] rounded-2xl p-8 text-center glow-green"
            >
              <TrendingDown className="w-12 h-12 text-[#00ff88] mx-auto mb-4" />
              <p className="text-gray-400 mb-2">YOUR TARGET NEGOTIATION AMOUNT</p>
              <motion.p
                initial={{ scale: 0.5 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200 }}
                className="text-6xl font-bold text-[#00ff88] mb-4"
              >
                {formatCurrency(result.price_comparison.target_realistic)}
              </motion.p>
              <div className="flex justify-center gap-8 text-sm">
                <div>
                  <p className="text-gray-500">Original Bill</p>
                  <p className="text-white font-semibold">{formatCurrency(result.bill_data.total_amount)}</p>
                </div>
                <div>
                  <p className="text-gray-500">Expected Savings</p>
                  <p className="text-[#00ff88] font-semibold">
                    {formatCurrency(result.bill_data.total_amount - result.price_comparison.target_realistic)}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500">Success Rate</p>
                  <p className="text-[#00d4ff] font-semibold">{result.predicted_outcome.success_probability}%</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Continue Button */}
        <AnimatePresence>
          {stage === 'complete' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-8 text-center"
            >
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onComplete}
                className="px-12 py-4 bg-[#00ff88] text-black font-bold text-xl rounded-lg glow-green"
              >
                VIEW YOUR ARSENAL →
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
