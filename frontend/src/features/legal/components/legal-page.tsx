import { Link } from "react-router-dom";

interface LegalPageProps {
  title: string;
}

/** Static legal-route shell. TODO: replace placeholder content with lawyer-reviewed text. */
export function LegalPage({ title }: LegalPageProps) {
  return (
    <main className="mx-auto min-h-screen max-w-3xl px-6 py-16 text-foreground">
      <Link to="/" className="text-sm font-semibold text-fuchsia-500 hover:underline">← Back to NipunHire AI</Link>
      <h1 className="mt-8 text-3xl font-bold">{title}</h1>
      <div className="mt-6 rounded-2xl border border-border bg-card p-6 text-sm leading-6 text-muted-foreground">
        <p className="font-semibold text-foreground">TODO: replace this placeholder with lawyer-reviewed legal text.</p>
        <p className="mt-3">This route exists only to provide a stable location for the final {title.toLowerCase()}.</p>
      </div>
    </main>
  );
}
