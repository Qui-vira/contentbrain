import { createClient } from "@supabase/supabase-js";
import { ArticlesClient } from "@/components/ArticlesClient";

export const revalidate = 60;

const supabase = createClient(
  "https://bnoqtghdptobbtrssmdj.supabase.co",
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJub3F0Z2hkcHRvYmJ0cnNzbWRqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM1OTYwMjQsImV4cCI6MjA4OTE3MjAyNH0.-Jl2_r83rEmKiyWAJOY5MCqPIiateTYYWlcW8bvYTLY"
);

export default async function ArticlesPage() {
  const { data: articles } = await supabase
    .from("cta_documents")
    .select("slug, title, cta_keyword, video_title, views, created_at")
    .order("created_at", { ascending: false });

  return <ArticlesClient articles={articles ?? []} />;
}
