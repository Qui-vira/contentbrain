import {
  Eye, Users, Handshake, Rocket, Phone, BookOpen, Code,
  Crosshair, Crown, BarChart3, Zap, Cpu, Layers,
  Hammer, MessageCircle, Mail, Calendar, GraduationCap,
  ArrowRight,
  type LucideIcon,
} from "lucide-react";

const iconMap: Record<string, LucideIcon> = {
  Eye, Users, Handshake, Rocket, Phone, BookOpen, Code,
  Crosshair, Crown, BarChart3, Zap, Cpu, Layers,
  Hammer, MessageCircle, Mail, Calendar, GraduationCap,
  ArrowRight,
};

export function getIcon(name: string): LucideIcon {
  return iconMap[name] || Zap;
}
