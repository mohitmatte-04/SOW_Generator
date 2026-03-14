"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { AlertCircle } from "lucide-react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="text-center space-y-6 max-w-md mx-auto p-8">
        <div className="p-4 bg-red-100 rounded-full w-fit mx-auto">
          <AlertCircle className="h-16 w-16 text-red-600" />
        </div>
        <div>
          <h2 className="text-2xl font-bold mb-2">Something went wrong!</h2>
          <p className="text-muted-foreground">
            An error occurred while loading the application.
          </p>
        </div>
        <Button onClick={() => reset()} size="lg">
          Try again
        </Button>
      </div>
    </div>
  );
}
