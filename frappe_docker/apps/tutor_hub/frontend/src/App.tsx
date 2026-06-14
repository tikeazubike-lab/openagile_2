import { useLandingData } from "@/hooks/useLandingData";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import HeroSection from "@/components/home/HeroSection";
import StatsSection from "@/components/home/StatsSection";
import SubjectsSection from "@/components/home/SubjectsSection";
import HowItWorksSection from "@/components/home/HowItWorksSection";
import TestimonialsSection from "@/components/home/TestimonialsSection";
import CTASection from "@/components/home/CTASection";

export default function App() {
  const { data, isLoading, isError } = useLandingData();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center text-center px-4">
        <div>
          <h1 className="text-2xl font-bold mb-2">Unable to load page</h1>
          <p className="text-muted-foreground">
            Please refresh or try again later.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        {/* id attributes match href anchors in cta_primary/cta_secondary — no react-router needed */}
        <section id="home">
          <HeroSection
            title={data.hero_title}
            subtitle={data.hero_subtitle}
            ctaPrimary={data.cta_primary}
            ctaSecondary={data.cta_secondary}
            tutors={data.featured_tutors}
          />
        </section>

        <StatsSection stats={data.stats} />

        <section id="subjects">
          <SubjectsSection subjects={data.subjects} />
        </section>

        <section id="how-it-works">
          <HowItWorksSection steps={data.how_it_works} />
        </section>

        <section id="tutors">
          {/* Carousel reused in hero; this section is the anchor target */}
        </section>

        <TestimonialsSection testimonials={data.testimonials} />

        <CTASection cta={data.cta_primary} />
      </main>
      <Footer />
    </div>
  );
}
