'use client';

import { useParams } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Copy, Check, Users, Crown, UserPlus, UserMinus, Download } from 'lucide-react';
import { useState, useEffect, useRef, useCallback } from 'react';
import Cookies from 'js-cookie';
import { io } from 'socket.io-client';

// --- Sparkle particle component ---
function Sparkles({ active }) {
  if (!active) return null;
  const particles = Array.from({ length: 12 });
  return (
    <span className="sparkle-container" aria-hidden="true">
      {particles.map((_, i) => (
        <span
          key={i}
          className="sparkle-particle"
          style={{
            '--angle': `${(i / 12) * 360}deg`,
            '--delay': `${i * 20}ms`,
          }}
        />
      ))}
    </span>
  );
}

// --- Presence Toast ---
function PresenceToast({ toasts }) {
  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`
            presence-toast
            flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium
            shadow-lg border backdrop-blur-sm relative overflow-hidden
            ${toast.leaving ? 'toast-leave' : 'toast-enter'}
            ${toast.type === 'join'
              ? 'bg-zinc-800/90 border-emerald-700/60 text-emerald-400'
              : 'bg-zinc-800/90 border-zinc-600/60 text-zinc-400'
            }
          `}
        >
          <span className="relative z-10 flex items-center gap-3">
            {toast.type === 'join'
              ? <UserPlus className="h-4 w-4 shrink-0" />
              : <UserMinus className="h-4 w-4 shrink-0" />
            }
            <span>{toast.message}</span>
          </span>
          {toast.type === 'join' && <Sparkles active={true} />}
        </div>
      ))}
    </div>
  );
}

// --- Class List Item with slide-in ---
function ClassItem({ item, isHost, onReview }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const t = requestAnimationFrame(() => setMounted(true));
    return () => cancelAnimationFrame(t);
  }, []);

  const borderColor =
    item.status === 'approved' ? 'border-green-700'
    : item.status === 'needs_review' ? 'border-yellow-700'
    : 'border-zinc-700';

  return (
    <div
      className={`
        class-item bg-zinc-900 p-3 rounded border flex items-center justify-between
        ${borderColor}
        ${mounted ? 'class-item-visible' : 'class-item-hidden'}
      `}
    >
      <div className="flex-1">
        <span className="text-zinc-300">{item.raw_class_name}</span>
        {item.review_reason && (
          <p className="text-xs text-zinc-500 mt-1">{item.review_reason}</p>
        )}
      </div>
      {isHost && item.status !== 'approved' && item.status !== 'discarded' && (
        <div className="flex gap-2">
          <Button
            size="sm"
            className="bg-green-700 hover:bg-green-600 text-white"
            onClick={() => onReview(item.id, 'approved')}
          >
            Approve
          </Button>
          <Button
            size="sm"
            className="bg-red-700 hover:bg-red-600 text-white"
            onClick={() => onReview(item.id, 'discarded')}
          >
            Discard
          </Button>
        </div>
      )}
    </div>
  );
}

// --- Main Page ---
export default function RoomPage() {
  const { roomCode } = useParams();
  const [copied, setCopied] = useState(false);
  const [className, setClassName] = useState('');
  const [sessionInfo, setSessionInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [classList, setClassList] = useState([]);
  const [socket, setSocket] = useState(null);
  const [toasts, setToasts] = useState([]);

  const prevContributorCount = useRef(null);
  const toastCounter = useRef(0);

  const addToast = useCallback((type, message) => {
    const id = toastCounter.current++;
    setToasts(prev => [...prev, { id, type, message, leaving: false }]);

    setTimeout(() => {
      setToasts(prev => prev.map(t => t.id === id ? { ...t, leaving: true } : t));
    }, 2700);

    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 3100);
  }, []);

  // Socket.IO connection
  useEffect(() => {
    const sessionToken = Cookies.get('session_token');
    if (!sessionToken || !roomCode) return;

    const socketInstance = io(
      process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
      { transports: ['websocket'] }
    );

    socketInstance.on('connect', () => {
      socketInstance.emit('join_room', {
        session_token: sessionToken,
        room_code: roomCode,
      });
    });

    socketInstance.on('room_presence_update', (data) => {
      const previousCount = prevContributorCount.current;

      if (previousCount !== null) {
        if (data.contributor_count > previousCount) {
          const delta = data.contributor_count - previousCount;
          addToast('join', delta === 1 ? 'Someone joined the room' : `${delta} people joined the room`);
        }
        if (data.contributor_count < previousCount) {
          const delta = previousCount - data.contributor_count;
          addToast('leave', delta === 1 ? 'Someone left the room' : `${delta} people left the room`);
        }
      }

      prevContributorCount.current = data.contributor_count;
      setSessionInfo(prev => ({
        ...prev,
        host_count: data.host_count,
        contributor_count: data.contributor_count,
      }));
    });

    socketInstance.on('class_created', (data) => {
      setClassList(prev => [data, ...prev]);
    });

    socketInstance.on('class_reviewed', (data) => {
      setClassList(prev =>
        prev.map(item => item.id === data.id ? { ...item, ...data } : item)
      );
    });

    setSocket(socketInstance);
    return () => { socketInstance.disconnect(); };
  }, [roomCode, addToast]);

  useEffect(() => {
    const fetchSessionInfo = async () => {
      const sessionToken = Cookies.get('session_token');
      if (!sessionToken) { setLoading(false); return; }
      try {
        const response = await fetch(`/api/session/info?room_code=${roomCode}&session_token=${sessionToken}`);
        if (!response.ok) throw new Error('Failed to fetch session info');
        const data = await response.json();
        setSessionInfo(data);
        prevContributorCount.current = data.contributor_count ?? 0;
      } catch (error) {
        console.error('Error fetching session info:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchSessionInfo();
  }, [roomCode]);

  useEffect(() => {
    const fetchClasses = async () => {
      const sessionToken = Cookies.get('session_token');
      if (!sessionToken) return;
      try {
        const response = await fetch('/api/classes/list');
        if (!response.ok) throw new Error('Failed to fetch classes');
        const data = await response.json();
        setClassList([...data].reverse());
      } catch (error) {
        console.error('Error fetching classes:', error);
      }
    };
    fetchClasses();
  }, []);

  const copyRoomCode = () => {
    navigator.clipboard.writeText(roomCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleReview = async (classId, status) => {
    try {
      const response = await fetch('/api/classes/review', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ class_id: classId, status }),
      });
      if (!response.ok) {
        const error = await response.json();
        alert(error.error || 'Failed to review class');
        return;
      }
      const data = await response.json();
      setClassList(prev => prev.map(item => item.id === classId ? data : item));
    } catch (error) {
      console.error('Error reviewing class:', error);
      alert('Failed to review class. Please try again.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!className.trim()) return;
    try {
      const response = await fetch('/api/classes/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ class_name: className.trim() }),
      });
      if (!response.ok) {
        const error = await response.json();
        alert(error.error || 'Failed to submit class name');
        return;
      }
      setClassName('');
    } catch (error) {
      console.error('Error submitting class:', error);
      alert('Failed to submit class name. Please try again.');
    }
  };

  const [exporting, setExporting] = useState(false);

  const handleExport = async () => {
    setExporting(true);
    try {
      const response = await fetch('/api/export');
      if (!response.ok) {
        const error = await response.json();
        alert(error.detail || 'Export failed');
        return;
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'data.yaml';
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export error:', error);
      alert('Export failed. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  const isHost = sessionInfo?.your_role === 'host';
  const contributorCount = sessionInfo?.contributor_count || 0;
  const visibleClasses = classList.filter(item => item.status !== 'discarded');

  return (
    <>
      <style>{`
        .class-scroll::-webkit-scrollbar { width: 4px; }
        .class-scroll::-webkit-scrollbar-track { background: transparent; }
        .class-scroll::-webkit-scrollbar-thumb { background: #3f3f46; border-radius: 9999px; }
        .class-scroll::-webkit-scrollbar-thumb:hover { background: #52525b; }
        .class-scroll { scrollbar-width: thin; scrollbar-color: #3f3f46 transparent; }

        .class-item { transition: opacity 300ms ease, transform 300ms ease; }
        .class-item-hidden { opacity: 0; transform: translateY(-10px); }
        .class-item-visible { opacity: 1; transform: translateY(0); }

        @keyframes toastIn {
          from { opacity: 0; transform: translateX(16px) scale(0.95); }
          to   { opacity: 1; transform: translateX(0) scale(1); }
        }
        @keyframes toastOut {
          from { opacity: 1; transform: translateX(0) scale(1); }
          to   { opacity: 0; transform: translateX(16px) scale(0.95); }
        }
        .toast-enter { animation: toastIn 250ms ease forwards; }
        .toast-leave { animation: toastOut 350ms ease forwards; }

        .sparkle-container { position: absolute; inset: 0; pointer-events: none; overflow: visible; }
        .sparkle-particle {
          position: absolute; top: 50%; left: 50%;
          width: 5px; height: 5px; border-radius: 50%;
          background: #34d399;
          animation: sparkle-burst 600ms ease-out calc(var(--delay)) both;
        }
        .sparkle-particle:nth-child(odd) { background: #6ee7b7; width: 4px; height: 4px; }
        .sparkle-particle:nth-child(3n) { background: #fbbf24; width: 3px; height: 3px; }
        @keyframes sparkle-burst {
          0%   { transform: rotate(var(--angle)) translateX(0px) scale(1); opacity: 1; }
          60%  { opacity: 1; }
          100% { transform: rotate(var(--angle)) translateX(28px) scale(0); opacity: 0; }
        }
      `}</style>

      <div className="min-h-screen bg-zinc-900 p-6">
        <PresenceToast toasts={toasts} />

        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-12 gap-6">
            {/* Left - Room Info */}
            <div className="col-span-3">
              <Card className="bg-zinc-800 border-zinc-700 p-4 space-y-4">
                <h2 className="text-lg font-bold text-zinc-100">Room Info</h2>
                {loading ? (
                  <p className="text-zinc-400 text-sm">Loading...</p>
                ) : (
                  <div className="space-y-3">
                    {isHost && (
                      <div className="flex items-center gap-2 text-zinc-300">
                        <Crown className="h-4 w-4 text-yellow-500" />
                        <span className="text-sm">You are Host</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-zinc-300">
                      <Users className="h-4 w-4 text-blue-500" />
                      <span className="text-sm">{contributorCount} Contributors</span>
                    </div>
                    {isHost && (
                      <Button
                        onClick={handleExport}
                        disabled={exporting}
                        className="w-full bg-zinc-700 hover:bg-zinc-600 text-zinc-100 gap-2"
                        size="sm"
                      >
                        <Download className="h-4 w-4" />
                        {exporting ? 'Exporting...' : 'Export YAML'}
                      </Button>
                    )}
                  </div>
                )}
              </Card>
            </div>

            {/* Center - Input Area */}
            <div className="col-span-6">
              <Card className="bg-zinc-800 border-zinc-700 p-6">
                <form onSubmit={handleSubmit} className="space-y-4">
                  <h2 className="text-xl font-bold text-zinc-100 text-center">Add Class Name</h2>
                  <Input
                    type="text"
                    placeholder="Enter class name..."
                    value={className}
                    onChange={(e) => setClassName(e.target.value)}
                    className="bg-zinc-900 border-zinc-700 text-zinc-100 h-12 text-center"
                  />
                  <Button
                    type="submit"
                    disabled={!className.trim()}
                    className="w-full h-12 bg-zinc-700 hover:bg-zinc-600 text-zinc-100 font-bold"
                  >
                    Submit
                  </Button>
                </form>

                <div className="mt-6 space-y-2">
                  <h3 className="text-sm font-semibold text-zinc-400">Submitted Classes</h3>
                  <div className="space-y-2 max-h-96 overflow-y-auto class-scroll pr-1">
                    {visibleClasses.length === 0 ? (
                      <p className="text-zinc-500 text-sm text-center py-4">No classes submitted yet</p>
                    ) : (
                      visibleClasses.map((item) => (
                        <ClassItem
                          key={item.id}
                          item={item}
                          isHost={isHost}
                          onReview={handleReview}
                        />
                      ))
                    )}
                  </div>
                </div>
              </Card>
            </div>

            {/* Right - Room Code */}
            <div className="col-span-3">
              <Card className="bg-zinc-800 border-zinc-700 p-4 space-y-4">
                <h2 className="text-lg font-bold text-zinc-100">Room Code</h2>
                <div className="space-y-3">
                  <div className="bg-zinc-900 p-4 rounded-lg">
                    <p className="text-2xl font-mono font-bold text-zinc-100 text-center tracking-wider">
                      {roomCode}
                    </p>
                  </div>
                  <Button
                    onClick={copyRoomCode}
                    variant="outline"
                    className="w-full bg-zinc-700 border-zinc-600 hover:bg-zinc-600 text-zinc-100"
                  >
                    {copied ? (
                      <><Check className="mr-2 h-4 w-4" />Copied!</>
                    ) : (
                      <><Copy className="mr-2 h-4 w-4" />Copy Code</>
                    )}
                  </Button>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}