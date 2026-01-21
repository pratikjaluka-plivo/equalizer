'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

import {
  Zap,
  Mail,
  MessageSquare,
  FileText,
  Scale,
  Twitter,
  CheckCircle,
  Loader2,
  AlertTriangle,
  Rocket,
  Shield,
  X,
  ExternalLink,
  Camera,
  Video,
  Download,
  Share2,
} from 'lucide-react';

interface Props {
  hospitalName: string;
  hospitalCity: string;
  procedure: string;
  billedAmount: number;
  fairAmount: number;
  onClose?: () => void;
}

interface EscalationStep {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  result?: {
    message?: string;
    demo_mode?: boolean;
    twitter_intent_url?: string;
    twitter_intent_urls?: string[];
    twitter_thread?: string[];
    thread_count?: number;
  };
}

const STEP_ICONS: Record<string, React.ElementType> = {
  email_billing: Mail,
  whatsapp_notify: MessageSquare,
  email_admin: Mail,
  generate_rti: FileText,
  prepare_consumer_court: Scale,
  social_media_draft: Twitter,
};

export function LiveEscalation({
  hospitalName,
  hospitalCity,
  procedure,
  billedAmount,
  fairAmount,
  onClose,
}: Props) {
  const [stage, setStage] = useState<'confirm' | 'input' | 'running' | 'completed'>('confirm');
  const [patientName, setPatientName] = useState('');
  const [patientEmail, setPatientEmail] = useState('');
  const [patientPhone, setPatientPhone] = useState('');
  const [steps, setSteps] = useState<EscalationStep[]>([]);
  const [currentStepIndex, setCurrentStepIndex] = useState(-1);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [twitterIntentUrl, setTwitterIntentUrl] = useState<string | null>(null);
  const [twitterThread, setTwitterThread] = useState<string[]>([]);
  const [twitterThreadUrls, setTwitterThreadUrls] = useState<string[]>([]);
  const [threadVideoUrl, setThreadVideoUrl] = useState<string | null>(null);

  // Viral Video State
  const [showWebcam, setShowWebcam] = useState(false);
  const [capturedPhoto, setCapturedPhoto] = useState<string | null>(null);
  const [videoGenerating, setVideoGenerating] = useState(false);
  const [videoResult, setVideoResult] = useState<{
    video_url?: string;
    script?: string;
    twitter_text?: string;
    fallback_used?: boolean;
    error?: string;
  } | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const overcharge = billedAmount - fairAmount;
  const overchargePercent = ((overcharge / fairAmount) * 100).toFixed(0);

  const startEscalation = async () => {
    if (!patientName || !patientEmail) {
      setError('Please enter your name and email');
      return;
    }

    setStage('running');
    setError(null);

    try {
      // Start the escalation session
      const response = await fetch(`${API_BASE}/api/live-escalation/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          hospital_name: hospitalName,
          hospital_city: hospitalCity,
          procedure,
          billed_amount: billedAmount,
          fair_amount: fairAmount,
          patient_name: patientName,
          patient_email: patientEmail,
          patient_phone: patientPhone || null,
        }),
      });

      const data = await response.json();
      setSessionId(data.session_id);
      setSteps(data.steps.map((s: EscalationStep) => ({ ...s, status: 'pending' })));

      // Connect to SSE stream
      const eventSource = new EventSource(
        `${API_BASE}/api/live-escalation/${data.session_id}/stream`
      );
      eventSourceRef.current = eventSource;

      eventSource.onmessage = (event) => {
        const eventData = JSON.parse(event.data);

        if (eventData.type === 'step_starting') {
          setCurrentStepIndex(eventData.step_index);
          setSteps((prev) =>
            prev.map((step, idx) =>
              idx === eventData.step_index ? { ...step, status: 'in_progress' } : step
            )
          );
        } else if (eventData.type === 'step_completed') {
          // Check for Twitter thread data
          if (eventData.result?.result?.twitter_intent_urls) {
            setTwitterThreadUrls(eventData.result.result.twitter_intent_urls);
            setTwitterThread(eventData.result.result.twitter_thread || []);
          }
          // Fallback to single URL for backwards compatibility
          if (eventData.result?.result?.twitter_intent_url) {
            setTwitterIntentUrl(eventData.result.result.twitter_intent_url);
          }
          // Capture video URL for thread
          if (eventData.result?.result?.video_url) {
            setThreadVideoUrl(eventData.result.result.video_url);
          }
          setSteps((prev) =>
            prev.map((step, idx) =>
              idx === eventData.step_index
                ? { ...step, status: 'completed', result: eventData.result?.result }
                : step
            )
          );
        } else if (eventData.type === 'session_completed') {
          setStage('completed');
          eventSource.close();
        }
      };

      eventSource.onerror = () => {
        setError('Connection lost. Please try again.');
        eventSource.close();
      };
    } catch (err) {
      setError('Failed to start escalation. Please try again.');
      setStage('input');
    }
  };

  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  // Webcam functions
  const startWebcam = async () => {
    setShowWebcam(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: 640, height: 480 },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error('Failed to access webcam:', err);
      setError('Failed to access webcam. Please allow camera permission.');
    }
  };

  const stopWebcam = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setShowWebcam(false);
  };

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0);
        const photoData = canvas.toDataURL('image/jpeg', 0.8);
        setCapturedPhoto(photoData);
        stopWebcam();
      }
    }
  };

  const generateViralVideo = async () => {
    if (!capturedPhoto) return;

    setVideoGenerating(true);
    setError(null);

    try {
      // Extract base64 data without the data URL prefix
      const base64Photo = capturedPhoto.replace(/^data:image\/\w+;base64,/, '');

      const response = await fetch(`${API_BASE}/api/viral-video/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_photo_base64: base64Photo,
          patient_name: patientName,
          hospital_name: hospitalName,
          hospital_city: hospitalCity,
          procedure: procedure,
          billed_amount: billedAmount,
          fair_amount: fairAmount,
          overcharge_percentage: parseFloat(overchargePercent),
        }),
      });

      const data = await response.json();
      if (data.success) {
        setVideoResult(data);
      } else {
        setError(data.error || 'Video generation failed');
      }
    } catch (err) {
      console.error('Video generation error:', err);
      setError('Failed to generate video. Please try again.');
    } finally {
      setVideoGenerating(false);
    }
  };

  const downloadVideo = () => {
    if (videoResult?.video_url) {
      const link = document.createElement('a');
      link.href = videoResult.video_url;
      link.download = `equalizer-${hospitalName.replace(/\s+/g, '-')}-viral.${videoResult.fallback_used ? 'png' : 'mp4'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const shareToTwitter = () => {
    if (videoResult?.twitter_text) {
      const tweetUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(videoResult.twitter_text)}`;
      window.open(tweetUrl, '_blank');
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-gray-900 border border-gray-800 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden"
        >
          {/* Header */}
          <div className="p-6 border-b border-gray-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-[#ff3366] to-[#ff6b3d] rounded-xl flex items-center justify-center">
                <Rocket className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold">Nuclear Option</h2>
                <p className="text-sm text-gray-500">Automated Escalation Pipeline</p>
              </div>
            </div>
            {onClose && (
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            )}
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[60vh]">
            {/* Confirmation Stage */}
            {stage === 'confirm' && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                <div className="bg-[#ff3366]/10 border border-[#ff3366]/30 rounded-xl p-6 text-center">
                  <AlertTriangle className="w-12 h-12 text-[#ff3366] mx-auto mb-4" />
                  <h3 className="text-xl font-bold mb-2">This Will Launch Real Actions</h3>
                  <p className="text-gray-400">
                    Clicking &quot;Launch&quot; will automatically send emails, generate legal documents,
                    and prepare complaints against <span className="text-white font-semibold">{hospitalName}</span>.
                  </p>
                </div>

                <div className="bg-gray-800/50 rounded-xl p-4 space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Hospital</span>
                    <span className="text-white font-medium">{hospitalName}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Procedure</span>
                    <span className="text-white font-medium">{procedure}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Overcharge</span>
                    <span className="text-[#ff3366] font-bold">
                      ₹{overcharge.toLocaleString()} ({overchargePercent}%)
                    </span>
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={onClose}
                    className="flex-1 py-3 bg-gray-800 text-gray-400 rounded-xl hover:bg-gray-700 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => setStage('input')}
                    className="flex-1 py-3 bg-gradient-to-r from-[#ff3366] to-[#ff6b3d] text-white font-bold rounded-xl hover:opacity-90 transition-opacity"
                  >
                    Continue
                  </button>
                </div>
              </motion.div>
            )}

            {/* Input Stage */}
            {stage === 'input' && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                <div className="text-center mb-6">
                  <Shield className="w-12 h-12 text-[#00ff88] mx-auto mb-3" />
                  <h3 className="text-xl font-bold">Your Information</h3>
                  <p className="text-gray-500 text-sm">Required to send on your behalf</p>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Your Name *</label>
                    <input
                      type="text"
                      value={patientName}
                      onChange={(e) => setPatientName(e.target.value)}
                      placeholder="Enter your full name"
                      className="w-full px-4 py-3 bg-black border border-gray-700 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-[#00ff88]"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Your Email *</label>
                    <input
                      type="email"
                      value={patientEmail}
                      onChange={(e) => setPatientEmail(e.target.value)}
                      placeholder="your@email.com"
                      className="w-full px-4 py-3 bg-black border border-gray-700 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-[#00ff88]"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">
                      WhatsApp Number (optional)
                    </label>
                    <input
                      type="tel"
                      value={patientPhone}
                      onChange={(e) => setPatientPhone(e.target.value)}
                      placeholder="+91 98765 43210"
                      className="w-full px-4 py-3 bg-black border border-gray-700 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-[#00ff88]"
                    />
                  </div>
                </div>

                {error && (
                  <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400 text-sm">
                    {error}
                  </div>
                )}

                <button
                  onClick={startEscalation}
                  disabled={!patientName || !patientEmail}
                  className="w-full py-4 bg-gradient-to-r from-[#ff3366] to-[#ff6b3d] text-white font-bold rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
                >
                  <Zap className="w-5 h-5" />
                  LAUNCH ESCALATION
                </button>
              </motion.div>
            )}

            {/* Running Stage */}
            {stage === 'running' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-4"
              >
                <div className="text-center mb-6">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                    className="w-16 h-16 mx-auto mb-4"
                  >
                    <div className="w-full h-full rounded-full border-4 border-[#ff3366] border-t-transparent" />
                  </motion.div>
                  <h3 className="text-xl font-bold">Escalation In Progress</h3>
                  <p className="text-gray-500 text-sm">Watch the magic happen</p>
                </div>

                <div className="space-y-3">
                  {steps.map((step, index) => {
                    const Icon = STEP_ICONS[step.id] || FileText;
                    const isActive = index === currentStepIndex;
                    const isCompleted = step.status === 'completed';
                    const isPending = step.status === 'pending';

                    return (
                      <motion.div
                        key={step.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className={`p-4 rounded-xl border transition-all duration-500 ${
                          isActive
                            ? 'bg-[#ff3366]/10 border-[#ff3366] shadow-lg shadow-[#ff3366]/20'
                            : isCompleted
                            ? 'bg-[#00ff88]/10 border-[#00ff88]/50'
                            : 'bg-gray-800/50 border-gray-700'
                        }`}
                      >
                        <div className="flex items-center gap-4">
                          <div
                            className={`w-10 h-10 rounded-lg flex items-center justify-center transition-colors ${
                              isActive
                                ? 'bg-[#ff3366]'
                                : isCompleted
                                ? 'bg-[#00ff88]'
                                : 'bg-gray-700'
                            }`}
                          >
                            {isActive ? (
                              <Loader2 className="w-5 h-5 text-white animate-spin" />
                            ) : isCompleted ? (
                              <CheckCircle className="w-5 h-5 text-black" />
                            ) : (
                              <Icon className="w-5 h-5 text-gray-400" />
                            )}
                          </div>
                          <div className="flex-1">
                            <h4
                              className={`font-medium ${
                                isActive
                                  ? 'text-[#ff3366]'
                                  : isCompleted
                                  ? 'text-[#00ff88]'
                                  : 'text-gray-400'
                              }`}
                            >
                              {step.name}
                            </h4>
                            <p className="text-sm text-gray-500">
                              {isActive
                                ? step.description
                                : isCompleted && step.result?.message
                                ? step.result.message
                                : isPending
                                ? 'Waiting...'
                                : step.description}
                            </p>
                          </div>
                          {isCompleted && (
                            <motion.div
                              initial={{ scale: 0 }}
                              animate={{ scale: 1 }}
                              className="text-[#00ff88] font-bold text-sm"
                            >
                              DONE
                            </motion.div>
                          )}
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </motion.div>
            )}

            {/* Completed Stage */}
            {stage === 'completed' && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center py-8"
              >
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', duration: 0.5 }}
                  className="w-24 h-24 bg-gradient-to-br from-[#00ff88] to-[#00d4ff] rounded-full flex items-center justify-center mx-auto mb-6"
                >
                  <CheckCircle className="w-12 h-12 text-black" />
                </motion.div>

                <h3 className="text-2xl font-bold mb-2">Escalation Complete!</h3>
                <p className="text-gray-400 mb-6">
                  All actions have been executed. The hospital should respond within 48 hours.
                </p>

                <div className="bg-gray-800/50 rounded-xl p-4 mb-6">
                  <p className="text-sm text-gray-500 mb-2">Case Reference</p>
                  <p className="text-2xl font-mono font-bold text-[#00ff88]">{sessionId}</p>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="bg-[#00ff88]/10 rounded-xl p-4">
                    <p className="text-2xl font-bold text-[#00ff88]">{steps.length}</p>
                    <p className="text-xs text-gray-500">Actions Taken</p>
                  </div>
                  <div className="bg-[#00d4ff]/10 rounded-xl p-4">
                    <p className="text-2xl font-bold text-[#00d4ff]">2</p>
                    <p className="text-xs text-gray-500">Emails Sent</p>
                  </div>
                  <div className="bg-[#ff3366]/10 rounded-xl p-4">
                    <p className="text-2xl font-bold text-[#ff3366]">3</p>
                    <p className="text-xs text-gray-500">Docs Generated</p>
                  </div>
                </div>

                {/* Live Case Tracking Dashboard */}
                <div className="bg-gray-800/50 rounded-xl p-4 mb-6 text-left">
                  <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center gap-2">
                    <Scale className="w-4 h-4" />
                    LIVE CASE TRACKING
                  </h4>
                  <div className="space-y-3">
                    {/* Consumer Court Case */}
                    <div className="p-3 bg-black/50 rounded-lg border border-gray-700">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 bg-[#ff3366]/20 rounded-lg flex items-center justify-center">
                            <Scale className="w-4 h-4 text-[#ff3366]" />
                          </div>
                          <div>
                            <p className="text-sm font-medium">Consumer Court</p>
                            <p className="text-xs text-gray-500">e-Jagriti Portal</p>
                          </div>
                        </div>
                        <span className="px-2 py-1 bg-yellow-500/20 text-yellow-500 text-xs font-bold rounded">
                          FILED
                        </span>
                      </div>
                      <div className="mt-2 p-2 bg-black/30 rounded text-xs space-y-1">
                        <div className="flex justify-between">
                          <span className="text-gray-500">Case No:</span>
                          <span className="text-white font-mono">CC/{new Date().getFullYear()}/{sessionId}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Filed On:</span>
                          <span className="text-white">{new Date().toLocaleDateString('en-IN')}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Status:</span>
                          <span className="text-yellow-500">Awaiting Hospital Response</span>
                        </div>
                      </div>
                    </div>

                    {/* RTI Request */}
                    <div className="p-3 bg-black/50 rounded-lg border border-gray-700">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 bg-[#00d4ff]/20 rounded-lg flex items-center justify-center">
                            <FileText className="w-4 h-4 text-[#00d4ff]" />
                          </div>
                          <div>
                            <p className="text-sm font-medium">RTI Request</p>
                            <p className="text-xs text-gray-500">Ministry of Health</p>
                          </div>
                        </div>
                        <span className="px-2 py-1 bg-[#00d4ff]/20 text-[#00d4ff] text-xs font-bold rounded">
                          SUBMITTED
                        </span>
                      </div>
                      <div className="mt-2 p-2 bg-black/30 rounded text-xs space-y-1">
                        <div className="flex justify-between">
                          <span className="text-gray-500">Registration No:</span>
                          <span className="text-white font-mono">MOHFW/R/{sessionId?.slice(0,6)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Response Due:</span>
                          <span className="text-white">{new Date(Date.now() + 30*24*60*60*1000).toLocaleDateString('en-IN')}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Status:</span>
                          <span className="text-[#00d4ff]">Under Process</span>
                        </div>
                      </div>
                    </div>

                    {/* Email to Hospital */}
                    <div className="p-3 bg-black/50 rounded-lg border border-gray-700">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 bg-[#00ff88]/20 rounded-lg flex items-center justify-center">
                            <Mail className="w-4 h-4 text-[#00ff88]" />
                          </div>
                          <div>
                            <p className="text-sm font-medium">Hospital Billing Dept</p>
                            <p className="text-xs text-gray-500">Email Escalation</p>
                          </div>
                        </div>
                        <span className="px-2 py-1 bg-[#00ff88]/20 text-[#00ff88] text-xs font-bold rounded">
                          DELIVERED
                        </span>
                      </div>
                      <div className="mt-2 p-2 bg-black/30 rounded text-xs space-y-1">
                        <div className="flex justify-between">
                          <span className="text-gray-500">Sent To:</span>
                          <span className="text-white">billing@{hospitalName.toLowerCase().replace(/\s+/g, '')}.com</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Response Deadline:</span>
                          <span className="text-white">{new Date(Date.now() + 48*60*60*1000).toLocaleDateString('en-IN')}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Status:</span>
                          <span className="text-[#00ff88]">Awaiting Response (48hrs)</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Quick Links */}
                  <div className="mt-4 pt-3 border-t border-gray-700">
                    <p className="text-xs text-gray-500 mb-2">Verify on official portals:</p>
                    <div className="flex flex-wrap gap-2">
                      <a
                        href="https://e-jagriti.gov.in"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-[#00d4ff] hover:underline flex items-center gap-1"
                      >
                        e-Jagriti <ExternalLink className="w-3 h-3" />
                      </a>
                      <a
                        href="https://rtionline.gov.in"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-[#00d4ff] hover:underline flex items-center gap-1"
                      >
                        RTI Portal <ExternalLink className="w-3 h-3" />
                      </a>
                      <a
                        href="https://pgportal.gov.in"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-[#00d4ff] hover:underline flex items-center gap-1"
                      >
                        CPGRAMS <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  </div>
                </div>

                {/* Viral Video Generator Section */}
                <div className="bg-gradient-to-r from-purple-900/30 to-pink-900/30 border border-purple-500/30 rounded-xl p-4 mb-6 text-left">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                      <Video className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-purple-300">CREATE VIRAL VIDEO FOR X/TWITTER</h4>
                      <p className="text-xs text-gray-500">AI-generated video with your face threatening legal action</p>
                    </div>
                  </div>

                  {/* Hidden canvas for photo capture */}
                  <canvas ref={canvasRef} className="hidden" />

                  {/* Webcam Modal */}
                  {showWebcam && (
                    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
                      <div className="bg-gray-900 rounded-xl p-6 max-w-md w-full">
                        <h4 className="text-lg font-bold mb-4 text-center">Take Your Photo</h4>
                        <div className="relative rounded-lg overflow-hidden mb-4 bg-black">
                          <video
                            ref={videoRef}
                            autoPlay
                            playsInline
                            muted
                            className="w-full aspect-video object-cover"
                          />
                          <div className="absolute inset-0 border-2 border-dashed border-purple-500/50 m-4 rounded-lg pointer-events-none" />
                        </div>
                        <p className="text-xs text-gray-500 text-center mb-4">
                          Position your face in the frame. This will be used to create your viral video.
                        </p>
                        <div className="flex gap-3">
                          <button
                            onClick={stopWebcam}
                            className="flex-1 py-3 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={capturePhoto}
                            className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-lg hover:opacity-90 flex items-center justify-center gap-2"
                          >
                            <Camera className="w-4 h-4" />
                            Capture
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                  {!videoResult ? (
                    <>
                      {!capturedPhoto ? (
                        <>
                          <p className="text-sm text-gray-400 mb-4">
                            Create a powerful AI-generated video with YOUR face delivering a message that will
                            make {hospitalName} take notice. Optimized to go viral on X/Twitter.
                          </p>

                          <div className="bg-black/30 rounded-lg p-3 mb-4 space-y-2 text-xs">
                            <div className="flex items-center gap-2 text-gray-400">
                              <Video className="w-3 h-3 text-purple-400" />
                              <span>AI-generated talking avatar video</span>
                            </div>
                            <div className="flex items-center gap-2 text-gray-400">
                              <Twitter className="w-3 h-3 text-purple-400" />
                              <span>Pre-written viral tweet text included</span>
                            </div>
                            <div className="flex items-center gap-2 text-gray-400">
                              <Scale className="w-3 h-3 text-purple-400" />
                              <span>Mentions legal action & evidence</span>
                            </div>
                          </div>

                          <button
                            onClick={startWebcam}
                            className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-lg hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
                          >
                            <Camera className="w-4 h-4" />
                            TAKE PHOTO FOR VIDEO
                          </button>
                        </>
                      ) : (
                        <>
                          <div className="mb-4">
                            <p className="text-xs text-gray-500 mb-2">Your photo:</p>
                            <div className="relative rounded-lg overflow-hidden">
                              <img src={capturedPhoto} alt="Captured" className="w-full rounded-lg" />
                              <button
                                onClick={() => setCapturedPhoto(null)}
                                className="absolute top-2 right-2 p-1 bg-black/50 rounded-full hover:bg-black/70"
                              >
                                <X className="w-4 h-4 text-white" />
                              </button>
                            </div>
                          </div>

                          {error && (
                            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-4 text-sm text-red-400">
                              {error}
                            </div>
                          )}

                          <div className="flex gap-3">
                            <button
                              onClick={startWebcam}
                              className="flex-1 py-3 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600"
                            >
                              Retake
                            </button>
                            <button
                              onClick={generateViralVideo}
                              disabled={videoGenerating}
                              className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-lg hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
                            >
                              {videoGenerating ? (
                                <>
                                  <Loader2 className="w-4 h-4 animate-spin" />
                                  Generating...
                                </>
                              ) : (
                                <>
                                  <Video className="w-4 h-4" />
                                  GENERATE VIDEO
                                </>
                              )}
                            </button>
                          </div>

                          {videoGenerating && (
                            <p className="text-xs text-gray-500 text-center mt-3">
                              Creating your viral video... This may take a minute.
                            </p>
                          )}
                        </>
                      )}
                    </>
                  ) : (
                    <div className="space-y-4">
                      <div className="flex items-center gap-2 p-3 bg-[#00ff88]/10 border border-[#00ff88]/30 rounded-lg">
                        <CheckCircle className="w-5 h-5 text-[#00ff88]" />
                        <div>
                          <p className="text-sm font-semibold text-[#00ff88]">
                            {videoResult.fallback_used ? 'Viral Poster Created!' : 'Viral Video Created!'}
                          </p>
                          <p className="text-xs text-gray-400">Ready to share on X/Twitter</p>
                        </div>
                      </div>

                      {/* Video/Image Preview */}
                      <div className="rounded-lg overflow-hidden bg-black">
                        {videoResult.fallback_used ? (
                          <img
                            src={videoResult.video_url}
                            alt="Viral Poster"
                            className="w-full"
                          />
                        ) : (
                          <video
                            src={videoResult.video_url}
                            controls
                            className="w-full"
                          />
                        )}
                      </div>

                      {/* Script Preview */}
                      {videoResult.script && (
                        <div className="bg-black/30 rounded-lg p-3">
                          <p className="text-xs text-gray-500 mb-1">Video Script:</p>
                          <p className="text-xs text-gray-300 whitespace-pre-wrap">
                            {videoResult.script.slice(0, 200)}...
                          </p>
                        </div>
                      )}

                      {/* Action Buttons */}
                      <div className="grid grid-cols-2 gap-3">
                        <button
                          onClick={downloadVideo}
                          className="py-3 bg-gray-700 text-white font-medium rounded-lg hover:bg-gray-600 flex items-center justify-center gap-2"
                        >
                          <Download className="w-4 h-4" />
                          Download
                        </button>
                        <button
                          onClick={shareToTwitter}
                          className="py-3 bg-[#1DA1F2] text-white font-medium rounded-lg hover:bg-[#1DA1F2]/80 flex items-center justify-center gap-2"
                        >
                          <Share2 className="w-4 h-4" />
                          Share to X
                        </button>
                      </div>

                      <p className="text-xs text-gray-500 text-center">
                        Download the {videoResult.fallback_used ? 'poster' : 'video'} and attach it to your tweet for maximum impact!
                      </p>
                    </div>
                  )}
                </div>

                {/* Twitter Thread Section */}
                {twitterThreadUrls.length > 0 && (
                  <div className="bg-gray-800/50 rounded-xl p-4 mb-6 text-left">
                    <h4 className="text-sm font-semibold text-[#1DA1F2] mb-3 flex items-center gap-2">
                      <Twitter className="w-4 h-4" />
                      VIRAL TWITTER THREAD ({twitterThreadUrls.length} TWEETS)
                    </h4>

                    {/* Video Download Section - Prominent */}
                    <div className="bg-gradient-to-r from-red-500/20 to-orange-500/20 border border-red-500/50 rounded-lg p-4 mb-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Video className="w-5 h-5 text-red-400" />
                        <span className="font-bold text-red-300">STEP 1: Download Video First!</span>
                      </div>
                      <p className="text-xs text-gray-300 mb-3">
                        Attach this video to your FIRST tweet for 10x more engagement and viral reach!
                      </p>
                      <a
                        href={`${API_BASE}${threadVideoUrl || '/static/default_viral_video.mp4'}`}
                        download="hospital_bill_exposed.mp4"
                        className="w-full py-3 bg-gradient-to-r from-red-500 to-orange-500 text-white font-bold rounded-lg hover:from-red-600 hover:to-orange-600 transition-all flex items-center justify-center gap-2"
                      >
                        <Download className="w-5 h-5" />
                        DOWNLOAD VIDEO FOR FIRST TWEET
                      </a>
                    </div>

                    <p className="text-xs text-gray-500 mb-4">
                      STEP 2: Post each tweet in order. <span className="text-red-400 font-semibold">Attach the video when posting Tweet 1!</span>
                    </p>
                    <div className="space-y-2">
                      {twitterThreadUrls.map((url, index) => (
                        <a
                          key={index}
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={`w-full py-3 px-4 bg-black border font-medium rounded-lg hover:text-white transition-all flex items-center justify-between group ${
                            index === 0
                              ? 'border-red-500 text-red-400 hover:bg-red-500'
                              : 'border-[#1DA1F2]/50 text-[#1DA1F2] hover:bg-[#1DA1F2]'
                          }`}
                        >
                          <span className="flex items-center gap-2">
                            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold group-hover:bg-white/20 ${
                              index === 0 ? 'bg-red-500/20' : 'bg-[#1DA1F2]/20'
                            }`}>
                              {index + 1}
                            </span>
                            {index === 0 && "🎬 The Hook - ATTACH VIDEO HERE"}
                            {index === 1 && "The Evidence"}
                            {index === 2 && "Legal Violations"}
                            {index === 3 && "Tag Authorities"}
                            {index === 4 && "Tag Activists & Media"}
                            {index === 5 && "Call to Action"}
                            {index > 5 && `Tweet ${index + 1}`}
                          </span>
                          <ExternalLink className="w-4 h-4 opacity-50 group-hover:opacity-100" />
                        </a>
                      ))}
                    </div>
                    <p className="text-xs text-gray-500 mt-3 text-center">
                      Reply to each tweet to create the thread
                    </p>
                  </div>
                )}

                {/* Fallback: Single Tweet Button */}
                {!twitterThreadUrls.length && twitterIntentUrl && (
                  <a
                    href={twitterIntentUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full py-4 bg-black border-2 border-[#1DA1F2] text-[#1DA1F2] font-bold rounded-xl hover:bg-[#1DA1F2] hover:text-white transition-all flex items-center justify-center gap-2 mb-3"
                  >
                    <Twitter className="w-5 h-5" />
                    POST TO X / TWITTER
                  </a>
                )}

                <button
                  onClick={onClose}
                  className="w-full py-4 bg-[#00ff88] text-black font-bold rounded-xl hover:bg-[#00ff88]/90 transition-colors"
                >
                  Done
                </button>
              </motion.div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
