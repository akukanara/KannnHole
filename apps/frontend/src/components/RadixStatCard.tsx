import { Card, Text } from '@radix-ui/themes';

type Props = {
  label: string;
  value: string | number;
  tone?: 'default' | 'success';
  className?: string;
};

const baseCardClass =
  'group rounded-2xl border border-slate-200/80 bg-white/90 px-4 py-3.5 shadow-[0_1px_2px_rgba(16,24,40,0.06),0_8px_20px_rgba(16,24,40,0.04)] backdrop-blur transition-all duration-200 ease-in-out hover:border-lime-300/70 hover:shadow-[0_2px_6px_rgba(16,24,40,0.08),0_12px_28px_rgba(16,24,40,0.06)] dark:border-slate-800 dark:bg-slate-950/80';

export default function RadixStatCard({ label, value, tone = 'default', className = '' }: Props) {
  const valueClass =
    tone === 'success'
      ? 'text-lime-700 dark:text-lime-400'
      : 'text-slate-900 dark:text-slate-100';

  return (
    <Card size="2" className={`${baseCardClass} ${className}`}>
      <Text as="p" className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500 dark:text-slate-400">
        {label}
      </Text>
      <Text
        as="p"
        className={`mt-1 text-[1.9rem] font-semibold leading-none tracking-[-0.02em] ${valueClass}`}
      >
        {value}
      </Text>
    </Card>
  );
}
