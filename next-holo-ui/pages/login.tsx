import { useEffect } from "react";
import { useRouter } from "next/router";

export default function Login() {
  const router = useRouter();
  
  useEffect(() => {
    // Redirect to home page immediately
    router.replace("/");
  }, [router]);

  return null;
}

