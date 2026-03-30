import { getAboutValues, getAboutEcosystem, getAboutContent, getMarqueeItems, getMilestones } from "@/lib/queries";
import { AboutClient } from "@/components/AboutClient";

export const revalidate = 60;

export default async function AboutPage() {
  const [values, ecosystem, content, marqueeItems, milestones] = await Promise.all([
    getAboutValues(),
    getAboutEcosystem(),
    getAboutContent(),
    getMarqueeItems("about"),
    getMilestones(),
  ]);

  return (
    <AboutClient
      content={content}
      values={values}
      ecosystem={ecosystem}
      marqueeItems={marqueeItems}
      milestones={milestones}
    />
  );
}
