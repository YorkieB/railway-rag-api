import { useEffect } from "react";

export default function Login() {
  useEffect(() => {
    // Redirect to home page immediately using window.location for immediate effect
    if (typeof window !== "undefined") {
      window.location.replace("/");
    }
  }, []);

  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh" }}>
      <p>Redirecting to home page...</p>
    </div>
  );
}

