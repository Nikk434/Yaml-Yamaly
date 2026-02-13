'use client';

import { useParams } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Copy, Check, Users, Crown } from 'lucide-react';
import { useState, useEffect } from 'react';
import Cookies from 'js-cookie';

export default function RoomPage() {
  const { roomCode } = useParams();
  const [copied, setCopied] = useState(false);
  const [className, setClassName] = useState('');
  const [sessionInfo, setSessionInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSessionInfo = async () => {
      const sessionToken = Cookies.get('session_token');
      
      if (!sessionToken) {
        console.error('No session token found');
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(
          `/api/session/info?room_code=${roomCode}&session_token=${sessionToken}`
        );

        if (!response.ok) {
          throw new Error('Failed to fetch session info');
        }

        const data = await response.json();
        setSessionInfo(data);
      } catch (error) {
        console.error('Error fetching session info:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSessionInfo();
  }, [roomCode]);

  const copyRoomCode = () => {
    navigator.clipboard.writeText(roomCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!className.trim()) return;
    
    // TODO: API call to submit class name
    console.log('Submitting:', className);
    setClassName('');
  };

  const isHost = sessionInfo?.your_role === 'host';
  const contributorCount = sessionInfo?.contributor_count || 0;

  return (
    <div className="min-h-screen bg-zinc-900 p-6">
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
                </div>
              )}
            </Card>
          </div>

          {/* Center - Input Area */}
          <div className="col-span-6">
            <Card className="bg-zinc-800 border-zinc-700 p-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <h2 className="text-xl font-bold text-zinc-100 text-center">
                  Add Class Name
                </h2>
                
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

              {/* Submitted Names List */}
              <div className="mt-6 space-y-2">
                <h3 className="text-sm font-semibold text-zinc-400">Submitted Classes</h3>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {/* Mock data - replace with actual list */}
                  {['person', 'car', 'dog', 'cat'].map((name, idx) => (
                    <div 
                      key={idx}
                      className="bg-zinc-900 p-3 rounded border border-zinc-700 text-zinc-300"
                    >
                      {name}
                    </div>
                  ))}
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
                    <>
                      <Check className="mr-2 h-4 w-4" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="mr-2 h-4 w-4" />
                      Copy Code
                    </>
                  )}
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}