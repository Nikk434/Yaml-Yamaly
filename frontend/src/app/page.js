'use client'

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import Cookies from 'js-cookie';
import { Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

export default function Home(){
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleCreate = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new Error('Failed to create room');
      }

      const data = await response.json();
      
      // Store owner_secret in cookie (expires in 7 days)
      Cookies.set('owner_secret', data.owner_secret, { expires: 7 });
      
      // Redirect to room page with room code
      router.push(`/room/${data.room_code}`);
    } catch (error) {
      console.error('Error creating room:', error);
      alert('Failed to create room. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-900 flex items-center justify-center p-4">
      <div className="text-center space-y-12">
        <div className="space-y-2">
          <h1 className="text-5xl font-bold text-zinc-400 tracking-wide">
            YOLO YAML GENERATOR
          </h1>
        </div>

        <div className="flex gap-12 justify-center items-start">
          <div className="flex flex-col items-center gap-6 space-y-3 max-w-xs flex-shrink-0">
              <Button onClick={handleCreate}
                size="lg" 
                className="w-40 h-16 bg-zinc-700 hover:bg-zinc-600 text-zinc-300 text-xl font-bold rounded-none"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Creating...
                  </>
                  ) : (''
                  )}
                CREATE
              </Button>
            
            <p className="text-zinc-400 text-left text-xl">
              Create new yaml
            </p>
          </div>

          <div className="flex flex-col items-center gap-6 space-y-3 max-w-xs">
            <Link href="/join" className="flex-shrink-0">
              <Button 
                size="lg" 
                className="w-40 h-16 bg-zinc-700 hover:bg-zinc-600 text-zinc-300 text-xl font-bold rounded-none"
              >
                JOIN
              </Button>
            </Link>
            <p className="text-zinc-400 text-left text-xl">
              Submit class names.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}