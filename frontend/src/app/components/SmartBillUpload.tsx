'use client';

import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  FileImage,
  FileText,
  X,
  AlertCircle,
  CheckCircle,
  Building2,
  Loader2,
  Camera,
  Info
} from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface SmartAnalysisResult {
  success: boolean;
  bill: {
    hospital_name: string;
    hospital_city: string;
    hospital_state: string;
    hospital_type: string;
    patient_name: string | null;
    admission_date: string | null;
    discharge_date: string | null;
    primary_diagnosis: string;
    primary_procedure: string;
    secondary_procedures: string[];
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
}

interface SmartBillUploadProps {
  onAnalysisComplete: (result: SmartAnalysisResult) => void;
  onBack: () => void;
}

export function SmartBillUpload({ onAnalysisComplete, onBack }: SmartBillUploadProps) {
  const [hospitalName, setHospitalName] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analyzeSteps, setAnalyzeSteps] = useState<string[]>([]);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'];
      if (!validTypes.includes(selectedFile.type)) {
        setError('Please upload an image (JPG, PNG) or PDF file');
        return;
      }

      // Validate file size (max 10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }

      setFile(selectedFile);
      setError(null);

      // Create preview for images
      if (selectedFile.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => setPreview(e.target?.result as string);
        reader.readAsDataURL(selectedFile);
      } else {
        setPreview(null);
      }
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      const input = fileInputRef.current;
      if (input) {
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(droppedFile);
        input.files = dataTransfer.files;
        handleFileSelect({ target: input } as any);
      }
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please upload your bill first');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalyzeSteps([]);

    // Simulate progress steps
    const steps = [
      'Reading your bill...',
      'Extracting charges and procedures...',
      'Identifying hospital and location...',
      'Looking up fair market prices...',
      'Checking for billing errors...',
      'Analyzing overcharges...',
      'Generating negotiation strategy...'
    ];

    let stepIndex = 0;
    const stepInterval = setInterval(() => {
      if (stepIndex < steps.length) {
        setAnalyzeSteps(prev => [...prev, steps[stepIndex]]);
        stepIndex++;
      }
    }, 800);

    try {
      const formData = new FormData();
      formData.append('file', file);
      if (hospitalName.trim()) {
        formData.append('hospital_name', hospitalName.trim());
      }

      const response = await fetch(`${API_BASE}/api/smart-analyze`, {
        method: 'POST',
        body: formData,
      });

      clearInterval(stepInterval);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const result: SmartAnalysisResult = await response.json();

      // Small delay for dramatic effect
      setTimeout(() => {
        onAnalysisComplete(result);
      }, 500);

    } catch (err) {
      clearInterval(stepInterval);
      setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.');
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-2xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <button
            onClick={onBack}
            className="text-gray-500 hover:text-white transition-colors mb-4"
          >
            ← Back
          </button>

          <h2 className="text-3xl font-bold mb-2">Upload Your Bill</h2>
          <p className="text-gray-400">
            Our AI will analyze everything and tell you exactly what to do
          </p>
        </motion.div>

        {/* Info Banner */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 mb-6"
        >
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-blue-200">
              <p className="font-semibold mb-1">Works for everyone - not just government employees</p>
              <p className="text-blue-300/80">
                We use PMJAY (Ayushman Bharat) rates and market data as benchmarks.
                CGHS rates are only for govt employees, so we don&apos;t rely on them.
              </p>
            </div>
          </div>
        </motion.div>

        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-red-900/30 border border-red-500 text-red-300 px-4 py-3 rounded-lg mb-6 flex items-center gap-2"
          >
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            {error}
          </motion.div>
        )}

        {/* Hospital Name (Optional) */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-6"
        >
          <label className="block text-sm text-gray-400 mb-2">
            Hospital Name (optional - we&apos;ll extract from bill)
          </label>
          <div className="relative">
            <Building2 className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              value={hospitalName}
              onChange={(e) => setHospitalName(e.target.value)}
              placeholder="Enter hospital name to verify..."
              className="w-full bg-gray-900 border border-gray-700 rounded-xl pl-12 pr-4 py-4 text-white placeholder-gray-500 focus:outline-none focus:border-[#00ff88] transition-colors"
              disabled={isAnalyzing}
            />
          </div>
        </motion.div>

        {/* File Upload Area */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mb-6"
        >
          <label className="block text-sm text-gray-400 mb-2">
            Upload Bill (Image or PDF) <span className="text-red-400">*</span>
          </label>

          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
              file
                ? 'border-[#00ff88] bg-[#00ff88]/5'
                : 'border-gray-700 hover:border-gray-500'
            } ${isAnalyzing ? 'opacity-50 pointer-events-none' : ''}`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp,application/pdf"
              onChange={handleFileSelect}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              disabled={isAnalyzing}
            />

            {file ? (
              <div className="space-y-4">
                {preview ? (
                  <div className="relative inline-block">
                    <img
                      src={preview}
                      alt="Bill preview"
                      className="max-h-48 mx-auto rounded-lg"
                    />
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setFile(null);
                        setPreview(null);
                      }}
                      className="absolute -top-2 -right-2 bg-red-500 rounded-full p-1 hover:bg-red-600 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ) : (
                  <div className="flex items-center justify-center gap-3">
                    <FileText className="w-12 h-12 text-[#00ff88]" />
                    <div className="text-left">
                      <p className="text-white font-medium">{file.name}</p>
                      <p className="text-gray-500 text-sm">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setFile(null);
                        setPreview(null);
                      }}
                      className="ml-4 p-2 bg-red-500/20 rounded-lg hover:bg-red-500/30 transition-colors"
                    >
                      <X className="w-5 h-5 text-red-400" />
                    </button>
                  </div>
                )}
                <p className="text-[#00ff88] text-sm">Click or drag to replace</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex justify-center gap-4">
                  <div className="w-16 h-16 bg-gray-800 rounded-xl flex items-center justify-center">
                    <FileImage className="w-8 h-8 text-gray-400" />
                  </div>
                  <div className="w-16 h-16 bg-gray-800 rounded-xl flex items-center justify-center">
                    <Camera className="w-8 h-8 text-gray-400" />
                  </div>
                  <div className="w-16 h-16 bg-gray-800 rounded-xl flex items-center justify-center">
                    <FileText className="w-8 h-8 text-gray-400" />
                  </div>
                </div>
                <div>
                  <p className="text-white font-medium mb-1">
                    Drop your bill here or click to upload
                  </p>
                  <p className="text-gray-500 text-sm">
                    Supports JPG, PNG, and PDF (max 10MB)
                  </p>
                </div>
              </div>
            )}
          </div>
        </motion.div>

        {/* Analyze Button */}
        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          whileHover={{ scale: isAnalyzing ? 1 : 1.02 }}
          whileTap={{ scale: isAnalyzing ? 1 : 0.98 }}
          onClick={handleAnalyze}
          disabled={!file || isAnalyzing}
          className={`w-full py-4 rounded-xl font-bold text-lg transition-all flex items-center justify-center gap-3 ${
            !file || isAnalyzing
              ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
              : 'bg-[#00ff88] text-black hover:bg-[#00dd77]'
          }`}
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="w-6 h-6 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Upload className="w-6 h-6" />
              Analyze My Bill
            </>
          )}
        </motion.button>

        {/* Analysis Progress */}
        <AnimatePresence>
          {isAnalyzing && analyzeSteps.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-6 space-y-2"
            >
              {analyzeSteps.map((step, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center gap-2 text-gray-400"
                >
                  <CheckCircle className="w-4 h-4 text-[#00ff88]" />
                  <span>{step}</span>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
