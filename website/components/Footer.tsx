import Link from "next/link";

const pageLinks = [
  { href: "/services", label: "Services" },
  { href: "/pricing", label: "Pricing" },
  { href: "/about", label: "About" },
  { href: "/portfolio", label: "Portfolio" },
  { href: "/contact", label: "Contact" },
];

const socialLinks = [
  { href: "https://x.com/_Quivira", label: "X / Twitter" },
  { href: "https://linkedin.com/in/bigquiv", label: "LinkedIn" },
  { href: "https://tiktok.com/@big_quiv", label: "TikTok" },
  { href: "https://instagram.com/big_quiv", label: "Instagram" },
  { href: "https://youtube.com/@big_quiv", label: "YouTube" },
  { href: "https://t.me/Quivira_Ophir", label: "Telegram" },
];

export function Footer() {
  return (
    <footer className="border-t border-border bg-bg-primary">
      <div className="mx-auto max-w-[1200px] px-6 pb-8 pt-16">
        <div className="grid gap-12 md:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div>
            <Link href="/" className="text-xl font-bold text-white">
              Quivira
            </Link>
            <p className="mt-3 text-sm leading-relaxed text-text-secondary">
              Automated trading signals. AI content intelligence. Real education that produces builders.
            </p>
          </div>

          {/* Pages */}
          <div>
            <h4 className="mb-4 text-xs font-medium uppercase tracking-widest text-text-muted">
              Pages
            </h4>
            <ul className="space-y-3">
              {pageLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-text-secondary transition-colors hover:text-text-primary"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Social */}
          <div>
            <h4 className="mb-4 text-xs font-medium uppercase tracking-widest text-text-muted">
              Social
            </h4>
            <ul className="space-y-3">
              {socialLinks.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-text-secondary transition-colors hover:text-text-primary"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="mb-4 text-xs font-medium uppercase tracking-widest text-text-muted">
              Contact
            </h4>
            <ul className="space-y-3">
              <li>
                <a
                  href="mailto:contact@bigquivdigitals.com"
                  className="text-sm text-text-secondary transition-colors hover:text-text-primary"
                >
                  contact@bigquivdigitals.com
                </a>
              </li>
              <li>
                <a
                  href="https://t.me/Quivira_Ophir"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-text-secondary transition-colors hover:text-text-primary"
                >
                  Telegram: @Quivira_Ophir
                </a>
              </li>
              <li>
                <a
                  href="https://calendly.com/_quivira/one-on-one-meeting"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-text-secondary transition-colors hover:text-text-primary"
                >
                  Book a Call
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 border-t border-border pt-6 text-center text-xs text-text-muted">
          &copy; {new Date().getFullYear()} Quivira. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
