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
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-emerald-950/30 to-gray-900" />
        <div className="absolute inset-0">
          <div className="absolute top-0 -left-4 w-72 h-72 bg-emerald-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob" />
          <div className="absolute top-0 -right-4 w-72 h-72 bg-teal-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000" />
          <div className="absolute -bottom-8 left-20 w-72 h-72 bg-cyan-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000" />
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
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full mb-6">
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <span className="text-sm text-emerald-300">
                AI Editor - Elevating Journalism Quality
              </span>
            </div>

            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              <span className="bg-gradient-to-r from-white via-emerald-200 to-white bg-clip-text text-transparent animate-gradient">
                Articles That Get Read vs. Articles That Get Buried.<br/>The Difference Is Editing.
              </span>
            </h1>

            <p className="text-lg md:text-xl text-gray-300 mb-4 max-w-4xl mx-auto leading-relaxed">
              Even exclusives can die in the first paragraph, and weak articles can be revived with better structure.<br/>
              Without editing, an article remains a rough draft. Editing completes the story.
            </p>

            <p className="text-base md:text-lg text-emerald-400 font-medium">
              No time for editing? AI Editor takes just 3 minutes.
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
                Choose Your Editing Type
              </h2>

              <div className="grid md:grid-cols-2 gap-8 mb-12">
                {/* Quick Edit Card */}
                <div
                  className={`relative group transition-all duration-500 delay-400 ${
                    isVisible
                      ? "opacity-100 translate-y-0"
                      : "opacity-0 translate-y-10"
                  }`}
                  onClick={() => onEngineSelect("11")}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-orange-600 to-red-600 rounded-2xl blur-xl opacity-20 group-hover:opacity-40 transition-opacity" />
                  <div className="relative bg-gray-900/90 backdrop-blur-xl rounded-2xl p-8 border border-gray-700 hover:border-orange-500/50 transition-all cursor-pointer hover:transform hover:scale-105 min-h-[550px] flex flex-col">
                    <div className="flex justify-between items-start mb-6">
                      <div className="flex items-center gap-4">
                        <div className="p-3 bg-gradient-to-br from-orange-500 to-red-500 rounded-xl">
                          <Zap className="w-8 h-8 text-white" />
                        </div>
                        <div>
                          <h3 className="text-2xl font-bold text-white mb-1">
                            📱 Quick Edit
                          </h3>
                          <p className="text-orange-400 text-sm font-medium">
                            Fast Article Editing
                          </p>
                        </div>
                      </div>
                      <div className="px-3 py-1 bg-orange-500/20 border border-orange-500/30 rounded-full">
                        <span className="text-xs text-orange-300">
                          Under 1,000 words
                        </span>
                      </div>
                    </div>

                    <p className="text-gray-100 mb-6 text-lg font-semibold">
                      "The Opening Sentence Problem Solved"
                    </p>

                    <div className="space-y-3 mb-6 flex-grow">
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-orange-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          "Where do I start?" → 3 killer opening suggestions
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-orange-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Buried paragraph 5 exclusive → Paragraph 1 punchline
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-orange-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          "3 trillion won" → "60,000 won per person" relatability conversion
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-orange-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Seoul Economic style auto-applied (last year/this year/%points)
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-orange-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Mobile first screen optimized (2-second decision)
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-orange-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Pre-desk feedback correction
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-orange-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          70% mobile bounce rate → Scroll to the end
                        </span>
                      </div>
                    </div>

                    <button className="w-full bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold py-3 px-6 rounded-xl hover:from-orange-600 hover:to-red-600 transition-all flex items-center justify-center gap-2 group mt-auto">
                      Quick Edit Now
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </button>
                  </div>
                </div>

                {/* Deep Edit Card */}
                <div
                  className={`relative group transition-all duration-500 delay-500 ${
                    isVisible
                      ? "opacity-100 translate-y-0"
                      : "opacity-0 translate-y-10"
                  }`}
                  onClick={() => onEngineSelect("22")}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur-xl opacity-20 group-hover:opacity-40 transition-opacity" />
                  <div className="relative bg-gray-900/90 backdrop-blur-xl rounded-2xl p-8 border border-gray-700 hover:border-blue-500/50 transition-all cursor-pointer hover:transform hover:scale-105 min-h-[550px] flex flex-col">
                    <div className="flex justify-between items-start mb-6">
                      <div className="flex items-center gap-4">
                        <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl">
                          <Sparkles className="w-8 h-8 text-white" />
                        </div>
                        <div>
                          <h3 className="text-2xl font-bold text-white mb-1">
                            📄 Deep Edit
                          </h3>
                          <p className="text-blue-400 text-sm font-medium">
                            Structural Analysis Editing
                          </p>
                        </div>
                      </div>
                      <div className="px-3 py-1 bg-blue-500/20 border border-blue-500/30 rounded-full">
                        <span className="text-xs text-blue-300">Over 1,000 words</span>
                      </div>
                    </div>

                    <p className="text-gray-100 mb-6 text-lg font-semibold">
                      "Articles That Get Read to the End"
                    </p>

                    <div className="space-y-3 mb-6 flex-grow">
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-blue-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          "Readers drop off mid-story" → Tension-maintaining structure design
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-blue-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Flat listing → Dramatic narrative structure
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-blue-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Boring data → Engaging story
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-blue-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          "Too long" → "Already finished?"
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-blue-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Structure that even rival journalists read to the end
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-blue-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Buried killer facts discovered → Placed in perfect spots
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-blue-400 flex-shrink-0" />
                        <span className="text-gray-300 text-sm">
                          Reader fatigue management (breathing spots placed)
                        </span>
                      </div>
                    </div>

                    <button className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold py-3 px-6 rounded-xl hover:from-blue-600 hover:to-purple-600 transition-all flex items-center justify-center gap-2 group mt-auto">
                      Deep Edit Now
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
