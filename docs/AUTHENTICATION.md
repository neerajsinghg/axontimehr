# Phase 2 — Authentication Architecture & Security Documentation

## 1. System Overview

AxonTime HR employs a **production-ready, dual-token JWT authentication engine** with support for both **Email + Password** and **Mobile Number + 6-digit OTP** authentication flows.

The architecture is strictly separated into **Authentication** (Phase 2 — *Who are you?*) and **Authorization / RBAC** (Phase 3 — *What are you allowed to do?*).

---

## 2. Conceptual Architecture

```text
                             React Frontend SPA
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
           Email & Password                      Mobile & OTP
                    │                                 │
                    ▼                                 ▼
         POST /auth/login                    POST /auth/otp/verify
                    │                                 │
                    └────────────────┬────────────────┘
                                     ▼
                          FastAPI Auth Controller
                                     │
                     ┌───────────────┴───────────────┐
                     │                               │
            Password Verifier /                 Mobile OTP
            Argon2 & Bcrypt Hash                Verifier
                     │                               │
                     └───────────────┬───────────────┘
                                     ▼
                        JWT Dual Token Generator
                                     │
                     ┌───────────────┴───────────────┐
                     │                               │
             JWT Access Token              JWT Refresh Token
            (30 Min Lifetime)             (7 Day Lifetime + JTI)
                     │                               │
                     ▼                               ▼
            Bearer Auth Header               DB / Redis AuthSession
            (Stateless Requests)             (Rotation & Revocation)
```

---

## 3. Security Features & Policies

### 3.1 Password Security & Storage
- Passwords are **never stored as plaintext** or logged.
- Password hashing utilizes `passlib` with **Argon2id** (`m=65536, t=3, p=4`) and **Bcrypt** schemes.

### 3.2 Token Architecture & Mandatory Rotation
- **Access Tokens**: Short-lived (30 minutes) containing minimal claims (`sub`, `type: "access"`, `iat`, `exp`, `jti`).
- **Refresh Tokens**: Long-lived (7 days) containing `jti` (JWT ID claim).
- **Token Rotation**: Each call to `POST /api/v1/auth/refresh` revokes the old `AuthSession` and issues a fresh Access/Refresh pair.
- **Revocation Protection**: Reusing a previously revoked refresh token invalidates all active sessions for that user family to protect against token theft.

### 3.3 Account Lockout Protection
- Tracks `failed_login_attempts` per user.
- Upon 5 consecutive failed password attempts, sets `is_locked = True` and locks the account for **15 minutes**.

### 3.4 Email & SMS Service Abstraction
- Abstract `BaseEmailService` and `BaseSMSService` interfaces.
- Local development logs email tokens and SMS OTP codes cleanly via `ConsoleEmailService` and `ConsoleSMSService` without requiring paid credentials.

---

## 4. API Endpoints Reference (`/api/v1/auth/`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register new user account |
| `POST` | `/api/v1/auth/login` | Authenticate with Email & Password |
| `POST` | `/api/v1/auth/otp/send` | Dispatch 6-digit OTP code to mobile number |
| `POST` | `/api/v1/auth/otp/verify` | Verify OTP & issue authentication tokens |
| `POST` | `/api/v1/auth/refresh` | Rotate refresh token & issue new access token |
| `POST` | `/api/v1/auth/logout` | Revoke session refresh token |
| `GET`  | `/api/v1/auth/me` | Fetch current authenticated user profile |
| `POST` | `/api/v1/auth/change-password` | Change authenticated user password |
| `POST` | `/api/v1/auth/forgot-password` | Request password reset token |
| `POST` | `/api/v1/auth/reset-password` | Reset password using valid reset token |
| `POST` | `/api/v1/auth/verify-email` | Verify user email address |
| `POST` | `/api/v1/auth/resend-verification` | Resend email verification token |

---

## 5. Frontend Integration Architecture

- **`AuthContext` & `useAuth()`**: React Context maintaining `user`, `isAuthenticated`, `isLoading`, `login`, `loginWithOTP`, and `logout`.
- **Axios Refresh Queue Interceptor (`client.ts`)**: Automatically catches `401 Unauthorized` responses, executes a single refresh token rotation, queues pending API requests, and retries them seamlessly.
- **`ProtectedRoute` Component**: Prevents unauthenticated users from opening protected dashboard routes.
