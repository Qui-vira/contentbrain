import { getSetting } from "./queries";

/**
 * Keyword → setting key map.
 * When a CTA href matches a keyword, we resolve it to the
 * corresponding setting value at render time.
 */
const KEYWORD_MAP: Record<string, string> = {
  calendly: "calendly_url",
  calendly_free: "calendly_free_url",
  cal_paid: "cal_paid_url",
  telegram: "telegram_url",
  contact: "/contact",
  pricing: "/pricing",
};

/** All keywords available for the admin dropdown */
export const CTA_OPTIONS = [
  { value: "", label: "None" },
  { value: "calendly", label: "Calendly (paid)" },
  { value: "calendly_free", label: "Calendly (free)" },
  { value: "telegram", label: "Telegram" },
  { value: "contact", label: "Contact page (/contact)" },
  { value: "pricing", label: "Pricing page (/pricing)" },
  { value: "__custom", label: "Custom URL..." },
];

/**
 * Resolve a CTA href keyword to its actual URL.
 * - Known keywords get resolved via settings or static paths
 * - Anything else (external URLs, relative paths) passes through as-is
 */
export async function resolveHref(href: string): Promise<string> {
  if (!href) return "";

  // Static path keywords
  if (href === "contact") return "/contact";
  if (href === "pricing") return "/pricing";

  // Setting-backed keywords
  const settingKey = KEYWORD_MAP[href];
  if (settingKey && !settingKey.startsWith("/")) {
    return await getSetting(settingKey);
  }

  // Already a URL or path — pass through
  return href;
}

/**
 * Synchronous version for client components that already have settings resolved.
 */
export function resolveHrefSync(href: string, settings: Record<string, string>): string {
  if (!href) return "";
  if (href === "contact") return "/contact";
  if (href === "pricing") return "/pricing";

  const settingKey = KEYWORD_MAP[href];
  if (settingKey && !settingKey.startsWith("/")) {
    return settings[settingKey] || "";
  }

  return href;
}
