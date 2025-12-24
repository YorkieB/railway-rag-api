import Script from "next/script";

export default function Login() {
  return (
    <>
      <Script id="redirect-login" strategy="beforeInteractive">
        {`if (typeof window !== 'undefined') { window.location.replace('/'); }`}
      </Script>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh", fontFamily: "system-ui" }}>
        <div style={{ textAlign: "center" }}>
          <p style={{ fontSize: "18px", marginBottom: "10px" }}>Redirecting to home page...</p>
          <p style={{ fontSize: "14px", color: "#666" }}>If you're not redirected, <a href="/" style={{ color: "#0066cc" }}>click here</a>.</p>
        </div>
      </div>
      <script dangerouslySetInnerHTML={{ __html: `window.location.replace('/');` }} />
    </>
  );
}
