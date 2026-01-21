'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Video,
  VideoOff,
  Mic,
  MicOff,
  Phone,
  PhoneOff,
  Copy,
  Check,
  AlertTriangle,
  Lightbulb,
  Target,
  TrendingUp,
  X,
  MessageSquare,
  Zap,
  Shield,
  HelpCircle,
} from 'lucide-react';

// PeerJS for WebRTC
import Peer, { MediaConnection } from 'peerjs';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

interface Props {
  onClose?: () => void;
}

interface CounterCard {
  card_id: string;
  timestamp: string;
  their_statement: string;
  verdict: string;
  verdict_emoji: string;
  explanation: string;
  counter_argument: string;
  evidence: string[];
  confidence: number;
  suggested_questions: string[];
}

export function NegotiationArena({ onClose }: Props) {
  // Stage management
  const [stage, setStage] = useState<'setup' | 'waiting' | 'connected' | 'ended'>('setup');

  // Setup form
  const [topic, setTopic] = useState('');
  const [yourPosition, setYourPosition] = useState('');
  const [roomId, setRoomId] = useState('');
  const [isHost, setIsHost] = useState(true);
  const [joinRoomId, setJoinRoomId] = useState('');

  // Connection state
  const [peerId, setPeerId] = useState<string | null>(null);
  const [remotePeerId, setRemotePeerId] = useState<string | null>(null);
  const [isVideoOn, setIsVideoOn] = useState(true);
  const [isAudioOn, setIsAudioOn] = useState(true);
  const [copied, setCopied] = useState(false);

  // AI state
  const [counterCards, setCounterCards] = useState<CounterCard[]>([]);
  const [negotiationScore, setNegotiationScore] = useState(50);
  const [isListening, setIsListening] = useState(false);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [wsConnected, setWsConnected] = useState(false);
  const [manualInput, setManualInput] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Refs
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRef = useRef<HTMLVideoElement>(null);
  const peerRef = useRef<Peer | null>(null);
  const callRef = useRef<MediaConnection | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const recognitionRef = useRef<any>(null);

  // Initialize PeerJS
  useEffect(() => {
    const peer = new Peer();

    peer.on('open', (id) => {
      console.log('My peer ID:', id);
      setPeerId(id);
    });

    peer.on('call', async (call) => {
      console.log('Incoming call from:', call.peer);
      setRemotePeerId(call.peer);

      // Get local media and answer
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        localStreamRef.current = stream;
        if (localVideoRef.current) {
          localVideoRef.current.srcObject = stream;
        }

        call.answer(stream);
        callRef.current = call;

        call.on('stream', (remoteStream) => {
          console.log('Received remote stream');
          if (remoteVideoRef.current) {
            remoteVideoRef.current.srcObject = remoteStream;
          }
          setStage('connected');
        });
      } catch (err) {
        console.error('Error answering call:', err);
      }
    });

    peer.on('error', (err) => {
      console.error('Peer error:', err);
    });

    peerRef.current = peer;

    return () => {
      peer.destroy();
      localStreamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  // Initialize Web Speech API
  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition;
      const recognition = new SpeechRecognition();

      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        setCurrentTranscript(interimTranscript);

        // Send final transcript to AI
        if (finalTranscript && wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(
            JSON.stringify({
              type: 'transcript',
              speaker: 'them', // Assume we're transcribing the other person
              text: finalTranscript,
            })
          );
          setCurrentTranscript('');
        }
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        if (event.error === 'not-allowed') {
          alert('Microphone access denied. Please allow microphone access for speech recognition.');
        }
      };

      recognition.onend = () => {
        // Auto-restart if still listening
        if (isListening) {
          recognition.start();
        }
      };

      recognitionRef.current = recognition;
    }

    return () => {
      recognitionRef.current?.stop();
    };
  }, [isListening]);

  // Connect WebSocket when room is created/joined
  const connectWebSocket = useCallback((roomId: string) => {
    const wsUrl = `${WS_BASE}/api/negotiation/ws/${roomId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WS message:', data);

      if (data.type === 'counter_card') {
        setCounterCards((prev) => [data.card, ...prev].slice(0, 5)); // Keep last 5 cards
        setNegotiationScore(data.negotiation_score);
        setIsAnalyzing(false);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);
    };

    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
    };

    wsRef.current = ws;

    return ws;
  }, []);

  // Create room as host
  const createRoom = async () => {
    if (!topic || !yourPosition) {
      alert('Please enter the negotiation topic and your position');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/negotiation/create-room`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, your_position: yourPosition }),
      });

      const data = await response.json();
      setRoomId(data.room_id);
      setIsHost(true);
      setStage('waiting');

      // Connect WebSocket
      connectWebSocket(data.room_id);

      // Get local media
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });
      localStreamRef.current = stream;
      if (localVideoRef.current) {
        localVideoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error('Error creating room:', err);
      alert('Failed to create room');
    }
  };

  // Join room as guest
  const joinRoom = async () => {
    if (!joinRoomId) {
      alert('Please enter the room ID');
      return;
    }

    try {
      // Check if room exists
      const response = await fetch(`${API_BASE}/api/negotiation/${joinRoomId}`);
      if (!response.ok) {
        alert('Room not found');
        return;
      }

      const data = await response.json();
      setRoomId(joinRoomId);
      setTopic(data.topic);
      setIsHost(false);
      setStage('waiting');

      // Connect WebSocket
      connectWebSocket(joinRoomId);

      // Get local media
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });
      localStreamRef.current = stream;
      if (localVideoRef.current) {
        localVideoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error('Error joining room:', err);
      alert('Failed to join room');
    }
  };

  // Call remote peer
  const callPeer = async (remotePeerId: string) => {
    if (!peerRef.current || !localStreamRef.current) return;

    const call = peerRef.current.call(remotePeerId, localStreamRef.current);
    callRef.current = call;

    call.on('stream', (remoteStream) => {
      console.log('Received remote stream');
      if (remoteVideoRef.current) {
        remoteVideoRef.current.srcObject = remoteStream;
      }
      setStage('connected');
    });
  };

  // Toggle video
  const toggleVideo = () => {
    if (localStreamRef.current) {
      const videoTrack = localStreamRef.current.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setIsVideoOn(videoTrack.enabled);
      }
    }
  };

  // Toggle audio
  const toggleAudio = () => {
    if (localStreamRef.current) {
      const audioTrack = localStreamRef.current.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setIsAudioOn(audioTrack.enabled);
      }
    }
  };

  // Toggle speech recognition
  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      recognitionRef.current?.start();
      setIsListening(true);
    }
  };

  // End call
  const endCall = () => {
    callRef.current?.close();
    localStreamRef.current?.getTracks().forEach((track) => track.stop());
    wsRef.current?.close();
    recognitionRef.current?.stop();
    setStage('ended');
  };

  // Copy room ID
  const copyRoomId = () => {
    navigator.clipboard.writeText(roomId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Copy peer ID
  const copyPeerId = () => {
    if (peerId) {
      navigator.clipboard.writeText(peerId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Send manual input to AI
  const sendManualInput = () => {
    if (!manualInput.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

    setIsAnalyzing(true);
    wsRef.current.send(
      JSON.stringify({
        type: 'transcript',
        speaker: 'them',
        text: manualInput.trim(),
      })
    );
    setManualInput('');
    // Reset analyzing after a timeout (in case no response)
    setTimeout(() => setIsAnalyzing(false), 10000);
  };

  // Verdict color mapping
  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'FALSE':
        return 'from-red-500/90 to-red-600/90 border-red-400';
      case 'MISLEADING':
        return 'from-orange-500/90 to-orange-600/90 border-orange-400';
      case 'PARTIALLY_TRUE':
        return 'from-yellow-500/90 to-yellow-600/90 border-yellow-400';
      case 'TRUE':
        return 'from-green-500/90 to-green-600/90 border-green-400';
      default:
        return 'from-blue-500/90 to-blue-600/90 border-blue-400';
    }
  };

  return (
    <div className="fixed inset-0 bg-black/95 z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-500/20 rounded-lg">
            <Zap className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Negotiation Arena</h1>
            <p className="text-sm text-gray-400">AI-Powered Real-time Counter-Arguments</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {wsConnected && (
            <div className="flex items-center gap-2 text-green-400 text-sm">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              AI Connected
            </div>
          )}
          {roomId && (
            <div className="flex items-center gap-2">
              <span className="text-gray-400 text-sm">Room:</span>
              <code className="bg-gray-800 px-2 py-1 rounded text-purple-400">{roomId}</code>
              <button onClick={copyRoomId} className="text-gray-400 hover:text-white">
                {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>
          )}
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="w-6 h-6" />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Setup Stage */}
        {stage === 'setup' && (
          <div className="flex-1 flex items-center justify-center">
            <div className="max-w-lg w-full p-8 bg-gray-900 rounded-2xl border border-gray-800">
              <h2 className="text-2xl font-bold text-white mb-6 text-center">Start Negotiation</h2>

              <div className="space-y-6">
                {/* Create Room Tab */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-purple-400">Create New Room</h3>

                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Negotiation Topic</label>
                    <input
                      type="text"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      placeholder="e.g., Medical bill dispute, Salary negotiation, Vendor contract"
                      className="w-full px-4 py-3 bg-gray-800 rounded-lg text-white placeholder-gray-500 border border-gray-700 focus:border-purple-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Your Position</label>
                    <textarea
                      value={yourPosition}
                      onChange={(e) => setYourPosition(e.target.value)}
                      placeholder="e.g., The hospital overcharged me 300% above CGHS rates. I have documentation."
                      rows={3}
                      className="w-full px-4 py-3 bg-gray-800 rounded-lg text-white placeholder-gray-500 border border-gray-700 focus:border-purple-500 focus:outline-none resize-none"
                    />
                  </div>

                  <button
                    onClick={createRoom}
                    className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all"
                  >
                    Create Room & Get AI Assistant
                  </button>
                </div>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-700" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-gray-900 text-gray-500">OR</span>
                  </div>
                </div>

                {/* Join Room Tab */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-blue-400">Join Existing Room</h3>

                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Room ID</label>
                    <input
                      type="text"
                      value={joinRoomId}
                      onChange={(e) => setJoinRoomId(e.target.value.toUpperCase())}
                      placeholder="Enter room ID (e.g., A1B2C3D4)"
                      className="w-full px-4 py-3 bg-gray-800 rounded-lg text-white placeholder-gray-500 border border-gray-700 focus:border-blue-500 focus:outline-none uppercase"
                    />
                  </div>

                  <button
                    onClick={joinRoom}
                    className="w-full py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all"
                  >
                    Join Room
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Waiting / Connected Stage */}
        {(stage === 'waiting' || stage === 'connected') && (
          <>
            {/* Video Section */}
            <div className="flex-1 flex flex-col p-4 relative">
              {/* Remote Video (Large) */}
              <div className="flex-1 relative bg-gray-900 rounded-2xl overflow-hidden">
                <video
                  ref={remoteVideoRef}
                  autoPlay
                  playsInline
                  className="w-full h-full object-cover"
                />

                {stage === 'waiting' && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-900">
                    <div className="text-center space-y-6 max-w-md">
                      <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto" />
                      <p className="text-white text-lg">Waiting for other party to join...</p>

                      {/* Shareable Link - PRIMARY */}
                      <div className="bg-gray-800 rounded-xl p-4 space-y-3">
                        <p className="text-green-400 font-semibold">Share this link with the other person:</p>
                        <div className="flex items-center gap-2">
                          <code className="flex-1 bg-gray-900 px-3 py-2 rounded text-blue-400 text-sm truncate">
                            {typeof window !== 'undefined' ? `${window.location.origin}/call/${peerId}?room=${roomId}` : 'Loading...'}
                          </code>
                          <button
                            onClick={() => {
                              navigator.clipboard.writeText(`${window.location.origin}/call/${peerId}?room=${roomId}`);
                              setCopied(true);
                              setTimeout(() => setCopied(false), 2000);
                            }}
                            className="px-3 py-2 bg-green-500 text-white rounded hover:bg-green-600 flex items-center gap-1"
                          >
                            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                            {copied ? 'Copied!' : 'Copy'}
                          </button>
                        </div>
                        <p className="text-gray-500 text-xs">They can open this link on any device to join the video call</p>
                      </div>

                      {/* Manual peer connection - SECONDARY */}
                      <div className="border-t border-gray-700 pt-4 space-y-3">
                        <p className="text-gray-400 text-sm">Or enter their Peer ID if they shared one:</p>
                        <div className="flex items-center justify-center gap-2">
                          <input
                            type="text"
                            value={remotePeerId || ''}
                            onChange={(e) => setRemotePeerId(e.target.value)}
                            placeholder="Enter their peer ID"
                            className="px-4 py-2 bg-gray-800 rounded text-white placeholder-gray-500 border border-gray-700 focus:border-purple-500 focus:outline-none"
                          />
                          <button
                            onClick={() => remotePeerId && callPeer(remotePeerId)}
                            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                          >
                            Call
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Current Transcript Overlay */}
                {currentTranscript && (
                  <div className="absolute bottom-4 left-4 right-4 p-3 bg-black/70 rounded-lg">
                    <p className="text-white text-sm italic">{currentTranscript}</p>
                  </div>
                )}

                {/* Local Video (Small) */}
                <div className="absolute bottom-4 right-4 w-48 h-36 bg-gray-800 rounded-lg overflow-hidden border-2 border-purple-500 shadow-xl">
                  <video
                    ref={localVideoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-full object-cover"
                  />
                  {!isVideoOn && (
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
                      <VideoOff className="w-8 h-8 text-gray-500" />
                    </div>
                  )}
                </div>
              </div>

              {/* Controls */}
              <div className="flex items-center justify-center gap-4 mt-4">
                <button
                  onClick={toggleVideo}
                  className={`p-4 rounded-full ${
                    isVideoOn ? 'bg-gray-700 hover:bg-gray-600' : 'bg-red-500 hover:bg-red-600'
                  } transition-colors`}
                >
                  {isVideoOn ? <Video className="w-6 h-6 text-white" /> : <VideoOff className="w-6 h-6 text-white" />}
                </button>

                <button
                  onClick={toggleAudio}
                  className={`p-4 rounded-full ${
                    isAudioOn ? 'bg-gray-700 hover:bg-gray-600' : 'bg-red-500 hover:bg-red-600'
                  } transition-colors`}
                >
                  {isAudioOn ? <Mic className="w-6 h-6 text-white" /> : <MicOff className="w-6 h-6 text-white" />}
                </button>

                <button
                  onClick={toggleListening}
                  className={`p-4 rounded-full ${
                    isListening
                      ? 'bg-green-500 hover:bg-green-600 animate-pulse'
                      : 'bg-gray-700 hover:bg-gray-600'
                  } transition-colors`}
                  title={isListening ? 'Stop AI Listening' : 'Start AI Listening'}
                >
                  <MessageSquare className="w-6 h-6 text-white" />
                </button>

                <button
                  onClick={endCall}
                  className="p-4 rounded-full bg-red-500 hover:bg-red-600 transition-colors"
                >
                  <PhoneOff className="w-6 h-6 text-white" />
                </button>
              </div>
            </div>

            {/* AI Counter Cards Panel */}
            <div className="w-96 bg-gray-900 border-l border-gray-800 flex flex-col">
              {/* Negotiation Score */}
              <div className="p-4 border-b border-gray-800">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">Your Advantage</span>
                  <span className="text-white font-bold">{negotiationScore}%</span>
                </div>
                <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500"
                    initial={{ width: '50%' }}
                    animate={{ width: `${negotiationScore}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Weak</span>
                  <span>Strong</span>
                </div>
              </div>

              {/* Topic & Position */}
              <div className="p-4 border-b border-gray-800">
                <div className="text-xs text-gray-500 mb-1">TOPIC</div>
                <div className="text-white font-medium mb-3">{topic}</div>
                <div className="text-xs text-gray-500 mb-1">YOUR POSITION</div>
                <div className="text-gray-300 text-sm">{yourPosition}</div>
              </div>

              {/* AI Listening Status */}
              <div className="p-4 border-b border-gray-800">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-3 h-3 rounded-full ${
                      isListening ? 'bg-green-400 animate-pulse' : 'bg-gray-600'
                    }`}
                  />
                  <span className="text-gray-300 text-sm">
                    {isListening ? 'AI is listening to their speech...' : 'Click microphone to start AI'}
                  </span>
                </div>
              </div>

              {/* Manual Input for Demo */}
              <div className="p-4 border-b border-gray-800">
                <label className="block text-xs text-gray-500 mb-2">TYPE WHAT THEY SAY (for demo)</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={manualInput}
                    onChange={(e) => setManualInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && sendManualInput()}
                    placeholder="Type their argument..."
                    className="flex-1 px-3 py-2 bg-gray-800 rounded text-white text-sm placeholder-gray-500 border border-gray-700 focus:border-purple-500 focus:outline-none"
                  />
                  <button
                    onClick={sendManualInput}
                    disabled={!manualInput.trim() || isAnalyzing}
                    className="px-4 py-2 bg-purple-500 text-white rounded text-sm font-semibold hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isAnalyzing ? '...' : 'Analyze'}
                  </button>
                </div>
              </div>

              {/* Counter Cards */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                <AnimatePresence>
                  {counterCards.length === 0 ? (
                    <div className="text-center text-gray-500 py-8">
                      <Shield className="w-12 h-12 mx-auto mb-3 opacity-50" />
                      <p>Counter cards will appear here</p>
                      <p className="text-xs mt-1">Start AI listening to analyze their statements</p>
                    </div>
                  ) : (
                    counterCards.map((card, index) => (
                      <motion.div
                        key={card.card_id}
                        initial={{ opacity: 0, x: 50, scale: 0.9 }}
                        animate={{ opacity: 1, x: 0, scale: 1 }}
                        exit={{ opacity: 0, x: -50, scale: 0.9 }}
                        transition={{ duration: 0.3 }}
                        className={`p-4 rounded-xl bg-gradient-to-br ${getVerdictColor(
                          card.verdict
                        )} border shadow-xl`}
                      >
                        {/* Verdict Header */}
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <span className="text-2xl">{card.verdict_emoji}</span>
                            <span className="text-white font-bold">{card.verdict}</span>
                          </div>
                          <span className="text-white/70 text-xs">{card.timestamp}</span>
                        </div>

                        {/* Their Statement */}
                        <div className="bg-black/30 rounded-lg p-2 mb-3">
                          <p className="text-white/90 text-sm italic">"{card.their_statement}"</p>
                        </div>

                        {/* Explanation */}
                        <p className="text-white/90 text-sm mb-3">{card.explanation}</p>

                        {/* Counter Argument */}
                        <div className="bg-white/10 rounded-lg p-3 mb-3">
                          <div className="flex items-center gap-2 mb-2">
                            <Lightbulb className="w-4 h-4 text-yellow-300" />
                            <span className="text-yellow-300 text-xs font-semibold">SAY THIS</span>
                          </div>
                          <p className="text-white font-medium text-sm">{card.counter_argument}</p>
                        </div>

                        {/* Evidence */}
                        {card.evidence.length > 0 && (
                          <div className="mb-3">
                            <div className="flex items-center gap-2 mb-2">
                              <Target className="w-4 h-4 text-blue-300" />
                              <span className="text-blue-300 text-xs font-semibold">EVIDENCE</span>
                            </div>
                            <ul className="space-y-1">
                              {card.evidence.map((e, i) => (
                                <li key={i} className="text-white/80 text-xs flex items-start gap-2">
                                  <span className="text-blue-300">•</span>
                                  {e}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Suggested Questions */}
                        {card.suggested_questions.length > 0 && (
                          <div>
                            <div className="flex items-center gap-2 mb-2">
                              <HelpCircle className="w-4 h-4 text-purple-300" />
                              <span className="text-purple-300 text-xs font-semibold">ASK THEM</span>
                            </div>
                            <ul className="space-y-1">
                              {card.suggested_questions.map((q, i) => (
                                <li key={i} className="text-white/80 text-xs flex items-start gap-2">
                                  <span className="text-purple-300">?</span>
                                  {q}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Confidence */}
                        <div className="mt-3 pt-3 border-t border-white/20 flex items-center justify-between">
                          <span className="text-white/60 text-xs">AI Confidence</span>
                          <span className="text-white font-bold text-sm">{card.confidence}%</span>
                        </div>
                      </motion.div>
                    ))
                  )}
                </AnimatePresence>
              </div>
            </div>
          </>
        )}

        {/* Ended Stage */}
        {stage === 'ended' && (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-4">
              <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto">
                <Check className="w-10 h-10 text-green-400" />
              </div>
              <h2 className="text-2xl font-bold text-white">Negotiation Ended</h2>
              <p className="text-gray-400">Final Score: {negotiationScore}%</p>
              <p className="text-gray-400">{counterCards.length} counter-arguments generated</p>
              <button
                onClick={() => setStage('setup')}
                className="mt-4 px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600"
              >
                Start New Negotiation
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
