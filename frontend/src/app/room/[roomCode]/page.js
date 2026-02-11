'use client';

import { useParams } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Copy, Check } from 'lucide-react';
import { useState } from 'react';

export default function RoomPage() {
  const { roomCode } = useParams();
  const [copied, setCopied] = useState(false);

  const copyRoomCode = () => {
    navigator.clipboard.writeText(roomCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-zinc-900 p-4">
      <div className="max-w-4xl mx-auto pt-8">
        <Card className="bg-zinc-800 border-zinc-700 p-6">
          <div className="space-y-4">
            <h1 className="text-2xl font-bold text-zinc-100">Room Created</h1>
            
            <div className="space-y-2">
              <p className="text-zinc-400 text-sm">Share this code with contributors:</p>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-zinc-900 p-4 rounded-lg">
                  <p className="text-3xl font-mono font-bold text-zinc-100 text-center tracking-wider">
                    {roomCode}
                  </p>
                </div>
                <Button
                  onClick={copyRoomCode}
                  variant="outline"
                  className="bg-zinc-700 border-zinc-600 hover:bg-zinc-600 text-zinc-100"
                >
                  {copied ? (
                    <Check className="h-5 w-5" />
                  ) : (
                    <Copy className="h-5 w-5" />
                  )}
                </Button>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}