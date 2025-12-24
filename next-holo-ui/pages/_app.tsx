import type { AppProps } from "next/app";
import "@/styles/globals.css";

function App(props: AppProps) {
  return <props.Component {...props.pageProps} />;
}

export default App;

