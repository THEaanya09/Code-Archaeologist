import { cn } from "@/lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "high" | "medium" | "low" | "outline";
  className?: string;
}

const VARIANT_CLASSES: Record<string, string> = {
  default: "text-stone",
  high: "text-ember",
  medium: "text-graphite",
  low: "text-stone",
  outline: "text-stone",
};

export default function Badge({
  children,
  variant = "default",
  className,
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 font-mono text-[11px] leading-none",
        VARIANT_CLASSES[variant] || VARIANT_CLASSES.default,
        className
      )}
    >
      {children}
    </span>
  );
}
