// WebSocket 서비스
class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
    this.messageHandlers = new Set();
    this.connectionHandlers = new Set();
    this.isConnecting = false;
    this.messageQueue = [];
    this.isReconnecting = false;
    this.conversationHistory = [];
    this.currentConversationId = null;
  }

  // WebSocket 연결
  async connect() {
    // 개발 환경에서는 모의 WebSocket 사용
    if (import.meta.env.DEV) {
      console.log("🔧 개발 모드: 모의 WebSocket 연결");
      this.isConnecting = false;
      this.ws = { readyState: WebSocket.OPEN }; // 모의 연결 상태
      this.connectionHandlers.forEach((handler) => handler(true));
      return Promise.resolve();
    }

    if (
      this.isConnecting ||
      (this.ws && this.ws.readyState === WebSocket.OPEN)
    ) {
      console.log("이미 연결되어 있거나 연결 중입니다.");
      return Promise.resolve();
    }

    this.isConnecting = true;

    return new Promise(async (resolve, reject) => {
      try {
        // JWT 토큰 가져오기
        const authService = (await import("../../auth/services/authService")).default;
        const token = await authService.getAuthToken();

        // config.js에서 WS_URL import
        const { WS_URL } = await import('../../../config');
        let wsUrl = WS_URL;

        // 토큰이 있으면 쿼리 파라미터로 추가
        if (token) {
          wsUrl += `?token=${encodeURIComponent(token)}`;
        }

        console.log("WebSocket 연결 시도:", wsUrl.split("?")[0]);

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log("WebSocket 연결 성공");
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.isReconnecting = false;
          this.connectionHandlers.forEach((handler) => handler(true));
          this.processMessageQueue();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log("WebSocket 메시지 수신:", data);
            this.messageHandlers.forEach((handler) => {
              try {
                handler(data);
              } catch (error) {
                console.error("메시지 핸들러 오류:", error);
              }
            });
          } catch (error) {
            console.error("메시지 파싱 오류:", error, event.data);
          }
        };

        this.ws.onerror = (error) => {
          console.error("WebSocket 오류:", error);
          this.isConnecting = false;
        };

        this.ws.onclose = (event) => {
          console.log("WebSocket 연결 종료:", event.code, event.reason);
          this.isConnecting = false;
          this.connectionHandlers.forEach((handler) => handler(false));
          if (event.code !== 1000 && event.code !== 1001) {
            this.handleReconnect();
          }
        };

        setTimeout(() => {
          if (this.isConnecting) {
            console.error("WebSocket 연결 타임아웃");
            this.isConnecting = false;
            this.ws?.close();
            reject(new Error("Connection timeout"));
          }
        }, 30000);
      } catch (error) {
        console.error("WebSocket 연결 실패:", error);
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  handleReconnect() {
    if (this.isReconnecting || this.reconnectAttempts >= this.maxReconnectAttempts) {
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error("최대 재연결 시도 횟수 초과");
      }
      return;
    }
    this.isReconnecting = true;
    this.reconnectAttempts++;
    console.log(`재연결 시도 ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
    setTimeout(() => {
      this.connect().then(() => {
        console.log("재연결 성공");
        this.isReconnecting = false;
      }).catch(() => {
        console.error("재연결 실패");
        this.isReconnecting = false;
        this.handleReconnect();
      });
    }, this.reconnectDelay);
  }

  sendMessage(message, engineType = "11", conversationId = null, conversationHistory = null, idempotencyKey = null, selectedModel = 'claude-opus-4-5-20251101') {
    return new Promise((resolve, reject) => {
      console.log("🔧 REST API 모드: 모의 AI 응답 생성");
      this.simulateAIResponse(message, engineType, selectedModel);
      resolve();
    });
  }

  processMessageQueue() {
    while (this.messageQueue.length > 0) {
      const { message, engineType, conversationId, resolve, reject } = this.messageQueue.shift();
      this.sendMessage(message, engineType, conversationId).then(resolve).catch(reject);
    }
  }

  addMessageHandler(handler) {
    this.messageHandlers.add(handler);
  }

  removeMessageHandler(handler) {
    this.messageHandlers.delete(handler);
  }

  addConnectionHandler(handler) {
    this.connectionHandlers.add(handler);
  }

  removeConnectionHandler(handler) {
    this.connectionHandlers.delete(handler);
  }

  async simulateAIResponse(message, engineType, selectedModel = 'claude-opus-4-5-20251101') {
    const useMockAPI = import.meta.env.VITE_USE_MOCK_API !== 'false';
    const hasClaudeKey = import.meta.env.VITE_CLAUDE_API_KEY && import.meta.env.VITE_CLAUDE_API_KEY !== 'your_claude_api_key_here';

    if (!useMockAPI && hasClaudeKey) {
      await this.callClaudeAPI(message, engineType, selectedModel);
    } else {
      this.generateMockResponse(message, engineType, selectedModel);
    }
  }

  async callClaudeAPI(message, engineType, selectedModel) {
    try {
      const { default: claudeService } = await import('./claudeService.js');
      this.messageHandlers.forEach((handler) => {
        handler({ type: "ai_start", timestamp: new Date().toISOString() });
      });

      const systemPrompts = {
        "11": "당신은 기업 보도자료 전문 분석가입니다.",
        "22": "당신은 정부/공공기관 보도자료 전문 분석가입니다."
      };

      const systemPrompt = systemPrompts[engineType] || systemPrompts["11"];
      const fullMessage = `${systemPrompt}\n\n분석할 내용:\n${message}`;

      await claudeService.streamChat(fullMessage, selectedModel,
        (chunk, chunkIndex) => {
          this.messageHandlers.forEach((handler) => {
            handler({ type: "ai_chunk", chunk: chunk, chunk_index: chunkIndex });
          });
        },
        (totalChunks) => {
          this.messageHandlers.forEach((handler) => {
            handler({ type: "chat_end", total_chunks: totalChunks, engine: engineType });
          });
        },
        (error) => {
          console.error('Claude API 오류:', error);
          this.messageHandlers.forEach((handler) => {
            handler({ type: "error", message: `Claude API 오류: ${error.message}` });
          });
        }
      );
    } catch (error) {
      console.error('Claude API 호출 실패:', error);
      this.generateMockResponse(message, engineType, selectedModel);
    }
  }

  generateMockResponse(message, engineType, selectedModel = 'claude-opus-4-5-20251101') {
    setTimeout(() => {
      this.messageHandlers.forEach((handler) => {
        handler({ type: "ai_start", timestamp: new Date().toISOString() });
      });
    }, 500);

    let userTextOnly = message;
    const fileStartIndex = message.indexOf("\n\n--- 파일:");
    if (fileStartIndex !== -1) {
      userTextOnly = message.substring(0, fileStartIndex).trim();
    }
    if (!userTextOnly) {
      userTextOnly = "파일을 업로드해주셨네요";
    }

    const mockResponses = {
      "11": `안녕하세요! 기업 보도자료 분석 엔진입니다.\n\n입력하신 내용: "${userTextOnly}"\n\n현재 사용 중인 모델: **${selectedModel}**\n\n🔧 **개발 모드 안내**\n현재 모의 응답을 사용 중입니다.`,
      "22": `안녕하세요! 정부/공공기관 보도자료 분석 엔진입니다.\n\n입력하신 내용: "${userTextOnly}"\n\n현재 사용 중인 모델: **${selectedModel}**\n\n🔧 **개발 모드 안내**\n현재 모의 응답을 사용 중입니다.`
    };

    const responseText = mockResponses[engineType] || mockResponses["11"];
    const chunks = responseText.split(' ');
    
    chunks.forEach((chunk, index) => {
      setTimeout(() => {
        this.messageHandlers.forEach((handler) => {
          handler({ type: "ai_chunk", chunk: chunk + ' ', chunk_index: index });
        });
      }, 1000 + (index * 100));
    });

    setTimeout(() => {
      this.messageHandlers.forEach((handler) => {
        handler({ type: "chat_end", total_chunks: chunks.length, engine: engineType });
      });
    }, 1000 + (chunks.length * 100) + 500);
  }

  isWebSocketConnected() {
    if (import.meta.env.DEV) {
      return true;
    }
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }

  disconnect() {
    if (this.ws) {
      console.log("WebSocket 연결 종료 요청");
      this.ws.close(1000, "Normal closure");
      this.ws = null;
    }
    this.messageHandlers.clear();
    this.connectionHandlers.clear();
    this.messageQueue = [];
    this.conversationHistory = [];
    this.currentConversationId = null;
  }
}

const webSocketService = new WebSocketService();

export const connectWebSocket = () => webSocketService.connect();
export const disconnectWebSocket = () => webSocketService.disconnect();
export const sendChatMessage = (message, engineType, conversationHistory, conversationId, idempotencyKey, selectedModel) =>
  webSocketService.sendMessage(message, engineType, conversationId, conversationHistory, idempotencyKey, selectedModel);
export const isWebSocketConnected = () => webSocketService.isWebSocketConnected();
export const addMessageHandler = (handler) => webSocketService.addMessageHandler(handler);
export const removeMessageHandler = (handler) => webSocketService.removeMessageHandler(handler);
export const addConnectionHandler = (handler) => webSocketService.addConnectionHandler(handler);
export const removeConnectionHandler = (handler) => webSocketService.removeConnectionHandler(handler);

export default webSocketService;
