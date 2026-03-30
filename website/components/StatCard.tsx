interface StatCardProps {
  number: string;
  label: string;
}

export function StatCard({ number, label }: StatCardProps) {
  return (
    <div className="rounded-xl bg-bg-secondary p-6 text-center">
      <div className="text-4xl font-extrabold text-text-primary md:text-[56px] md:leading-none" style={{ textShadow: "0 0 20px rgba(230, 57, 70, 0.2)" }}>
        {number}
      </div>
      <div className="mt-2 text-sm font-medium tracking-widest text-text-secondary uppercase">
        {label}
      </div>
    </div>
  );
}
