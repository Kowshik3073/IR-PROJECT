import Image from "next/image";
import Search from "./components/Search";

export default function Home() {
  return (
    <div className="font-sans min-h-screen">
      <main className="relative">
        {/* Background decoration */}
        <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute -top-32 left-1/2 -translate-x-1/2 h-[600px] w-[1200px] rounded-full bg-gradient-to-r from-blue-500/15 via-indigo-500/15 to-purple-500/15 blur-3xl" />
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-transparent via-white/2 to-transparent dark:via-black/10" />
        </div>

        {/* Hero */}
        <section className="px-6 md:px-10 pt-20 pb-10 md:pt-28 md:pb-16">
          <div className="max-w-5xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/15 dark:border-white/10 bg-white/5 px-3 py-1 text-xs md:text-sm text-foreground/80">
              <Image src="/globe.svg" alt="Globe" width={14} height={14} />
              <span>Fast semantic document search</span>
            </div>
            <h1 className="mt-6 text-4xl md:text-6xl font-bold tracking-tight">
              Find the right document in seconds
            </h1>
            <p className="mt-4 md:mt-5 text-base md:text-lg text-foreground/70 max-w-2xl mx-auto">
              Query across a curated corpus and surface the most relevant passages with clear scoring and context.
            </p>

            <div className="mt-8 md:mt-10">
              <Search />
            </div>

            <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
              <div className="rounded-xl border border-white/10 bg-white/5 p-4 backdrop-blur">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <Image src="/file.svg" alt="Files" width={16} height={16} />
                  Rich Corpus
                </div>
                <p className="mt-2 text-sm text-foreground/70">Search across technology brands and more.</p>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-4 backdrop-blur">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <Image src="/window.svg" alt="Window" width={16} height={16} />
                  Clear Results
                </div>
                <p className="mt-2 text-sm text-foreground/70">See document, score, and contextual snippet.</p>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-4 backdrop-blur">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <Image src="/vercel.svg" alt="Lightning" width={16} height={16} className="dark:invert" />
                  Fast & Simple
                </div>
                <p className="mt-2 text-sm text-foreground/70">Lightweight UI powered by Next.js.</p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="px-6 md:px-10 py-8 border-t border-white/10 text-center text-sm text-foreground/60">
        Built with Next.js. Made for exploring IR concepts.
      </footer>
    </div>
  );
}
