import { getAboutValues, getAboutEcosystem, getAboutContent, getMilestones } from "@/lib/queries";
import { upsertAboutValue, deleteAboutValue, upsertEcosystem, deleteEcosystem, updateAboutContent } from "../../actions/about";
import { upsertMilestone, deleteMilestone } from "../../actions/milestones";
import { AdminInput, AdminTextarea, AdminCard, FormWithStatus, DeleteButton, ImageUpload } from "../components";
import { MilestoneEditor } from "./MilestoneEditor";

export default async function AboutPage() {
  const [values, ecosystem, content, milestones] = await Promise.all([
    getAboutValues(),
    getAboutEcosystem(),
    getAboutContent(),
    getMilestones(),
  ]);

  // Serialize milestones for client component (strip computed fields)
  const rawMilestones = milestones.map((m) => ({
    id: m.id,
    year: m.year,
    title: m.title,
    text: m.text,
    image: m.image,
    images: m.images,
    imageLayout: m.imageLayout,
    sortOrder: m.sortOrder,
  }));

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-white">About Page</h1>

      {/* Content (story, mission) */}
      <AdminCard title="Page Content">
        <FormWithStatus action={updateAboutContent} buttonText="Save Content">
          <AdminInput label="Hero Title" name="content_hero_title" defaultValue={content.hero_title || ""} />
          <AdminInput label="Hero Subtitle" name="content_hero_subtitle" defaultValue={content.hero_subtitle || ""} />
          <AdminInput label="What I Do" name="content_what_i_do" defaultValue={content.what_i_do || ""} />
          <AdminTextarea label="Services List (one per line)" name="content_services_list" defaultValue={content.services_list || ""} rows={4} />
          <AdminInput label="Mission Title" name="content_mission_title" defaultValue={content.mission_title || ""} />
          <AdminTextarea label="Mission" name="content_mission" defaultValue={content.mission || ""} rows={4} />
        </FormWithStatus>
      </AdminCard>

      {/* Images */}
      <AdminCard title="Page Images">
        <FormWithStatus action={updateAboutContent} buttonText="Save Images">
          <div className="space-y-6">
            <ImageUpload label="Hero Image" name="content_hero_image" defaultValue={content.hero_image || "/quivira-hero.webp"} />
          </div>
        </FormWithStatus>
      </AdminCard>

      {/* Growth Timeline / Milestones */}
      <AdminCard title="Growth Timeline">
        <MilestoneEditor
          milestones={rawMilestones}
          upsertAction={upsertMilestone}
          deleteAction={deleteMilestone}
        />
      </AdminCard>

      {/* Values */}
      <AdminCard title="Values">
        <div className="space-y-3">
          {values.map((v) => (
            <div key={v.id} className="flex items-start justify-between rounded-lg bg-[#1a1a1a] p-3">
              <div>
                <span className="text-sm font-medium text-white">{v.title}</span>
                <span className="ml-2 text-xs text-[#555]">({v.icon})</span>
                <p className="mt-1 text-xs text-[#666]">{v.description}</p>
              </div>
              <DeleteButton action={async () => { "use server"; await deleteAboutValue(v.id); }} />
            </div>
          ))}
        </div>
        <div className="mt-6 border-t border-[#222] pt-6">
          <FormWithStatus action={upsertAboutValue} buttonText="Add Value">
            <input type="hidden" name="id" value="" />
            <div className="grid gap-4 md:grid-cols-3">
              <AdminInput label="Icon (Lucide)" name="icon" required placeholder="e.g. Crosshair" />
              <AdminInput label="Title" name="title" required />
              <AdminInput label="Sort Order" name="sortOrder" type="number" defaultValue="0" />
            </div>
            <AdminTextarea label="Description" name="description" required />
          </FormWithStatus>
        </div>
      </AdminCard>

      {/* Ecosystem */}
      <AdminCard title="Ecosystem">
        <div className="space-y-3">
          {ecosystem.map((e) => (
            <div key={e.id} className="flex items-start justify-between rounded-lg bg-[#1a1a1a] p-3">
              <div>
                <span className="text-sm font-medium text-white">{e.name}</span>
                <span className="ml-2 text-xs text-[#E63946]">{e.role}</span>
                <p className="mt-1 text-xs text-[#666]">{e.description}</p>
              </div>
              <DeleteButton action={async () => { "use server"; await deleteEcosystem(e.id); }} />
            </div>
          ))}
        </div>
        <div className="mt-6 border-t border-[#222] pt-6">
          <FormWithStatus action={upsertEcosystem} buttonText="Add">
            <input type="hidden" name="id" value="" />
            <div className="grid gap-4 md:grid-cols-3">
              <AdminInput label="Name" name="name" required />
              <AdminInput label="Role" name="role" required />
              <AdminInput label="Sort Order" name="sortOrder" type="number" defaultValue="0" />
            </div>
            <AdminTextarea label="Description" name="description" required />
          </FormWithStatus>
        </div>
      </AdminCard>
    </div>
  );
}
