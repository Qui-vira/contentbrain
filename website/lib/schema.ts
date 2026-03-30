import { sqliteTable, text, integer, real } from "drizzle-orm/sqlite-core";

// ─── Key-value settings (Calendly URL, email, etc.) ───
export const settings = sqliteTable("settings", {
  key: text("key").primaryKey(),
  value: text("value").notNull(),
});

// ─── Social links ───
export const socialLinks = sqliteTable("social_links", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  name: text("name").notNull(),
  href: text("href").notNull(),
  sortOrder: integer("sort_order").notNull().default(0),
});

// ─── Trust bar / results stats ───
export const stats = sqliteTable("stats", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  page: text("page").notNull(), // "home_trust", "home_results", "portfolio"
  label: text("label").notNull(),
  value: integer("value").notNull(),
  suffix: text("suffix").default(""),
  sortOrder: integer("sort_order").notNull().default(0),
});

// ─── Services (consulting, education, AI products) ───
export const services = sqliteTable("services", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  category: text("category").notNull(), // "consulting", "education", "ai_products"
  title: text("title").notNull(),
  description: text("description").notNull(),
  price: text("price"),
  priceDetail: text("price_detail"),
  icon: text("icon"), // lucide icon name
  ctaText: text("cta_text"),
  ctaHref: text("cta_href"),
  sortOrder: integer("sort_order").notNull().default(0),
});

// ─── Pricing tiers (SignalOS, ContentBrain, Quivira OS) ───
export const pricingTiers = sqliteTable("pricing_tiers", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  product: text("product").notNull(), // "signalos", "contentbrain", "quivira_os"
  productTitle: text("product_title").notNull(),
  productSubtitle: text("product_subtitle").notNull(),
  tierKey: text("tier_key").notNull(), // "starter", "pro", "premium"
  tierLabel: text("tier_label").notNull(),
  tierPrice: text("tier_price").notNull(),
  sortOrder: integer("sort_order").notNull().default(0),
});

// ─── Pricing features per product ───
export const pricingFeatures = sqliteTable("pricing_features", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  product: text("product").notNull(),
  featureName: text("feature_name").notNull(),
  starter: text("starter").notNull(), // "true", "false", or string value
  pro: text("pro").notNull(),
  premium: text("premium").notNull(),
  sortOrder: integer("sort_order").notNull().default(0),
});

// ─── Personal services table (pricing page) ───
export const personalServices = sqliteTable("personal_services", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  name: text("name").notNull(),
  price: text("price").notNull(),
  detail: text("detail").notNull(),
  sortOrder: integer("sort_order").notNull().default(0),
});

// ─── FAQ items ───
export const faqItems = sqliteTable("faq_items", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  question: text("question").notNull(),
  answer: text("answer").notNull(),
  sortOrder: integer("sort_order").notNull().default(0),
});

// ─── Testimonials ───
export const testimonials = sqliteTable("testimonials", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  page: text("page").notNull(), // "home", "portfolio"
  quote: text("quote").notNull(),
  attribution: text("attribution").notNull(),
  image: text("image"), // single image
  images: text("images"), // JSON array of image URLs
  rating: integer("rating").notNull().default(5),
  avatar: text("avatar"),
  category: text("category").notNull().default("general"),
  sortOrder: integer("sort_order").notNull().default(0),
});

// ─── Case studies ───
export const caseStudies = sqliteTable("case_studies", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  title: text("title").notNull(),
  image: text("image"), // single image
  images: text("images"), // JSON array of image URLs
  videos: text("videos"), // JSON array of video URLs
  sortOrder: integer("sort_order").notNull().default(0),
});

// ─── Case study stats (bullet points) ───
export const caseStudyStats = sqliteTable("case_study_stats", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  caseStudyId: integer("case_study_id").notNull(),
  stat: text("stat").notNull(),
  sortOrder: integer("sort_order").notNull().default(0),
});

// ─── About page values ───
export const aboutValues = sqliteTable("about_values", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  icon: text("icon").notNull(), // lucide icon name
  title: text("title").notNull(),
  description: text("description").notNull(),
  sortOrder: integer("sort_order").notNull().default(0),
});

// ─── About page ecosystem ───
export const aboutEcosystem = sqliteTable("about_ecosystem", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  name: text("name").notNull(),
  role: text("role").notNull(),
  description: text("description").notNull(),
  sortOrder: integer("sort_order").notNull().default(0),
});

// ─── About page long-form content (story, mission) ───
export const aboutContent = sqliteTable("about_content", {
  key: text("key").primaryKey(), // "story", "mission", "hero_title", "hero_subtitle"
  value: text("value").notNull(),
});

// ─── CTA banners across pages ───
export const ctaBanners = sqliteTable("cta_banners", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  page: text("page").notNull(), // "home", "pricing", "services", "portfolio"
  headline: text("headline").notNull(),
  subtext: text("subtext").notNull(),
  buttonText: text("button_text").notNull(),
  buttonHref: text("button_href").notNull(),
});

// ─── Contact options (cards) ───
export const contactOptions = sqliteTable("contact_options", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  icon: text("icon").notNull(), // lucide icon name
  title: text("title").notNull(),
  description: text("description").notNull(),
  href: text("href").notNull(),
  sortOrder: integer("sort_order").notNull().default(0),
});

// ─── Contact form service dropdown options ───
export const serviceOptions = sqliteTable("service_options", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  name: text("name").notNull(),
  sortOrder: integer("sort_order").notNull().default(0),
});

// ─── Marquee items per page ───
export const marqueeItems = sqliteTable("marquee_items", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  page: text("page").notNull(), // "home", "pricing", "services", "about"
  text: text("text").notNull(),
  sortOrder: integer("sort_order").notNull().default(0),
});

// ─── About page milestones (timeline) ───
export const milestones = sqliteTable("milestones", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  year: text("year").notNull(),
  title: text("title").notNull(),
  text: text("text").notNull(),
  image: text("image"), // legacy single image
  images: text("images"), // JSON array of image URLs
  imageLayout: text("image_layout").default("carousel"), // "carousel" | "grid"
  sortOrder: integer("sort_order").notNull().default(0),
});

// ─── Client logos ───
export const clientLogos = sqliteTable("client_logos", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  name: text("name").notNull(),
  image: text("image").notNull(),
  sortOrder: integer("sort_order").notNull().default(0),
});

// ─── Admin user ───
export const adminUsers = sqliteTable("admin_users", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  username: text("username").notNull().unique(),
  passwordHash: text("password_hash").notNull(),
});
