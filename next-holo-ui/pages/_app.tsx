import type { AppProps } from "next/app";
import "@/styles/globals.css";
import { AuthProvider } from "@/lib/auth";

function App(props: AppProps) {
  return (
    <AuthProvider>
      <props.Component {...props.pageProps} />
    </AuthProvider>
  );
}

export default App;

