'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { BillInput as BillInputType } from '@/lib/api';

interface Props {
  onSubmit: (bill: BillInputType) => void;
}

const STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Delhi', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
  'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
  'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan',
  'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh',
  'Uttarakhand', 'West Bengal'
];

const COMMON_PROCEDURES = [
  'Appendectomy (Appendix Removal)',
  'Laparoscopic Appendectomy',
  'Cholecystectomy (Gall Bladder Removal)',
  'Laparoscopic Cholecystectomy',
  'Hernia Repair',
  'Caesarean Section (C-Section)',
  'Normal Delivery',
  'Hysterectomy',
  'Knee Replacement',
  'Hip Replacement',
  'Bypass Surgery (CABG)',
  'Angioplasty with Stent',
  'Cataract Surgery',
  'Other'
];

export function BillInput({ onSubmit }: Props) {
  const [formData, setFormData] = useState({
    hospital_name: '',
    hospital_city: '',
    hospital_state: 'Maharashtra',
    procedure_description: '',
    total_amount: '',
    patient_income: '',
    patient_state: 'Maharashtra',
  });

  const [customProcedure, setCustomProcedure] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const procedure = formData.procedure_description === 'Other'
      ? customProcedure
      : formData.procedure_description;

    onSubmit({
      ...formData,
      procedure_description: procedure,
      total_amount: parseFloat(formData.total_amount) || 0,
      patient_income: formData.patient_income ? parseFloat(formData.patient_income) : undefined,
    });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      onSubmit={handleSubmit}
      className="space-y-6"
    >
      {/* Hospital Details */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 text-[#00d4ff]">Hospital Details</h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Hospital Name *</label>
            <input
              type="text"
              name="hospital_name"
              value={formData.hospital_name}
              onChange={handleChange}
              required
              placeholder="e.g., Fortis Hospital, Apollo Hospital"
              className="w-full px-4 py-3 bg-black border border-gray-700 rounded-lg focus:border-[#00ff88] focus:outline-none transition-colors"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">City *</label>
              <input
                type="text"
                name="hospital_city"
                value={formData.hospital_city}
                onChange={handleChange}
                required
                placeholder="e.g., Mumbai, Delhi"
                className="w-full px-4 py-3 bg-black border border-gray-700 rounded-lg focus:border-[#00ff88] focus:outline-none transition-colors"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">State *</label>
              <select
                name="hospital_state"
                value={formData.hospital_state}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-black border border-gray-700 rounded-lg focus:border-[#00ff88] focus:outline-none transition-colors"
              >
                {STATES.map(state => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Bill Details */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 text-[#ff3366]">Bill Details</h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Procedure / Treatment *</label>
            <select
              name="procedure_description"
              value={formData.procedure_description}
              onChange={handleChange}
              required
              className="w-full px-4 py-3 bg-black border border-gray-700 rounded-lg focus:border-[#00ff88] focus:outline-none transition-colors"
            >
              <option value="">Select a procedure</option>
              {COMMON_PROCEDURES.map(proc => (
                <option key={proc} value={proc}>{proc}</option>
              ))}
            </select>
          </div>

          {formData.procedure_description === 'Other' && (
            <div>
              <label className="block text-sm text-gray-400 mb-2">Describe the procedure *</label>
              <input
                type="text"
                value={customProcedure}
                onChange={(e) => setCustomProcedure(e.target.value)}
                required
                placeholder="e.g., Kidney Stone Removal"
                className="w-full px-4 py-3 bg-black border border-gray-700 rounded-lg focus:border-[#00ff88] focus:outline-none transition-colors"
              />
            </div>
          )}

          <div>
            <label className="block text-sm text-gray-400 mb-2">Total Bill Amount (₹) *</label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">₹</span>
              <input
                type="number"
                name="total_amount"
                value={formData.total_amount}
                onChange={handleChange}
                required
                min="0"
                placeholder="e.g., 150000"
                className="w-full pl-8 pr-4 py-3 bg-black border border-gray-700 rounded-lg focus:border-[#00ff88] focus:outline-none transition-colors"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Patient Details (Optional) */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 text-[#00ff88]">Your Details (Optional)</h3>
        <p className="text-sm text-gray-500 mb-4">
          Helps us check if you qualify for charity care or EWS benefits
        </p>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Annual Income (₹)</label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">₹</span>
              <input
                type="number"
                name="patient_income"
                value={formData.patient_income}
                onChange={handleChange}
                min="0"
                placeholder="e.g., 500000"
                className="w-full pl-8 pr-4 py-3 bg-black border border-gray-700 rounded-lg focus:border-[#00ff88] focus:outline-none transition-colors"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-2">Your State</label>
            <select
              name="patient_state"
              value={formData.patient_state}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-black border border-gray-700 rounded-lg focus:border-[#00ff88] focus:outline-none transition-colors"
            >
              {STATES.map(state => (
                <option key={state} value={state}>{state}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Submit */}
      <motion.button
        type="submit"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full py-4 bg-[#00ff88] text-black font-bold text-lg rounded-lg glow-green hover:bg-[#00dd77] transition-colors"
      >
        ANALYZE MY BILL
      </motion.button>
    </motion.form>
  );
}
