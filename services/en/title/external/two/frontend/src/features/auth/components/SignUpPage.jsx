import React, { useState } from "react";
import clsx from "clsx";
import { Home } from "lucide-react";
import authService from "../services/authService";
import { ADMIN_EMAIL, COMPANY_DOMAIN } from "../../../config";

const SignUpPage = ({ onSignUp, onBackToLogin }) => {
  const [step, setStep] = useState("signup"); // 'signup' or 'verify'
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [verificationCode, setVerificationCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // 비밀번호 일치 확인
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    // 비밀번호 정책 확인
    const passwordRegex =
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    if (!passwordRegex.test(formData.password)) {
      setError(
        "Password must be 8+ characters with uppercase, lowercase, numbers, and special characters."
      );
      return;
    }

    // 이메일 형식 확인
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError("Please enter a valid email address.");
      return;
    }

    setIsLoading(true);

    try {
      // 회원가입 데이터 로그
      console.log("회원가입 시도:", {
        email: formData.email,
        passwordLength: formData.password.length,
      });

      // Cognito 회원가입 - 이메일을 username으로, 이름은 이메일에서 추출
      const emailName = formData.email.split("@")[0]; // 이메일에서 @ 앞부분을 이름으로 사용
      const result = await authService.signUp(
        formData.email, // username으로 이메일 사용
        formData.password,
        formData.email,
        emailName // 이메일에서 추출한 이름 사용
      );

      console.log("회원가입 결과:", result);

      if (result.success) {
        if (result.needsConfirmation) {
          // 이메일 인증이 필요한 경우
          setStep("verify");
          setSuccessMessage(
            "A verification code has been sent to your email. Please enter the code."
          );
        } else {
          // 인증이 필요 없는 경우 (자동 인증 설정 시)
          onSignUp();
        }
      } else {
        setError(result.error || "Sign up failed.");
      }
    } catch (err) {
      console.error("회원가입 오류:", err);
      setError("An error occurred during sign up.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerification = async (e) => {
    e.preventDefault();
    setError("");

    if (!verificationCode || verificationCode.length !== 6) {
      setError("Please enter a 6-digit verification code.");
      return;
    }

    setIsLoading(true);

    try {
      const result = await authService.confirmSignUp(
        formData.email,
        verificationCode
      );

      if (result.success) {
        setSuccessMessage("Email verification completed!");

        // 자동 로그인 시도
        const loginResult = await authService.signIn(
          formData.email,
          formData.password
        );

        if (loginResult.success) {
          // 로그인 성공 - LoginPage와 동일한 형식으로 저장
          const userInfo = {
            ...loginResult.user,
            selectedEngine: "11", // 기본값
          };

          // 사용자 정보 저장
          localStorage.setItem("userInfo", JSON.stringify(userInfo));
          localStorage.setItem("authToken", loginResult.tokens.accessToken); // accessToken 사용
          localStorage.setItem("idToken", loginResult.tokens.idToken);
          localStorage.setItem("refreshToken", loginResult.tokens.refreshToken);
          localStorage.setItem("isLoggedIn", "true");
          localStorage.setItem("selectedEngine", "11");

          // 사용자 역할 결정
          let userRole = "user";
          if (
            loginResult.user.email === ADMIN_EMAIL ||
            loginResult.user.email?.includes(COMPANY_DOMAIN)
          ) {
            userRole = "admin";
          }
          localStorage.setItem("userRole", userRole);

          // Header에 사용자 정보 업데이트 알림
          window.dispatchEvent(new CustomEvent("userInfoUpdated"));

          onSignUp();
        } else {
          // 로그인 페이지로 이동
          setTimeout(() => {
            onBackToLogin();
          }, 2000);
        }
      } else {
        setError(result.error || "Verification failed.");
      }
    } catch (err) {
      console.error("인증 오류:", err);
      setError("An error occurred during verification.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendCode = async () => {
    setError("");
    setSuccessMessage("");
    setIsLoading(true);

    try {
      const result = await authService.resendConfirmationCode(formData.email);

      if (result.success) {
        setSuccessMessage(result.message || "Verification code has been resent.");
      } else {
        setError(result.error || "Failed to resend verification code.");
      }
    } catch (err) {
      console.error("인증 코드 재발송 오류:", err);
      setError("An error occurred while resending the verification code.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
    setError(""); // 입력 시 에러 메시지 제거
  };

  // 회원가입 폼
  if (step === "signup") {
    return (
      <div
        className="min-h-screen flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden"
        style={{
          background: `linear-gradient(135deg, hsl(var(--bg-100)) 0%, hsl(var(--bg-200)) 50%, hsl(var(--bg-100)) 100%)`,
        }}
      >
        {/* 배경 장식 요소 */}
        <div className="absolute inset-0 overflow-hidden">
          <div
            className="absolute -top-40 -right-40 w-80 h-80 rounded-full opacity-5"
            style={{
              background: `radial-gradient(circle, hsl(var(--accent-main-000)), transparent)`,
            }}
          />
          <div
            className="absolute -bottom-40 -left-40 w-80 h-80 rounded-full opacity-5"
            style={{
              background: `radial-gradient(circle, hsl(var(--accent-main-000)), transparent)`,
            }}
          />
        </div>

        {/* 홈 버튼 - 모바일 반응형 개선 */}
        <a
          href="/"
          className="absolute top-4 sm:top-8 left-4 sm:left-8 flex items-center gap-2 px-3 sm:px-4 py-2 rounded-full backdrop-blur-sm transition-all hover:scale-105 z-10"
          style={{
            backgroundColor: "hsl(var(--bg-200)/0.8)",
            color: "hsl(var(--text-200))",
            border: "1px solid hsl(var(--bg-300)/0.3)",
          }}
        >
          <Home size={18} />
          <span className="font-medium text-sm hidden sm:inline">Home</span>
        </a>

        <div className="max-w-md w-full z-10">
          <div className="p-10 space-y-8">
            <div>
              <div className="flex flex-col items-center">
                <div className="mb-6 relative group">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full blur-lg opacity-5 group-hover:opacity-10 transition-opacity" />
                  <img
                    src="/images/logo.png"
                    alt="Logo"
                    className="w-32 h-32 object-contain relative z-10 transform transition-transform group-hover:scale-105"
                  />
                </div>
              </div>
              <h2
                className="text-center text-3xl font-extrabold tracking-tight mb-2"
                style={{
                  color: "hsl(var(--text-100))",
                  textShadow: "0 2px 4px hsl(var(--always-black)/0.1)",
                }}
              >
                TITLE-HUB
              </h2>

              <p
                className="text-center text-sm"
                style={{ color: "hsl(var(--text-400))" }}
              >
                AI-Powered Title Generation Service
              </p>
            </div>
            <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label
                    htmlFor="email"
                    className="block text-sm font-medium mb-1"
                    style={{ color: "hsl(var(--text-200))" }}
                  >
                    Email
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={formData.email}
                    onChange={(e) => handleInputChange("email", e.target.value)}
                    className="appearance-none relative block w-full px-4 py-3 rounded-lg focus:outline-none focus:z-10 text-sm transition-all duration-200"
                    style={{
                      backgroundColor: "hsl(var(--bg-100))",
                      border: "1px solid hsl(var(--bg-300))",
                      color: "hsl(var(--text-100))",
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor =
                        "hsl(var(--accent-main-100))";
                      e.target.style.boxShadow =
                        "0 0 0 3px hsl(var(--accent-main-100)/0.1)";
                      e.target.style.backgroundColor = "hsl(var(--bg-000))";
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = "hsl(var(--bg-300))";
                      e.target.style.boxShadow = "none";
                      e.target.style.backgroundColor = "hsl(var(--bg-100))";
                    }}
                    placeholder="email@example.com"
                  />
                </div>

                <div>
                  <label
                    htmlFor="password"
                    className="block text-sm font-medium mb-1"
                    style={{ color: "hsl(var(--text-200))" }}
                  >
                    Password
                  </label>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="new-password"
                    required
                    value={formData.password}
                    onChange={(e) =>
                      handleInputChange("password", e.target.value)
                    }
                    className="appearance-none relative block w-full px-4 py-3 rounded-lg focus:outline-none focus:z-10 text-sm transition-all duration-200"
                    style={{
                      backgroundColor: "hsl(var(--bg-100))",
                      border: "1px solid hsl(var(--bg-300))",
                      color: "hsl(var(--text-100))",
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor =
                        "hsl(var(--accent-main-100))";
                      e.target.style.boxShadow =
                        "0 0 0 3px hsl(var(--accent-main-100)/0.1)";
                      e.target.style.backgroundColor = "hsl(var(--bg-000))";
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = "hsl(var(--bg-300))";
                      e.target.style.boxShadow = "none";
                      e.target.style.backgroundColor = "hsl(var(--bg-100))";
                    }}
                    placeholder="Password (8+ characters)"
                  />
                  <p
                    className="mt-1 text-xs"
                    style={{ color: "hsl(var(--text-300))" }}
                  >
                    * Must include uppercase, lowercase, numbers, and special characters
                  </p>
                </div>

                <div>
                  <label
                    htmlFor="confirmPassword"
                    className="block text-sm font-medium mb-1"
                    style={{ color: "hsl(var(--text-200))" }}
                  >
                    Confirm Password
                  </label>
                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type="password"
                    autoComplete="new-password"
                    required
                    value={formData.confirmPassword}
                    onChange={(e) =>
                      handleInputChange("confirmPassword", e.target.value)
                    }
                    className="appearance-none relative block w-full px-4 py-3 rounded-lg focus:outline-none focus:z-10 text-sm transition-all duration-200"
                    style={{
                      backgroundColor: "hsl(var(--bg-100))",
                      border: "1px solid hsl(var(--bg-300))",
                      color: "hsl(var(--text-100))",
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor =
                        "hsl(var(--accent-main-100))";
                      e.target.style.boxShadow =
                        "0 0 0 3px hsl(var(--accent-main-100)/0.1)";
                      e.target.style.backgroundColor = "hsl(var(--bg-000))";
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = "hsl(var(--bg-300))";
                      e.target.style.boxShadow = "none";
                      e.target.style.backgroundColor = "hsl(var(--bg-100))";
                    }}
                    placeholder="Re-enter your password"
                  />
                </div>
              </div>

              {error && (
                <div
                  className="rounded-md p-4"
                  style={{ backgroundColor: "hsl(var(--danger-100))" }}
                >
                  <p
                    className="text-sm"
                    style={{ color: "hsl(var(--danger-000))" }}
                  >
                    {error}
                  </p>
                </div>
              )}

              {successMessage && (
                <div
                  className="rounded-md p-4"
                  style={{ backgroundColor: "hsl(var(--success-100))" }}
                >
                  <p
                    className="text-sm"
                    style={{ color: "hsl(var(--success-000))" }}
                  >
                    {successMessage}
                  </p>
                </div>
              )}

              <div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className={clsx(
                    "group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white focus:outline-none focus:ring-2 focus:ring-offset-2",
                    isLoading ? "opacity-50 cursor-not-allowed" : ""
                  )}
                  style={{
                    backgroundColor: "hsl(var(--accent-main-000))",
                  }}
                >
                  {isLoading ? "Processing..." : "Sign up"}
                </button>
              </div>

              <div className="text-center">
                <button
                  type="button"
                  onClick={onBackToLogin}
                  className="text-sm hover:underline"
                  style={{ color: "hsl(var(--text-300))" }}
                >
                  Already have an account? Login
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }

  // 이메일 인증 폼
  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden"
      style={{
        background: `linear-gradient(135deg, hsl(var(--bg-100)) 0%, hsl(var(--bg-200)) 50%, hsl(var(--bg-100)) 100%)`,
      }}
    >
      {/* 배경 장식 요소 */}
      <div className="absolute inset-0 overflow-hidden">
        <div
          className="absolute -top-40 -right-40 w-80 h-80 rounded-full opacity-5"
          style={{
            background: `radial-gradient(circle, hsl(var(--accent-main-000)), transparent)`,
          }}
        />
        <div
          className="absolute -bottom-40 -left-40 w-80 h-80 rounded-full opacity-5"
          style={{
            background: `radial-gradient(circle, hsl(var(--accent-main-000)), transparent)`,
          }}
        />
      </div>

      {/* 홈 버튼 - 모바일 반응형 개선 */}
      <a
        href="/"
        className="absolute top-4 sm:top-8 left-4 sm:left-8 flex items-center gap-2 px-3 sm:px-4 py-2 rounded-full backdrop-blur-sm transition-all hover:scale-105 z-10"
        style={{
          backgroundColor: "hsl(var(--bg-200)/0.8)",
          color: "hsl(var(--text-200))",
          border: "1px solid hsl(var(--bg-300)/0.3)",
        }}
      >
        <Home size={18} />
        <span className="font-medium text-sm hidden sm:inline">Home</span>
      </a>

      <div className="max-w-md w-full z-10">
        <div className="p-10 space-y-8">
          <div>
            <div className="flex flex-col items-center mb-6">
              <div className="mb-4 relative group">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full blur-lg opacity-5 group-hover:opacity-10 transition-opacity" />
                <img
                  src="/images/logo.png"
                  alt="Logo"
                  className="w-28 h-28 object-contain relative z-10 transform transition-transform group-hover:scale-105"
                />
              </div>
            </div>
            <h2
              className="text-center text-2xl font-extrabold tracking-tight mb-2"
              style={{
                color: "hsl(var(--text-100))",
                textShadow: "0 2px 4px hsl(var(--always-black)/0.1)",
              }}
            >
              Email Verification
            </h2>
            <p
              className="text-center text-sm"
              style={{ color: "hsl(var(--text-300))" }}
            >
              Please enter the 6-digit code sent to {formData.email}
            </p>
          </div>
          <form className="mt-8 space-y-6" onSubmit={handleVerification}>
            <div>
              <label
                htmlFor="code"
                className="block text-sm font-medium mb-1"
                style={{ color: "hsl(var(--text-200))" }}
              >
                Verification Code
              </label>
              <input
                id="code"
                name="code"
                type="text"
                maxLength="6"
                required
                value={verificationCode}
                onChange={(e) =>
                  setVerificationCode(e.target.value.replace(/[^0-9]/g, ""))
                }
                className="appearance-none relative block w-full px-4 py-3 text-center text-2xl tracking-widest rounded-lg focus:outline-none focus:z-10 transition-all duration-200"
                style={{
                  backgroundColor: "hsl(var(--bg-100))",
                  border: "1px solid hsl(var(--bg-300))",
                  color: "hsl(var(--text-100))",
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = "hsl(var(--accent-main-100))";
                  e.target.style.boxShadow =
                    "0 0 0 3px hsl(var(--accent-main-100)/0.1)";
                  e.target.style.backgroundColor = "hsl(var(--bg-000))";
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = "hsl(var(--bg-300))";
                  e.target.style.boxShadow = "none";
                  e.target.style.backgroundColor = "hsl(var(--bg-100))";
                }}
                placeholder="000000"
              />
            </div>

            {error && (
              <div
                className="rounded-md p-4"
                style={{ backgroundColor: "hsl(var(--danger-100))" }}
              >
                <p
                  className="text-sm"
                  style={{ color: "hsl(var(--danger-000))" }}
                >
                  {error}
                </p>
              </div>
            )}

            {successMessage && (
              <div
                className="rounded-md p-4"
                style={{ backgroundColor: "hsl(var(--success-100))" }}
              >
                <p
                  className="text-sm"
                  style={{ color: "hsl(var(--success-000))" }}
                >
                  {successMessage}
                </p>
              </div>
            )}

            <div className="space-y-3">
              <button
                type="submit"
                disabled={isLoading}
                className={clsx(
                  "group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white focus:outline-none focus:ring-2 focus:ring-offset-2",
                  isLoading ? "opacity-50 cursor-not-allowed" : ""
                )}
                style={{
                  backgroundColor: "hsl(var(--accent-main-000))",
                }}
              >
                {isLoading ? "Verifying..." : "Verify"}
              </button>

              <button
                type="button"
                onClick={handleResendCode}
                disabled={isLoading}
                className="w-full text-sm hover:underline"
                style={{ color: "hsl(var(--text-300))" }}
              >
                Resend verification code
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SignUpPage;
