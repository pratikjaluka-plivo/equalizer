'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import Peer, { MediaConnection } from 'peerjs';
import { Video, VideoOff, Mic, MicOff, PhoneOff, Phone } from 'lucide-react';

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

/**
 * Video call page for the OTHER party to join.
 * They open: /call/{peerId}?room={roomId}
 * Their speech is captured via MediaRecorder, sent to backend for Whisper transcription,
 * then analyzed by AI for the host to get counter-arguments.
 */
export default function JoinCallPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const hostPeerId = params.peerId as string;
  const roomId = searchParams.get('room');

  const [status, setStatus] = useState<'connecting' | 'ready' | 'calling' | 'connected' | 'ended'>('connecting');
  const [myPeerId, setMyPeerId] = useState<string | null>(null);
  const [isVideoOn, setIsVideoOn] = useState(true);
  const [isAudioOn, setIsAudioOn] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isTranscribing, setIsTranscribing] = useState(false);

  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRef = useRef<HTMLVideoElement>(null);
  const peerRef = useRef<Peer | null>(null);
  const callRef = useRef<MediaConnection | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Initialize PeerJS and get local media
  useEffect(() => {
    const initPeer = async () => {
      try {
        // Get local media first
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        localStreamRef.current = stream;
        if (localVideoRef.current) {
          localVideoRef.current.srcObject = stream;
        }

        // Initialize PeerJS with proper ICE servers
        const peer = new Peer({
          config: {
            iceServers: [
              { urls: 'stun:stun.l.google.com:19302' },
              { urls: 'stun:stun1.l.google.com:19302' },
              { urls: 'stun:stun2.l.google.com:19302' },
              { urls: 'stun:stun3.l.google.com:19302' },
              { urls: 'stun:stun4.l.google.com:19302' },
              { urls: 'stun:global.stun.twilio.com:3478' },
            ]
          }
        });

        peer.on('open', (id) => {
          console.log('My peer ID:', id);
          setMyPeerId(id);
          setStatus('ready');
        });

        peer.on('call', async (call) => {
          // Answer incoming calls
          call.answer(stream);
          callRef.current = call;

          call.on('stream', (remoteStream) => {
            if (remoteVideoRef.current) {
              remoteVideoRef.current.srcObject = remoteStream;
            }
            setStatus('connected');
          });
        });

        peer.on('error', (err) => {
          console.error('Peer error:', err);
          setError(`Connection error: ${err.message}`);
        });

        peerRef.current = peer;
      } catch (err: any) {
        console.error('Media error:', err);
        setError(`Camera/microphone access denied: ${err.message}`);
      }
    };

    initPeer();

    return () => {
      peerRef.current?.destroy();
      localStreamRef.current?.getTracks().forEach((track) => track.stop());
      wsRef.current?.close();
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
    };
  }, []);

  // Start capturing audio using MediaRecorder and send to backend for Whisper transcription
  const startAudioCapture = useCallback(() => {
    if (!localStreamRef.current) {
      console.error('No local stream available for audio capture');
      return;
    }

    // Create audio-only stream from the local stream
    const audioTracks = localStreamRef.current.getAudioTracks();
    if (audioTracks.length === 0) {
      console.error('No audio tracks available');
      return;
    }

    const audioStream = new MediaStream(audioTracks);

    // Check for supported mime types
    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : MediaRecorder.isTypeSupported('audio/webm')
      ? 'audio/webm'
      : 'audio/mp4';

    try {
      const mediaRecorder = new MediaRecorder(audioStream, {
        mimeType,
        audioBitsPerSecond: 16000, // Lower bitrate for faster upload
      });

      mediaRecorder.ondataavailable = async (event) => {
        if (event.data.size > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
          // Convert blob to base64 and send to backend
          const reader = new FileReader();
          reader.onloadend = () => {
            const base64Audio = (reader.result as string).split(',')[1];
            if (base64Audio) {
              console.log('Sending audio chunk for transcription:', event.data.size, 'bytes');
              wsRef.current?.send(
                JSON.stringify({
                  type: 'audio',
                  data: base64Audio,
                })
              );
            }
          };
          reader.readAsDataURL(event.data);
        }
      };

      mediaRecorder.onerror = (event) => {
        console.error('MediaRecorder error:', event);
      };

      // Record in 3-second chunks for real-time transcription
      mediaRecorder.start(3000);
      mediaRecorderRef.current = mediaRecorder;
      setIsTranscribing(true);
      console.log('Audio capture started with', mimeType);
    } catch (err) {
      console.error('Failed to start MediaRecorder:', err);
    }
  }, []);

  // Stop audio capture
  const stopAudioCapture = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current = null;
    }
    setIsTranscribing(false);
  }, []);

  // Connect to WebSocket when we have a room ID and start audio capture after
  useEffect(() => {
    if (roomId && status === 'connected' && !wsRef.current) {
      const wsUrl = `${WS_BASE}/api/negotiation/ws/${roomId}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected for audio transcription');
        // Start audio capture AFTER WebSocket is connected
        startAudioCapture();
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        stopAudioCapture();
      };

      ws.onerror = (err) => {
        console.error('WebSocket error:', err);
      };

      wsRef.current = ws;
    }
  }, [roomId, status, startAudioCapture, stopAudioCapture]);

  // Call the host
  const callHost = () => {
    if (!peerRef.current || !localStreamRef.current || !hostPeerId) return;

    setStatus('calling');

    const call = peerRef.current.call(hostPeerId, localStreamRef.current);
    callRef.current = call;

    call.on('stream', (remoteStream) => {
      if (remoteVideoRef.current) {
        remoteVideoRef.current.srcObject = remoteStream;
      }
      setStatus('connected');
    });

    call.on('error', (err) => {
      console.error('Call error:', err);
      setError(`Call failed: ${err.message}`);
      setStatus('ready');
    });

    call.on('close', () => {
      setStatus('ended');
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

  // End call
  const endCall = () => {
    callRef.current?.close();
    localStreamRef.current?.getTracks().forEach((track) => track.stop());
    wsRef.current?.close();
    stopAudioCapture();
    setStatus('ended');
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="p-4 bg-gray-800 border-b border-gray-700">
        <h1 className="text-xl font-bold text-white text-center">Video Call</h1>
        {isTranscribing && (
          <p className="text-green-400 text-sm text-center mt-1 flex items-center justify-center gap-2">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            Voice active
          </p>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center p-4">
        {error && (
          <div className="bg-red-500/20 border border-red-500 text-red-300 px-4 py-3 rounded-lg mb-4 max-w-md">
            {error}
          </div>
        )}

        {/* Connecting State */}
        {status === 'connecting' && (
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-gray-400">Initializing camera and microphone...</p>
          </div>
        )}

        {/* Ready State */}
        {status === 'ready' && (
          <div className="text-center space-y-6">
            <div className="w-64 h-48 bg-gray-800 rounded-xl overflow-hidden mx-auto">
              <video
                ref={localVideoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
              />
            </div>
            <p className="text-gray-400">Ready to join the call</p>
            <button
              onClick={callHost}
              className="px-8 py-4 bg-green-500 hover:bg-green-600 text-white font-bold rounded-xl flex items-center gap-3 mx-auto transition-colors"
            >
              <Phone className="w-6 h-6" />
              Join Call
            </button>
          </div>
        )}

        {/* Calling State */}
        {status === 'calling' && (
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-gray-400">Connecting to call...</p>
          </div>
        )}

        {/* Connected State */}
        {status === 'connected' && (
          <div className="w-full max-w-4xl">
            {/* Remote Video (Large) */}
            <div className="relative aspect-video bg-gray-800 rounded-2xl overflow-hidden mb-4">
              <video
                ref={remoteVideoRef}
                autoPlay
                playsInline
                className="w-full h-full object-cover"
              />

              {/* Local Video (Small) */}
              <div className="absolute bottom-4 right-4 w-32 h-24 bg-gray-700 rounded-lg overflow-hidden border-2 border-white/30">
                <video
                  ref={localVideoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover"
                />
              </div>
            </div>

            {/* Controls */}
            <div className="flex items-center justify-center gap-4">
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
                onClick={endCall}
                className="p-4 rounded-full bg-red-500 hover:bg-red-600 transition-colors"
              >
                <PhoneOff className="w-6 h-6 text-white" />
              </button>
            </div>
          </div>
        )}

        {/* Ended State */}
        {status === 'ended' && (
          <div className="text-center">
            <p className="text-gray-400 text-xl mb-4">Call ended</p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
            >
              Rejoin
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
