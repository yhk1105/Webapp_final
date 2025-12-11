import { useState } from "react";
import { login, register, AuthResponse } from "../api";

interface AuthProps {
  onLogin: (authData: AuthResponse) => void;
}

export function Auth({ onLogin }: AuthProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isLogin) {
        const authData = await login({ username, password });
        onLogin(authData);
      } else {
        await register({ username, password });
        // 註冊成功後自動登入
        const authData = await login({ username, password });
        onLogin(authData);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "操作失敗");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h2>{isLogin ? "登入" : "註冊"}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>用戶名</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label>密碼</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          {error && <div className="error">{error}</div>}
          <button type="submit" disabled={loading}>
            {loading ? "處理中..." : isLogin ? "登入" : "註冊"}
          </button>
        </form>
        <p className="auth-switch">
          {isLogin ? "還沒有帳號？" : "已有帳號？"}{" "}
          <button
            type="button"
            className="link-button"
            onClick={() => {
              setIsLogin(!isLogin);
              setError(null);
            }}
          >
            {isLogin ? "註冊" : "登入"}
          </button>
        </p>
      </div>
    </div>
  );
}




