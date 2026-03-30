interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export function Card({ children, className = "" }: CardProps) {
  return (
    <div
      className={`rounded-xl border border-border bg-bg-secondary p-8 transition-all duration-300 hover:-translate-y-1 hover:border-border-hover hover:shadow-[0_8px_32px_rgba(0,0,0,0.3)] ${className}`}
    >
      {children}
    </div>
  );
}
