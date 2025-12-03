from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import database

# 密碼加密設定
# 直接使用 bcrypt 庫，避免 passlib 的檢測問題
try:
    import bcrypt
    USE_DIRECT_BCRYPT = True
    pwd_context = None  # 不需要 passlib
except ImportError:
    USE_DIRECT_BCRYPT = False
    # 如果 bcrypt 不可用，使用 passlib
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 設定
SECRET_KEY = "your-secret-key-change-this-in-production"  # 生產環境應該使用環境變數
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 天

# HTTPBearer 配置，確保正確處理 Authorization header
security = HTTPBearer(
    scheme_name="Bearer",
    auto_error=True  # 如果沒有 token，自動返回 401
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證密碼"""
    if USE_DIRECT_BCRYPT:
        # 直接使用 bcrypt，避免 passlib 的檢測問題
        password_bytes = plain_password.encode('utf-8')
        # 確保密碼不超過 72 bytes
        password_to_check = password_bytes[:72] if len(
            password_bytes) > 72 else password_bytes
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_to_check, hashed_bytes)
    else:
        # 使用 passlib
        return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密碼雜湊"""
    # 確保密碼是字符串且長度合理
    if not isinstance(password, str):
        raise ValueError("密碼必須是字符串")

    if len(password) < 1:
        raise ValueError("密碼不能為空")

    # bcrypt 限制密碼長度為 72 bytes
    # 檢查 UTF-8 編碼後的長度
    password_bytes = password.encode('utf-8')
    password_byte_length = len(password_bytes)

    if password_byte_length > 72:
        raise ValueError(
            f"密碼長度不能超過 72 bytes（當前為 {password_byte_length} bytes，約 {len(password)} 個字符）")

    # 根據配置選擇使用 bcrypt 或 passlib
    if USE_DIRECT_BCRYPT:
        # 直接使用 bcrypt，避免 passlib 的檢測問題
        password_to_hash = password_bytes[:72] if password_byte_length > 72 else password_bytes
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_to_hash, salt)
        # bcrypt.hashpw 返回 bytes，解碼為字符串
        return hashed.decode('utf-8')
    else:
        # 使用 passlib
        try:
            return pwd_context.hash(password)
        except Exception as e:
            error_msg = str(e)
            raise ValueError(f"密碼加密失敗: {error_msg}")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """創建 JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + \
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """驗證 JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        # 記錄詳細錯誤信息以便調試
        print(f"JWT 驗證失敗: {str(e)}")
        print(f"Token 前 20 個字符: {token[:20] if token else 'None'}...")
        return None
    except Exception as e:
        print(f"Token 驗證時發生未知錯誤: {str(e)}")
        return None


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """從 token 獲取當前用戶（必需認證）"""
    try:
        token = credentials.credentials
        if not token:
            print("認證錯誤: 沒有提供 token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="缺少認證憑證",
                headers={"WWW-Authenticate": "Bearer"},
            )

        print(f"收到 token，長度: {len(token)}")
        payload = verify_token(token)
        if payload is None:
            print("認證錯誤: token 驗證失敗")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無效的認證憑證",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id_str = payload.get("sub")
        if user_id_str is None:
            print(f"認證錯誤: payload 中沒有 'sub' 欄位，payload: {payload}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無效的認證憑證",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # sub 是字符串，需要轉換為整數
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            print(f"認證錯誤: 'sub' 欄位無法轉換為整數: {user_id_str}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無效的認證憑證",
                headers={"WWW-Authenticate": "Bearer"},
            )
        print(f"認證成功，user_id: {user_id}")
        return {"user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        # 記錄其他錯誤
        print(f"認證錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"認證失敗: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[dict]:
    """從 token 獲取當前用戶（可選認證）"""
    if credentials is None:
        return None
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        return None
    user_id: int = payload.get("sub")
    if user_id is None:
        return None
    return {"user_id": user_id}


def get_user_by_username(username: str) -> Optional[dict]:
    """根據用戶名獲取用戶"""
    import sqlite3
    conn = sqlite3.connect(database.DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute(
        'SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()

    if row:
        return {"id": row["id"], "username": row["username"], "password_hash": row["password_hash"]}
    return None


def create_user(username: str, password: str) -> dict:
    """創建新用戶"""
    import sqlite3

    # 驗證用戶名
    if not username or len(username.strip()) == 0:
        raise ValueError("用戶名不能為空")

    if len(username) > 50:
        raise ValueError("用戶名長度不能超過 50 個字符")

    # 驗證密碼
    if not password or len(password.strip()) == 0:
        raise ValueError("密碼不能為空")

    # 檢查密碼長度（以 bytes 計算）
    password_bytes = password.encode('utf-8')
    password_byte_length = len(password_bytes)

    if password_byte_length > 72:
        raise ValueError(
            f"密碼長度不能超過 72 bytes（當前為 {password_byte_length} bytes，"
            f"字符數: {len(password)}）。請使用較短的密碼。"
        )

    conn = sqlite3.connect(database.DB_NAME)
    c = conn.cursor()

    try:
        password_hash = get_password_hash(password)
        c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                  (username.strip(), password_hash))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return {"id": user_id, "username": username.strip()}
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError("用戶名已存在")
    except ValueError:
        # 重新拋出 ValueError（包括密碼長度錯誤）
        conn.close()
        raise
    except Exception as e:
        conn.close()
        # 其他錯誤，可能是 bcrypt 的問題
        error_msg = str(e)
        raise ValueError(f"創建用戶失敗: {error_msg}")
