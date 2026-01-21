'use client';

import { motion } from 'framer-motion';
import { AnalysisResult } from '@/lib/api';
import { TrendingUp, Clock, Target, Shield } from 'lucide-react';

interface Props {
  result: AnalysisResult;
}

export function PredictionPanel({ result }: Props) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const { predicted_outcome, leverage_points, hospital_intel } = result;

  return (
    <div className="space-y-6">
      {/* Success Probability */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-900/80 border border-gray-800 rounded-xl p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <TrendingUp className="w-5 h-5 text-[#00ff88]" />
          <h3 className="font-semibold">Success Probability</h3>
        </div>

        <div className="relative pt-1">
          <div className="flex items-center justify-between mb-2">
            <span className="text-4xl font-bold text-[#00ff88]">
              {predicted_outcome.success_probability}%
            </span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              predicted_outcome.confidence === 'HIGH' ? 'bg-[#00ff88]/20 text-[#00ff88]' :
              predicted_outcome.confidence === 'MEDIUM' ? 'bg-[#00d4ff]/20 text-[#00d4ff]' :
              'bg-yellow-500/20 text-yellow-500'
            }`}>
              {predicted_outcome.confidence} CONFIDENCE
            </span>
          </div>

          {/* Progress bar */}
          <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${predicted_outcome.success_probability}%` }}
              transition={{ duration: 1, delay: 0.5 }}
              className="h-full bg-gradient-to-r from-[#00ff88] to-[#00d4ff] rounded-full"
            />
          </div>

          <p className="text-sm text-gray-500 mt-3">
            {predicted_outcome.confidence_explanation}
          </p>
        </div>
      </motion.div>

      {/* Expected Savings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-gradient-to-br from-[#00ff88]/20 to-transparent border border-[#00ff88]/30 rounded-xl p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <Target className="w-5 h-5 text-[#00ff88]" />
          <h3 className="font-semibold">Expected Savings</h3>
        </div>

        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-gray-400">Original Bill</span>
            <span className="text-white font-medium">{formatCurrency(predicted_outcome.original_bill)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400">Target Amount</span>
            <span className="text-[#00ff88] font-bold text-xl">{formatCurrency(predicted_outcome.target_amount)}</span>
          </div>
          <div className="border-t border-gray-700 pt-3 flex justify-between items-center">
            <span className="text-gray-400">Expected Savings</span>
            <span className="text-[#00ff88] font-bold text-2xl">
              {formatCurrency(predicted_outcome.savings_estimate.expected)}
            </span>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-gray-700/50">
          <p className="text-xs text-gray-500 mb-2">Savings Range:</p>
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Min: {formatCurrency(predicted_outcome.savings_estimate.minimum)}</span>
            <span className="text-gray-400">Max: {formatCurrency(predicted_outcome.savings_estimate.maximum)}</span>
          </div>
        </div>
      </motion.div>

      {/* Timeline */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-gray-900/80 border border-gray-800 rounded-xl p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <Clock className="w-5 h-5 text-[#00d4ff]" />
          <h3 className="font-semibold">Expected Timeline</h3>
        </div>

        <p className="text-2xl font-bold text-[#00d4ff]">{predicted_outcome.time_estimate}</p>
        <p className="text-sm text-gray-500 mt-2">
          Based on {result.recommended_strategy.primary_strategy.name} approach
        </p>
      </motion.div>

      {/* Leverage Score */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-gray-900/80 border border-gray-800 rounded-xl p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <Shield className="w-5 h-5 text-[#ff3366]" />
          <h3 className="font-semibold">Your Leverage</h3>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-4xl font-bold text-white">
            {leverage_points.total_score}
            <span className="text-lg text-gray-500">/200</span>
          </div>
          <div className={`px-3 py-1 rounded-full text-sm font-bold ${
            leverage_points.level === 'MAXIMUM' ? 'bg-[#00ff88]/20 text-[#00ff88]' :
            leverage_points.level === 'HIGH' ? 'bg-[#00d4ff]/20 text-[#00d4ff]' :
            leverage_points.level === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-500' :
            'bg-gray-500/20 text-gray-400'
          }`}>
            {leverage_points.level}
          </div>
        </div>

        <p className="text-sm text-gray-500 mt-3">{leverage_points.summary}</p>
      </motion.div>

      {/* Hospital Quick Facts */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-gray-900/80 border border-gray-800 rounded-xl p-6"
      >
        <h3 className="font-semibold mb-4">Hospital Profile</h3>

        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">Name</span>
            <span className="text-white">{hospital_intel.hospital_profile.name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Type</span>
            <span className={hospital_intel.charity_obligations.is_charitable_trust ? 'text-[#ff3366]' : 'text-white'}>
              {hospital_intel.hospital_profile.type === 'charitable_trust' ? 'Charitable Trust' : 'Private'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">NABH</span>
            <span className={hospital_intel.accreditation.nabh_accredited ? 'text-[#00ff88]' : 'text-gray-400'}>
              {hospital_intel.accreditation.nabh_accredited ? 'Accredited' : 'Not Accredited'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">CGHS</span>
            <span className={hospital_intel.accreditation.cghs_empanelled ? 'text-[#00ff88]' : 'text-gray-400'}>
              {hospital_intel.accreditation.cghs_empanelled ? 'Empanelled' : 'Not Empanelled'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Complaints (2024)</span>
            <span className={hospital_intel.complaint_history.consumer_complaints_last_year > 30 ? 'text-[#ff3366]' : 'text-white'}>
              {hospital_intel.complaint_history.consumer_complaints_last_year}
            </span>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
