'use client'

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import Cookies from 'js-cookie';
import { Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';

export default function Home(){
  const [mounted, setMounted] = useState(false);
  const [showJoinInput, setShowJoinInput] = useState(false);
  const [roomCode, setRoomCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleJoin = async () => {
    const code = String(roomCode || '').trim();
    
    if (!code) {
      setError('Please enter a room code');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Call sessions/join endpoint
      const response = await fetch('/api/sessions/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ room_code: code }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'Failed to join room');
        return;
      }

      // Store session token
      Cookies.set('session_token', data.session_token, { expires: 7 });
      
      router.push(`/room/${code}`);
    } catch (error) {
      console.error('Error joining room:', error);
      setError('Failed to join room. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    setLoading(true);
    try {
      // Step 1: Create room
      const createResponse = await fetch('/api/rooms/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (!createResponse.ok) {
        throw new Error('Failed to create room');
      }

      const createData = await createResponse.json();
      const { room_code, owner_secret } = createData;

      // Step 2: Create host session
      const sessionResponse = await fetch('/api/sessions/host', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ room_code, owner_secret }),
      });

      if (!sessionResponse.ok) {
        throw new Error('Failed to create host session');
      }

      const sessionData = await sessionResponse.json();
      
      // Store session token
      Cookies.set('session_token', sessionData.session_token, { expires: 7 });
      
      router.push(`/room/${room_code}`);
    } catch (error) {
      console.error('Error creating room:', error);
      alert('Failed to create room. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!mounted) {
    return null;
  }

  return (
    <div className="min-h-screen bg-zinc-900 flex items-center justify-center p-4">
      <div className="text-center space-y-12">
        <div className="space-y-2">
          <h1 className="text-5xl font-bold text-zinc-400 tracking-wide">
            YOLO YAML GENERATOR
          </h1>
        </div>

        <div className="flex gap-12 justify-center items-start">
          {/* CREATE */}
          <div className="flex flex-col items-center gap-6 max-w-xs flex-shrink-0">
            <Button 
              onClick={handleCreate}
              disabled={loading}
              size="lg" 
              className="w-40 h-16 bg-zinc-700 hover:bg-zinc-600 text-zinc-300 text-xl font-bold rounded-none"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Creating...
                </>
              ) : (
                'CREATE'
              )}
            </Button>
            <p className="text-zinc-400 text-left text-xl">
              Create new yaml
            </p>
          </div>

          {/* JOIN */}
          <div className="flex flex-col items-center gap-6 max-w-xs flex-shrink-0">
            {!showJoinInput ? (
              <Button 
                onClick={() => setShowJoinInput(true)}
                size="lg" 
                className="w-40 h-16 bg-zinc-700 hover:bg-zinc-600 text-zinc-300 text-xl font-bold rounded-none"
              >
                JOIN
              </Button>
            ) : (
              <div className="space-y-3">
                <Input
                  type="text"
                  placeholder="ROOM CODE"
                  value={roomCode}
                  onChange={(e) => setRoomCode(e.target.value)}
                  className="w-40 h-12 bg-zinc-800 border-zinc-700 text-zinc-100 text-center text-lg font-mono tracking-wider placeholder:text-zinc-600"
                  maxLength={6}
                  onKeyDown={(e) => e.key === 'Enter' && handleJoin()}
                  autoFocus
                />
                <Button 
                  onClick={handleJoin} 
                  disabled={loading || !String(roomCode || '').trim()}
                  size="lg" 
                  className="w-40 h-16 bg-zinc-700 hover:bg-zinc-600 text-zinc-300 text-xl font-bold rounded-none"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Joining...
                    </>
                  ) : (
                    'SUBMIT'
                  )}
                </Button>
              </div>
            )}
            {error && (
              <p className="text-red-400 text-sm">{error}</p>
            )}
            <p className="text-zinc-400 text-left text-xl">
              Submit class names.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}