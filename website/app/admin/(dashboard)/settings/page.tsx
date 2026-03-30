import { getSettings, getSocialLinks } from "@/lib/queries";
import { updateSettings, upsertSocialLink, deleteSocialLink } from "../../actions/settings";
import { AdminCard, FormWithStatus, AdminInput } from "../components";
import { SocialLinkEditor } from "./SocialLinkEditor";

export default async function SettingsPage() {
  const [settings, links] = await Promise.all([getSettings(), getSocialLinks()]);

  const settingFields = [
    { key: "calendly_url", label: "Calendly URL" },
    { key: "calendly_free_url", label: "Calendly Free URL" },
    { key: "email", label: "Contact Email" },
    { key: "telegram_handle", label: "Telegram Handle" },
    { key: "telegram_url", label: "Telegram URL" },
    { key: "formsubmit_email", label: "FormSubmit Email" },
    { key: "hero_tagline", label: "Hero Tagline" },
    { key: "hero_subtitle", label: "Hero Subtitle" },
  ];

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-white">Settings</h1>

      <AdminCard title="Global Settings">
        <FormWithStatus action={updateSettings}>
          <div className="grid gap-4 md:grid-cols-2">
            {settingFields.map((f) => (
              <AdminInput
                key={f.key}
                label={f.label}
                name={`setting_${f.key}`}
                defaultValue={settings[f.key] || ""}
              />
            ))}
          </div>
        </FormWithStatus>
      </AdminCard>

      <AdminCard title="Social Links">
        <SocialLinkEditor
          links={links.map((l) => ({ ...l }))}
          upsertAction={upsertSocialLink}
          deleteAction={deleteSocialLink}
        />
      </AdminCard>
    </div>
  );
}
