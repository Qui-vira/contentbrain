import { getContactOptions, getServiceOptions } from "@/lib/queries";
import { upsertContactOption, deleteContactOption, upsertServiceOption, deleteServiceOption } from "../../actions/contact";
import { AdminCard } from "../components";
import { ContactOptionEditor } from "./ContactOptionEditor";
import { ServiceOptionEditor } from "./ServiceOptionEditor";

export default async function ContactPage() {
  const [options, serviceOpts] = await Promise.all([
    getContactOptions(),
    getServiceOptions(),
  ]);

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-white">Contact Page</h1>

      <AdminCard title="Contact Options">
        <ContactOptionEditor
          options={options.map((o) => ({ ...o }))}
          upsertAction={upsertContactOption}
          deleteAction={deleteContactOption}
        />
      </AdminCard>

      <AdminCard title="Contact Form Service Options">
        <ServiceOptionEditor
          options={serviceOpts.map((o) => ({ ...o }))}
          upsertAction={upsertServiceOption}
          deleteAction={deleteServiceOption}
        />
      </AdminCard>
    </div>
  );
}
