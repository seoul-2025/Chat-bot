import React, {
  useState,
  useEffect,
  forwardRef,
  useImperativeHandle,
} from "react";
import { Link, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  Plus,
  Star,
  ChevronLeft,
  MoreHorizontal,
  User,
  X,
  Edit2,
  Check,
} from "lucide-react";
import {
  listConversations,
  deleteConversation,
  updateConversationTitle,
} from "../features/chat/services/conversationService";

const Sidebar = forwardRef(
  ({ selectedEngine = "11", isOpen = true, onToggle }, ref) => {
    const location = useLocation();
    const [conversations, setConversations] = useState([]);
    const [favorites, setFavorites] = useState([]);
    const [loading, setLoading] = useState(true);
    const [deleteModal, setDeleteModal] = useState({
      open: false,
      conversationId: null,
      title: "",
    });
    const [isMobile, setIsMobile] = useState(() => {
      // 초기값을 안전하게 설정
      if (typeof window !== "undefined") {
        return window.innerWidth < 768;
      }
      return false;
    });

    // 대화 목록 불러오기
    useEffect(() => {
      loadConversations();
    }, [selectedEngine]);

    // refreshSidebar 이벤트 리스너 추가
    useEffect(() => {
      const handleRefresh = () => {
        console.log("🔄 사이드바 새로고침 이벤트 수신");
        loadConversations();
      };

      window.addEventListener("refreshSidebar", handleRefresh);
      return () => window.removeEventListener("refreshSidebar", handleRefresh);
    }, [selectedEngine]);

    // 화면 크기 변경 감지
    useEffect(() => {
      const handleResize = () => {
        const mobile = window.innerWidth < 768;
        const wasMobile = isMobile;
        setIsMobile(mobile);

        // 데스크톱에서 모바일로 전환될 때만 자동 닫기
        // (이미 모바일인 상태에서는 사용자가 열 수 있도록 허용)
        if (!wasMobile && mobile && isOpen) {
          onToggle?.();
        }
      };

      // 초기 체크 (자동 닫기 없이)
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);

      window.addEventListener("resize", handleResize);
      return () => window.removeEventListener("resize", handleResize);
    }, [isOpen, onToggle, isMobile]);

    const loadConversations = async () => {
      try {
        setLoading(true);
        const convs = await listConversations(selectedEngine);

        console.log(`📊 사이드바 대화 목록 (${selectedEngine}):`, {
          totalCount: convs.length,
          first5: convs.slice(0, 5).map((c) => ({
            id: c.conversationId,
            title: c.title,
            updatedAt: c.updatedAt,
            engineType: c.engineType,
          })),
        });

        setConversations(convs);
        // localStorage에서 즐겨찾기 불러오기
        const savedFavorites = JSON.parse(
          localStorage.getItem("favorites") || "[]"
        );
        setFavorites(savedFavorites);
      } catch (error) {
        console.error("대화 목록 불러오기 실패:", error);
      } finally {
        setLoading(false);
      }
    };

    // ref로 노출할 메서드
    useImperativeHandle(ref, () => ({
      loadConversations,
    }));

    const toggleFavorite = (conversationId) => {
      const newFavorites = favorites.includes(conversationId)
        ? favorites.filter((id) => id !== conversationId)
        : [...favorites, conversationId];

      setFavorites(newFavorites);
      localStorage.setItem("favorites", JSON.stringify(newFavorites));
    };

    const handleDeleteClick = (conversationId, title) => {
      setDeleteModal({ open: true, conversationId, title });
    };

    const handleDeleteConfirm = async () => {
      if (!deleteModal.conversationId) return;

      try {
        await deleteConversation(deleteModal.conversationId);
        // 목록 즉시 새로고침
        await loadConversations();
        setDeleteModal({ open: false, conversationId: null, title: "" });
      } catch (error) {
        console.error("대화 삭제 실패:", error);
        // 에러가 발생해도 localStorage에서는 삭제되므로 목록 새로고침
        await loadConversations();
        setDeleteModal({ open: false, conversationId: null, title: "" });
      }
    };

    const handleDeleteCancel = () => {
      setDeleteModal({ open: false, conversationId: null, title: "" });
    };

    const favoriteConversations = conversations.filter((conv) =>
      favorites.includes(conv.conversationId)
    );

    const recentConversations = conversations.filter(
      (conv) => !favorites.includes(conv.conversationId)
    );

    return (
      <>
        {/* Delete Confirmation Modal */}
        {deleteModal.open && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
              className="absolute inset-0 bg-black/50"
              onClick={handleDeleteCancel}
            />

            {/* Modal */}
            <div
              className="relative flex flex-col focus:outline-none text-text-100 text-left shadow-xl 
            rounded-2xl p-6 align-middle bg-bg-100 
            min-w-0 w-full max-w-md animate-[zoom_250ms_ease-in_forwards]"
            >
              <div className="min-h-full flex flex-col">
                <div className="flex items-center gap-4 justify-between">
                  <h2 className="font-xl-bold text-text-100 flex w-full min-w-0 items-center leading-6 break-words">
                    <span className="[overflow-wrap:anywhere]">Delete Conversation</span>
                  </h2>
                  <button
                    onClick={handleDeleteCancel}
                    className="p-1 rounded hover:bg-bg-300 transition-colors"
                  >
                    <X size={20} />
                  </button>
                </div>
                <div className="mt-1 mb-2">
                  Are you sure you want to delete this conversation?
                  {deleteModal.title && (
                    <div className="mt-2 text-sm text-text-300">
                      "{deleteModal.title}"
                    </div>
                  )}
                </div>
                <div className="mt-4 flex flex-col gap-2 sm:flex-row justify-end">
                  <button
                    onClick={handleDeleteCancel}
                    className="inline-flex items-center justify-center relative h-9 px-4 py-2 rounded-lg 
                    min-w-[5rem] text-text-100 font-medium 
                    bg-bg-300 hover:bg-bg-400 transition duration-100 active:scale-[0.985]"
                    type="button"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleDeleteConfirm}
                    className="inline-flex items-center justify-center relative h-9 px-4 py-2 rounded-lg
                    min-w-[5rem] bg-red-600 text-white font-medium transition
                    hover:bg-red-700 hover:scale-[1.02] active:scale-[0.985]"
                    type="button"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 모바일 오버레이 */}
        {isOpen && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
            onClick={onToggle}
          />
        )}

        <motion.nav
          animate={{
            width: isOpen ? (isMobile ? "75vw" : 288) : 0,
            opacity: isOpen ? 1 : 0,
          }}
          transition={{
            type: "tween",
            ease: "easeInOut",
            duration: 0.2,
          }}
          className="h-screen flex flex-col gap-3 pb-2 px-0 fixed top-0 left-0
          shadow-lg bg-bg-200 z-50 overflow-hidden"
          style={{
            width: isOpen ? (isMobile ? "75vw" : "288px") : "0px",
          }}
          aria-label="사이드바"
        >
          {/* Header */}
          <div className="flex w-full items-center gap-px p-2">
            <button
              onClick={onToggle}
              className="h-8 w-8 rounded-md hover:bg-bg-300 flex items-center justify-center transition-colors"
              aria-label="사이드바 닫기"
            >
              <ChevronLeft size={20} />
            </button>

            <Link to="/" className="flex items-center ml-2">
              <span className="text-xl font-semibold text-text-100">
                {selectedEngine === "11" ? " T5" : " C7"}
              </span>
            </Link>
          </div>

          {/* New Chat Button */}
          <div className="flex flex-col px-1.5 pt-0.5 gap-px mb-2">
            <button
              onClick={() => {
                // 현재 URL에서 conversationId 추출
                const pathParts = location.pathname.split("/");
                const conversationId = pathParts[pathParts.length - 1];

                // 현재 대화의 캐시만 삭제 (다른 대화는 유지)
                if (conversationId && conversationId !== "chat") {
                  const cacheKey = `conv:${conversationId}`;
                  localStorage.removeItem(cacheKey);
                  console.log(`🗑️ 현재 대화 캐시 삭제: ${cacheKey}`);
                }

                // 임시 데이터 정리
                localStorage.removeItem("pendingMessage");
                localStorage.removeItem("pendingConversationId");

                // sessionStorage 정리 (모든 processed 키 제거)
                Object.keys(sessionStorage).forEach((key) => {
                  if (key.startsWith("processed_")) {
                    sessionStorage.removeItem(key);
                  }
                });

                console.log("🔄 새 채팅 시작 - 이전 대화 기록 정리 완료");

                // 모바일에서는 사이드바 닫기
                if (isMobile && onToggle) {
                  onToggle();
                }

                // 메인 페이지로 이동 (conversationId 없이)
                window.location.href = `/${selectedEngine.toLowerCase()}`;
              }}
              className="group flex items-center h-9 px-2.5 py-2 rounded-lg 
            hover:bg-accent-main-100/[0.08] active:bg-accent-main-100/[0.15]
            transition-all ease-in-out active:scale-[0.985] w-full text-left"
            >
              <div className="flex flex-row items-center gap-2">
                <div
                  className="w-6 h-6 flex items-center justify-center rounded-full 
              bg-accent-main-100 group-hover:bg-accent-main-100 
              group-hover:shadow-md group-hover:scale-110 group-hover:-rotate-3
              group-active:rotate-6 group-active:scale-[0.98]
              transition-all ease-in-out"
                >
                  <Plus
                    size={12}
                    className="text-white group-hover:scale-105 transition"
                  />
                </div>
                <span className="text-sm font-medium text-accent-main-100 tracking-tight">
                  New Chat
                </span>
              </div>
            </button>
          </div>

          {/* Conversation Lists */}
          <div className="flex flex-grow flex-col overflow-y-auto overflow-x-hidden relative px-2 mb-2">
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-8 w-8 border-2 border-accent-main-100 border-t-transparent"></div>
              </div>
            ) : (
              <>
                {/* Favorites */}
                {favoriteConversations.length > 0 && (
                  <div className="flex flex-col mb-6">
                    <h3
                      className="text-text-300 pb-2 mt-1 text-xs select-none pl-2 sticky top-0 z-10
                  bg-gradient-to-b from-bg-200 from-50% to-bg-200/40"
                    >
                      Favorites
                    </h3>
                    <ul className="flex flex-col gap-px">
                      {favoriteConversations.map((conv) => (
                        <ConversationItem
                          key={conv.conversationId}
                          conversation={conv}
                          isActive={location.pathname.includes(
                            conv.conversationId
                          )}
                          isFavorite={true}
                          onToggleFavorite={() =>
                            toggleFavorite(conv.conversationId)
                          }
                          selectedEngine={selectedEngine}
                          loadConversations={loadConversations}
                          onDelete={handleDeleteClick}
                        />
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recent */}
                <div className="flex flex-col">
                  <h3
                    className="text-text-300 pb-2 mt-1 text-xs select-none pl-2 sticky top-0 z-10
                bg-gradient-to-b from-bg-200 from-50% to-bg-200/40"
                  >
                    Recent
                  </h3>
                  <ul className="flex flex-col gap-px">
                    {recentConversations.length > 0 ? (
                      recentConversations.map((conv) => (
                        <ConversationItem
                          key={conv.conversationId}
                          conversation={conv}
                          isActive={location.pathname.includes(
                            conv.conversationId
                          )}
                          isFavorite={false}
                          onToggleFavorite={() =>
                            toggleFavorite(conv.conversationId)
                          }
                          selectedEngine={selectedEngine}
                          loadConversations={loadConversations}
                          onDelete={handleDeleteClick}
                          onToggle={onToggle}
                          isMobile={isMobile}
                        />
                      ))
                    ) : (
                      <li className="text-text-300 text-sm px-4 py-2">
                        No conversations
                      </li>
                    )}
                  </ul>
                </div>
              </>
            )}
          </div>

          {/* User Menu */}
          <div className="px-2 pb-1">
            <button
              className="flex items-center gap-3 w-full h-12 px-2 rounded-lg hover:bg-bg-300 transition-colors"
              type="button"
            >
              <div className="flex-shrink-0 flex size-8 items-center justify-center rounded-full bg-bg-400">
                <User size={16} className="text-text-300" />
              </div>
              <div className="flex flex-col items-start flex-1 min-w-0">
                <span className="text-sm font-medium text-text-100 truncate w-full text-left">
                  User
                </span>
                <span className="text-xs text-text-300 truncate w-full text-left">
                  AI Engine
                </span>
              </div>
            </button>
          </div>
        </motion.nav>
      </>
    );
  }
);

// 대화 아이템 컴포넌트
const ConversationItem = ({
  conversation,
  isActive,
  isFavorite,
  onToggleFavorite,
  selectedEngine,
  loadConversations,
  onDelete,
  onToggle,
  isMobile,
}) => {
  const [showOptions, setShowOptions] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(conversation.title || "");

  // 외부 클릭 감지
  useEffect(() => {
    const handleClickOutside = (event) => {
      // 드롭다운이 열려있고, 클릭한 요소가 드롭다운 내부가 아닌 경우
      if (
        showOptions &&
        !event.target.closest(".options-dropdown") &&
        !event.target.closest(".options-button")
      ) {
        setShowOptions(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [showOptions]);

  const handleRename = async () => {
    if (!editTitle.trim()) return;

    try {
      await updateConversationTitle(conversation.conversationId, editTitle);
      // loadConversations를 먼저 호출하여 상태를 새로고침
      await loadConversations(); // 목록 새로고침
      setIsEditing(false);
    } catch (error) {
      console.error("제목 수정 실패:", error);
      // 실패해도 편집 모드는 종료
      setIsEditing(false);
    }
  };

  if (isEditing) {
    return (
      <li className="relative px-3 py-1">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === "Enter") {
                handleRename();
              }
            }}
            className="flex-1 px-2 py-1 text-sm bg-bg-300 border border-bg-400 
              rounded text-text-100 focus:outline-none focus:border-accent-main-100"
            autoFocus
          />
          <button
            onClick={handleRename}
            className="p-1 hover:bg-bg-400 rounded"
          >
            <Check size={14} className="text-green-500" />
          </button>
          <button
            onClick={() => {
              setIsEditing(false);
              setEditTitle(conversation.title || "");
            }}
            className="p-1 hover:bg-bg-400 rounded"
          >
            <X size={14} className="text-red-500" />
          </button>
        </div>
      </li>
    );
  }

  return (
    <li className="relative group">
      <Link
        to={`/${selectedEngine.toLowerCase()}/chat/${
          conversation.conversationId
        }`}
        className={`flex items-center gap-3 h-8 px-3 rounded-md text-xs
          hover:bg-bg-400 transition-colors relative
          ${
            isActive
              ? "bg-bg-400 text-text-100"
              : "text-text-300 hover:text-text-100"
          }`}
        onClick={() => {
          console.log("🔗 스레드 클릭:", {
            conversationId: conversation.conversationId,
            targetUrl: `/${selectedEngine.toLowerCase()}/chat/${
              conversation.conversationId
            }`,
            currentUrl: window.location.pathname,
            isMobile: isMobile,
          });

          // 모바일에서는 대화 클릭 시 사이드바 자동 닫기
          if (isMobile && onToggle) {
            setTimeout(() => {
              onToggle();
            }, 100); // 약간의 딜레이를 주어 페이지 전환이 먼저 일어나도록 함
          }
        }}
      >
        {isFavorite && (
          <Star size={12} className="flex-shrink-0 fill-current" />
        )}
        <span className="truncate text-sm flex-1">
          {conversation.title || "Untitled"}
        </span>

        {/* Options button */}
        <button
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setShowOptions(!showOptions);
          }}
          className="options-button opacity-0 group-hover:opacity-100 transition-opacity
            h-6 w-6 rounded flex items-center justify-center hover:bg-bg-300"
        >
          <MoreHorizontal size={14} />
        </button>
      </Link>

      {/* Options dropdown */}
      {showOptions && (
        <div
          className="options-dropdown absolute right-0 top-8 bg-bg-100 
          rounded-lg shadow-lg z-20 py-1 min-w-[150px] border border-bg-300"
        >
          <button
            onClick={() => {
              setIsEditing(true);
              setShowOptions(false);
            }}
            className="w-full text-left px-3 py-1.5 text-sm hover:bg-bg-200 transition-colors
              flex items-center gap-2"
          >
            <Edit2 size={12} />
            Rename
          </button>
          <button
            onClick={() => {
              onToggleFavorite();
              setShowOptions(false);
            }}
            className="w-full text-left px-3 py-1.5 text-sm hover:bg-bg-200 transition-colors"
          >
            {isFavorite ? "Remove from favorites" : "Add to favorites"}
          </button>
          <button
            onClick={() => {
              onDelete(conversation.conversationId, conversation.title);
              setShowOptions(false);
            }}
            className="w-full text-left px-3 py-1.5 text-sm hover:bg-bg-200 transition-colors text-red-500"
          >
            Delete
          </button>
        </div>
      )}
    </li>
  );
};

Sidebar.displayName = "Sidebar";

export default Sidebar;
