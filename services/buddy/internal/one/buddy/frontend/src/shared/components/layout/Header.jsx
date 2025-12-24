import React from "react";
import { Menu, BarChart3, Home } from "lucide-react";

// 로그인 비활성화 버전 - 로그인/로그아웃 UI 제거
const Header = ({
  onHome,
  chatTitle,
  onToggleSidebar,
  isSidebarOpen = false,
  onDashboard,
  isLandingPage = false,
}) => {
  return (
    <header
      className={`sticky top-0 z-50 w-full transition-all duration-200 ${
        isLandingPage ? "border-b border-gray-800" : ""
      }`}
      style={{
        backdropFilter: "blur(12px)",
        backgroundColor: isLandingPage
          ? "rgba(15, 15, 15, 0.95)"
          : "hsl(var(--bg-100)/0.95)",
      }}
    >
      <div className="w-full px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 relative">
          <div className="flex items-center space-x-4">
            {/* 사이드바 토글 버튼 - 사이드바가 닫혀있을 때만 표시 */}
            {onToggleSidebar && !isSidebarOpen && (
              <button
                className="p-2 rounded-md text-text-300 hover:bg-bg-300 hover:text-text-100 transition-colors"
                onClick={onToggleSidebar}
                aria-label="사이드바 열기"
              >
                <Menu size={24} />
              </button>
            )}

            {/* 홈 버튼 */}
            {onHome && (
              <button
                className="flex items-center space-x-2 p-2 rounded-md text-text-300 hover:bg-bg-300 hover:text-text-100 transition-colors"
                onClick={onHome}
              >
                <Home size={20} />
                <span className="hidden sm:inline text-sm font-medium">
                  Article Buddy
                </span>
              </button>
            )}
          </div>

          {/* 채팅 제목 (가운데) */}
          {chatTitle && (
            <div className="flex-1 flex justify-center mx-4">
              <h1 className="text-text-100 font-medium text-sm lg:text-base truncate max-w-md">
                {chatTitle}
              </h1>
            </div>
          )}

          <div className="ml-auto flex items-center space-x-4">
            {/* 대시보드 버튼 */}
            {onDashboard && (
              <div className="hidden md:block">
                <button
                  className="flex items-center space-x-2 px-5 py-3 rounded-lg text-sm font-semibold transition-all duration-200 text-text-300 hover:bg-bg-300 hover:text-text-100"
                  onClick={onDashboard}
                >
                  <BarChart3 size={20} />
                  <span>대시보드</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
