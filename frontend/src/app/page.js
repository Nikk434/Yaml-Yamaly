import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function Home() {
  return (
    <div className="min-h-screen bg-zinc-900 flex items-center justify-center p-4">
      <div className="text-center space-y-12">
        <div className="space-y-2">
          <h1 className="text-5xl font-bold text-zinc-400 tracking-wide">
            YOLO YAML GENERATOR
          </h1>
        </div>

        <div className="flex gap-12 justify-center items-start">
          <div className="flex flex-col items-center gap-6 space-y-3 max-w-xs">
            <Link href="/create" className="flex-shrink-0">
              <Button 
                size="lg" 
                className="w-40 h-16 bg-zinc-700 hover:bg-zinc-600 text-zinc-300 text-xl font-bold rounded-none"
              >
                CREATE
              </Button>
            </Link>
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