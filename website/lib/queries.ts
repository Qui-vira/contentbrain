import { db } from "./db";
import { eq, asc } from "drizzle-orm";

import * as s from "./schema";

// ─── Settings ───
export async function getSettings() {

  const rows = await db.select().from(s.settings);
  return Object.fromEntries(rows.map((r) => [r.key, r.value]));
}

export async function getSetting(key: string) {

  const [row] = await db.select().from(s.settings).where(eq(s.settings.key, key));
  return row?.value ?? "";
}

// ─── Social links ───
export async function getSocialLinks() {

  return db.select().from(s.socialLinks).orderBy(asc(s.socialLinks.sortOrder));
}

// ─── Stats ───
export async function getStats(page: string) {

  return db.select().from(s.stats).where(eq(s.stats.page, page)).orderBy(asc(s.stats.sortOrder));
}

// ─── Services ───
export async function getServices(category: string) {

  return db.select().from(s.services).where(eq(s.services.category, category)).orderBy(asc(s.services.sortOrder));
}

export async function getAllServices() {

  return db.select().from(s.services).orderBy(asc(s.services.sortOrder));
}

// ─── Personal services ───
export async function getPersonalServices() {

  return db.select().from(s.personalServices).orderBy(asc(s.personalServices.sortOrder));
}

// ─── Pricing tiers ───
export async function getPricingTiers(product: string) {

  return db.select().from(s.pricingTiers).where(eq(s.pricingTiers.product, product)).orderBy(asc(s.pricingTiers.sortOrder));
}

// ─── Pricing features ───
export async function getPricingFeatures(product: string) {

  return db.select().from(s.pricingFeatures).where(eq(s.pricingFeatures.product, product)).orderBy(asc(s.pricingFeatures.sortOrder));
}

// ─── FAQ ───
export async function getFaqItems() {

  return db.select().from(s.faqItems).orderBy(asc(s.faqItems.sortOrder));
}

// ─── Testimonials ───
export async function getTestimonials(page: string) {

  const rows = await db.select().from(s.testimonials).where(eq(s.testimonials.page, page)).orderBy(asc(s.testimonials.sortOrder));
  return rows.map((r) => {
    let parsedImages: string[] = [];
    try { parsedImages = r.images ? JSON.parse(r.images) : []; } catch { parsedImages = []; }
    if (parsedImages.length === 0 && r.image) parsedImages = [r.image];
    return { ...r, allImages: parsedImages };
  });
}

// ─── Client logos ───
export async function getClientLogos() {

  return db.select().from(s.clientLogos).orderBy(asc(s.clientLogos.sortOrder));
}

// ─── Case studies ───
export async function getCaseStudies() {

  const studies = await db.select().from(s.caseStudies).orderBy(asc(s.caseStudies.sortOrder));
  const allStats = await db.select().from(s.caseStudyStats).orderBy(asc(s.caseStudyStats.sortOrder));

  return studies.map((cs) => {
    let parsedImages: string[] = [];
    try { parsedImages = cs.images ? JSON.parse(cs.images) : []; } catch { parsedImages = []; }
    if (parsedImages.length === 0 && cs.image) parsedImages = [cs.image];
    let parsedVideos: string[] = [];
    try { parsedVideos = cs.videos ? JSON.parse(cs.videos) : []; } catch { parsedVideos = []; }
    return {
      ...cs,
      stats: allStats.filter((st) => st.caseStudyId === cs.id).map((st) => st.stat),
      allImages: parsedImages,
      allVideos: parsedVideos,
    };
  });
}

// ─── About ───
export async function getAboutValues() {

  return db.select().from(s.aboutValues).orderBy(asc(s.aboutValues.sortOrder));
}

export async function getAboutEcosystem() {

  return db.select().from(s.aboutEcosystem).orderBy(asc(s.aboutEcosystem.sortOrder));
}

export async function getAboutContent() {

  const rows = await db.select().from(s.aboutContent);
  return Object.fromEntries(rows.map((r) => [r.key, r.value]));
}

// ─── Milestones (about timeline) ───
export async function getMilestones() {

  const rows = await db.select().from(s.milestones).orderBy(asc(s.milestones.sortOrder));
  return rows.map((r) => {
    let parsedImages: string[] = [];
    try { parsedImages = r.images ? JSON.parse(r.images) : []; } catch { parsedImages = []; }
    // Merge legacy single image into array if images is empty
    if (parsedImages.length === 0 && r.image) parsedImages = [r.image];
    return {
      ...r,
      allImages: parsedImages,
      imageLayout: (r.imageLayout || "carousel") as "carousel" | "grid",
    };
  });
}

// ─── CTA banners ───
export async function getCtaBanner(page: string) {

  const [row] = await db.select().from(s.ctaBanners).where(eq(s.ctaBanners.page, page));
  return row;
}

// ─── Contact ───
export async function getContactOptions() {

  return db.select().from(s.contactOptions).orderBy(asc(s.contactOptions.sortOrder));
}

export async function getServiceOptions() {

  return db.select().from(s.serviceOptions).orderBy(asc(s.serviceOptions.sortOrder));
}

// ─── Marquee ───
export async function getMarqueeItems(page: string) {

  const rows = await db.select().from(s.marqueeItems).where(eq(s.marqueeItems.page, page)).orderBy(asc(s.marqueeItems.sortOrder));
  return rows.map((r) => r.text);
}
