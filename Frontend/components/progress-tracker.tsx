"use client";

import { Progress } from "@/components/ui/progress";
import {
  Upload,
  FileText,
  Sparkles,
  CheckCircle,
  Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";

export type GenerationStage =
  | "idle"
  | "uploading"
  | "extracting"
  | "generating"
  | "complete";

interface ProgressTrackerProps {
  currentStage: GenerationStage;
  progress: number;
  message?: string;
}

const stages = [
  {
    id: "uploading" as const,
    label: "Uploading Proposal",
    icon: Upload,
  },
  {
    id: "extracting" as const,
    label: "Extracting Details",
    icon: FileText,
  },
  {
    id: "generating" as const,
    label: "Generating SOW",
    icon: Sparkles,
  },
  {
    id: "complete" as const,
    label: "Complete",
    icon: CheckCircle,
  },
];

export function ProgressTracker({
  currentStage,
  progress,
  message,
}: ProgressTrackerProps) {
  if (currentStage === "idle") return null;

  const getCurrentStageIndex = () => {
    return stages.findIndex((stage) => stage.id === currentStage);
  };

  const currentIndex = getCurrentStageIndex();

  return (
    <div className="w-full max-w-2xl mx-auto p-6 space-y-6 animate-fade-in">
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="font-medium">
            {stages[currentIndex]?.label || "Processing..."}
          </span>
          <span className="text-muted-foreground">{progress}%</span>
        </div>
        {message && (
          <p className="text-sm text-muted-foreground animate-fade-in">
            {message}
          </p>
        )}
        <Progress value={progress} className="h-2" />
      </div>

      <div className="grid grid-cols-4 gap-4">
        {stages.map((stage, index) => {
          const Icon = stage.icon;
          const isActive = index === currentIndex;
          const isCompleted = index < currentIndex;
          const isPending = index > currentIndex;

          return (
            <div
              key={stage.id}
              className={cn(
                "flex flex-col items-center gap-2 transition-all duration-300",
                isActive && "scale-110"
              )}
            >
              <div
                className={cn(
                  "w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300",
                  isCompleted && "bg-green-500 text-white",
                  isActive && "bg-primary text-primary-foreground animate-pulse",
                  isPending && "bg-muted text-muted-foreground"
                )}
              >
                {isActive && currentStage !== "complete" ? (
                  <Loader2 className="h-6 w-6 animate-spin" />
                ) : (
                  <Icon className="h-6 w-6" />
                )}
              </div>
              <p
                className={cn(
                  "text-xs text-center font-medium transition-colors",
                  isActive && "text-primary",
                  isCompleted && "text-green-600",
                  isPending && "text-muted-foreground"
                )}
              >
                {stage.label}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
