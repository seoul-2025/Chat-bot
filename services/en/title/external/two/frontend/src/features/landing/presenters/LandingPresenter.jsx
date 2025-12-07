import React from "react";
import { Zap, Sparkles, ArrowRight, CheckCircle2 } from "lucide-react";
import Header from "../../../layouts/Header";

const LandingPresenter = ({
  // Data props
  isVisible,
  selectedEngine,
  articleInput,
  showArticleInput,
  stats,
  engines,
  features,
  userRole,

  // Action props
  onEngineSelect,
  onArticleInputChange,
  onProceedWithArticle,
  onCancelArticleInput,
  onLogout,
  onLogin,
}) => {
  return (
    <div className="min-h-screen overflow-x-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900" />
        <div className="absolute inset-0">
          <div className="absolute top-0 -left-4 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob" />
          <div className="absolute top-0 -right-4 w-72 h-72 bg-yellow-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000" />
          <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000" />
        </div>
      </div>

      {/* Header Component */}
      <Header
        onLogout={onLogout}
        onAdminLogin={() => onLogin && onLogin("admin")}
        onHome={() => window.location.reload()}
        isLandingPage={true}
        userRole={userRole}
      />

      {/* Main Content */}
      <main className="relative z-10">
        <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Hero Section */}
          <div
            className={`text-center mb-16 transition-all duration-1000 ${
              isVisible
                ? "opacity-100 translate-y-0"
                : "opacity-0 translate-y-10"
            }`}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-500/10 border border-purple-500/20 rounded-full mb-6">
              <Sparkles className="w-4 h-4 text-purple-400" />
              <span className="text-sm text-purple-300">
                AI-Powered Title Generation Platform
              </span>
            </div>

            <h1 className="text-6xl md:text-7xl font-bold mb-6">
              <span className="bg-gradient-to-r from-white via-purple-200 to-white bg-clip-text text-transparent animate-gradient">
                TITLE-HUB
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-300 mb-4">
              Seoul Economic Daily AI Title Generation System
            </p>
          </div>

          {/* Stats Section - Removed */}

          {/* Product Selection */}
          <div className="main-content">
            <div className="product-selection">
              <h2
                className={`text-2xl md:text-3xl font-bold text-center mb-12 text-white transition-all duration-1000 delay-300 ${
                  isVisible
                    ? "opacity-100 translate-y-0"
                    : "opacity-0 translate-y-10"
                }`}
              >
                Your First Meeting with Readers - We Recommend the Perfect Title
              </h2>

              <div className="grid md:grid-cols-2 gap-8 mb-12">
                {/* C1 Card */}
                <div
                  className={`relative group transition-all duration-500 delay-400 ${
                    isVisible
                      ? "opacity-100 translate-y-0"
                      : "opacity-0 translate-y-10"
                  }`}
                  onClick={() => onEngineSelect("11")}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-orange-600 to-red-600 rounded-2xl blur-xl opacity-20 group-hover:opacity-40 transition-opacity" />
                  <div className="relative bg-gray-900/90 backdrop-blur-xl rounded-2xl p-8 border border-gray-700 hover:border-orange-500/50 transition-all cursor-pointer hover:transform hover:scale-105 min-h-[500px] flex flex-col">
                    <div className="flex justify-between items-start mb-6">
                      <div className="flex items-center gap-4">
                        <div className="p-3 bg-gradient-to-br from-orange-500 to-red-500 rounded-xl">
                          <Zap className="w-8 h-8 text-white" />
                        </div>
                        <div>
                          <h3 className="text-3xl font-bold text-white mb-1">
                            T5
                          </h3>
                          <p className="text-orange-400 text-sm font-medium">
                            Penetrating the Core Titles
                          </p>
                        </div>
                      </div>
                      <div className="px-3 py-1 bg-orange-500/20 border border-orange-500/30 rounded-full">
                        <span className="text-xs text-orange-300">
                          RECOMMENDED
                        </span>
                      </div>
                    </div>

                    <p className="text-gray-300 mb-6">
                      5 Different Perspectives - Generate <span className="text-orange-400 font-semibold">Type-Specific</span> Differentiated Titles
                    </p>

                    <div className="space-y-3 mb-6 flex-grow">
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-orange-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Journalism-Focused (Credibility Centered)
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-orange-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Balanced Hooking (Information + Curiosity)
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-orange-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Click-Driven (Maximize Engagement)
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-orange-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          SEO Optimized (Search Visibility)
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-orange-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Social Media Style (Viral Spread)
                        </span>
                      </div>
                    </div>

                    <button className="w-full bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold py-3 px-6 rounded-xl hover:from-orange-600 hover:to-red-600 transition-all flex items-center justify-center gap-2 group mt-auto">
                      Choose T5
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </button>
                  </div>
                </div>

                {/* C2 Card */}
                <div
                  className={`relative group transition-all duration-500 delay-500 ${
                    isVisible
                      ? "opacity-100 translate-y-0"
                      : "opacity-0 translate-y-10"
                  }`}
                  onClick={() => onEngineSelect("22")}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur-xl opacity-20 group-hover:opacity-40 transition-opacity" />
                  <div className="relative bg-gray-900/90 backdrop-blur-xl rounded-2xl p-8 border border-gray-700 hover:border-blue-500/50 transition-all cursor-pointer hover:transform hover:scale-105 min-h-[500px] flex flex-col">
                    <div className="flex justify-between items-start mb-6">
                      <div className="flex items-center gap-4">
                        <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl">
                          <Sparkles className="w-8 h-8 text-white" />
                        </div>
                        <div>
                          <h3 className="text-3xl font-bold text-white mb-1">
                            C7
                          </h3>
                          <p className="text-blue-400 text-sm font-medium">
                            <span className="block">
                              Explosive Creativity, Beyond Your Imagination
                            </span>
                          </p>
                        </div>
                      </div>
                      <div className="px-3 py-1 bg-blue-500/20 border border-blue-500/30 rounded-full">
                        <span className="text-xs text-blue-300">CREATIVE</span>
                      </div>
                    </div>

                    <p className="text-gray-300 mb-6">
                      <span className="block md:inline">
                        7 Creative Engines for{" "}
                        <span className="text-blue-400 font-semibold">
                          Every Time
                        </span>{" "}
                        a Masterpiece Title
                      </span>
                    </p>

                    <div className="space-y-3 mb-6 flex-grow">
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-blue-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Language Innovation Engine (Industry-First Expression)
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-blue-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Collision Generation Engine (Aha! Moment Guaranteed)
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-blue-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Emotion Amplification Engine (Share Immediately)
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-blue-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Perspective Shift Engine (Unseen Angle)
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-blue-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Cultural Code Engine (Resonance with Zeitgeist)
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-blue-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Future Forecast Engine (Trend Leading)
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-blue-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Viral Design Engine (Maximum Buzz)
                        </span>
                      </div>
                    </div>

                    <button className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold py-3 px-6 rounded-xl hover:from-blue-600 hover:to-purple-600 transition-all flex items-center justify-center gap-2 group mt-auto">
                      Choose C7
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Features Grid - Removed */}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default LandingPresenter;
