import { getSocialLinks, getSetting } from "@/lib/queries";
import { FooterClient } from "./FooterClient";

export async function FooterServer() {
  const [socialLinks, email, telegramHandle, telegramUrl, calendlyUrl] = await Promise.all([
    getSocialLinks(),
    getSetting("email"),
    getSetting("telegram_handle"),
    getSetting("telegram_url"),
    getSetting("calendly_url"),
  ]);

  return (
    <FooterClient
      socialLinks={socialLinks}
      email={email}
      telegramHandle={telegramHandle}
      telegramUrl={telegramUrl}
      calendlyUrl={calendlyUrl}
    />
  );
}
