import { AppShell } from "@/components/layout/app-shell";
import { AssetInput } from "@/components/features/home/asset-input";
import { SystemStatus } from "@/components/features/system/status";
import { getTranslations } from "next-intl/server";

/**
 * Home Page (Landing)
 * 
 * The default route (`/`) of the application.
 * Designed to be clean and focused, similar to a search engine's homepage.
 * 
 * Structure:
 * - **AppShell**: Wraps content with standard navigation.
 * - **Hero Section**: Title and concise value proposition.
 * - **AssetInput**: Central interactive component for starting an analysis.
 * - **SystemStatus**: Subtle monitoring indicator.
 * 
 * @returns {JSX.Element} The landing page view
 */
export default async function Home() {
  const t = await getTranslations("home");

  return (
    <AppShell>
      <div className="flex flex-col items-center justify-center min-h-[80vh] gap-8 animate-in fade-in duration-700">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
            {t("title")}
          </h1>
          <p className="text-xl text-muted-foreground max-w-[600px] mx-auto">
            {t("subtitle")}
          </p>
        </div>

        <AssetInput />

        <SystemStatus />
      </div>
    </AppShell>
  );
}
