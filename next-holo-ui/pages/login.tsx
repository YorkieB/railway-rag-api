import { useEffect } from "react";
import { useRouter } from "next/router";

export default function Login() {
  const router = useRouter();
  
  useEffect(() => {
    // Multiple redirect methods to ensure it works
    if (typeof window !== "undefined") {
      // Try router first (client-side, faster)
      router.replace("/");
      // Fallback to window.location (more reliable)
      setTimeout(() => {
        if (window.location.pathname === "/login") {
          window.location.replace("/");
        }
      }, 100);
    }
  }, [router]);

  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh", fontFamily: "system-ui" }}>
      <div style={{ textAlign: "center" }}>
        <p style={{ fontSize: "18px", marginBottom: "10px" }}>Redirecting to home page...</p>
        <p style={{ fontSize: "14px", color: "#666" }}>If you're not redirected, <a href="/" style={{ color: "#0066cc" }}>click here</a>.</p>
      </div>
    </div>
  );
}

