"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { GoogleDriveInput } from "@/components/google-drive-input";
import { ProgressTracker, GenerationStage } from "@/components/progress-tracker";
import { useToast } from "@/components/ui/use-toast";
import { generateSOW, getSOWProgress } from "@/lib/api";
import {
  FileText,
  Sparkles,
  ArrowRight,
  Download,
  CheckCircle2,
} from "lucide-react";

const formSchema = z.object({
  proposalFolderUrl: z
    .string()
    .min(1, "Please enter a URL or GCS path")
    .refine(
      (url) => {
        // Accept GCS URIs (gs://bucket/path)
        if (url.startsWith("gs://")) return true;
        // Accept Google Drive URLs
        if (url.includes("drive.google.com") || url.includes("docs.google.com")) return true;
        return false;
      },
      "Please enter a valid Google Drive URL or GCS URI (gs://...)"
    ),
});

type FormData = z.infer<typeof formSchema>;

export default function Home() {
  const [currentStage, setCurrentStage] = useState<GenerationStage>("idle");
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState<string>("");
  const [generatedSowUrl, setGeneratedSowUrl] = useState<string | null>(null);
  const { toast } = useToast();

  const {
    watch,
    setValue,
    formState: { errors },
    handleSubmit,
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      proposalFolderUrl: "",
    },
  });

  const proposalUrl = watch("proposalFolderUrl");

  const onSubmit = async (data: FormData) => {
    try {
      console.log("================================================================================");
      console.log("🚀 Starting SOW Generation");
      console.log("================================================================================");
      console.log("📥 Input:", data.proposalFolderUrl);
      console.log("================================================================================");

      // Start SOW generation
      const response = await generateSOW({
        proposal_file_url: data.proposalFolderUrl,
      });

      if (!response.session_id) {
        throw new Error(response.message || "Failed to start SOW generation");
      }

      const sessionId = response.session_id;
      console.log("✅ Session Created:", sessionId);

      // Immediately fetch the first progress update (don't wait 1 second)
      const updateProgress = async () => {
        const progressData = await getSOWProgress(sessionId);

        // Update UI based on progress
        setCurrentStage(progressData.stage as GenerationStage);
        setProgress(progressData.progress);
        setProgressMessage(progressData.message || "");

        // Check if complete or error
        if (progressData.stage === "complete") {
          if (progressData.sow_url) {
            setGeneratedSowUrl(progressData.sow_url);

            // Log the GCS location to console
            console.log("================================================================================");
            console.log("✅ SOW GENERATION COMPLETE!");
            console.log("================================================================================");
            console.log("📍 Saved Location:", progressData.sow_url);
            console.log("Session ID:", progressData.session_id);
            console.log("================================================================================");
          }
          toast({
            title: "Success!",
            description: "Your Statement of Work has been generated successfully.",
          });
          return true; // Signal completion
        } else if (progressData.stage === "error") {
          throw new Error(progressData.error || "Generation failed");
        }
        return false; // Not done yet
      };

      // Fetch immediately
      const isDone = await updateProgress();
      if (isDone) return;

      // Then poll every 1 second for faster updates
      const pollInterval = setInterval(async () => {
        try {
          const isDone = await updateProgress();
          if (isDone) {
            clearInterval(pollInterval);
          }
        } catch (pollError) {
          clearInterval(pollInterval);
          throw pollError;
        }
      }, 1000); // Poll every 1 second (faster than before)

    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to generate SOW. Please try again.",
        variant: "destructive",
      });
      setCurrentStage("idle");
      setProgress(0);
      setProgressMessage("");
    }
  };

  const handleReset = () => {
    setCurrentStage("idle");
    setProgress(0);
    setProgressMessage("");
    setGeneratedSowUrl(null);
    setValue("proposalFolderUrl", "");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-red-400/10 to-orange-400/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-red-300/10 to-pink-400/10 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 container mx-auto px-4 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-gradient-to-br from-primary to-red-600 rounded-2xl shadow-lg">
              <FileText className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-red-600">
              SOW Generator
            </h1>
          </div>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Transform your proposals into professional Statement of Work documents,
            powered by advanced AI technology
          </p>
        </motion.div>

        {/* Main Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="max-w-4xl mx-auto"
        >
          <Card className="border-0 shadow-2xl backdrop-blur-sm bg-white/80">
            <CardHeader className="space-y-3 pb-8">
              <CardTitle className="text-3xl flex items-center gap-2">
                <Sparkles className="h-7 w-7 text-primary" />
                Generate Your SOW
              </CardTitle>
              <CardDescription className="text-base">
                Provide your proposal link to get started. We&apos;ll deliver a
                comprehensive Statement of Work document tailored to your needs.
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-8">
              {currentStage === "idle" && (
                <motion.form
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.4 }}
                  onSubmit={handleSubmit(onSubmit)}
                  className="space-y-6"
                >
                  <GoogleDriveInput
                    label="Proposal File URL or GCS Path"
                    placeholder="https://drive.google.com/file/d/... or gs://bucket/file.pptx"
                    value={proposalUrl}
                    onChange={(value) => setValue("proposalFolderUrl", value)}
                    error={errors.proposalFolderUrl?.message}
                    description="Paste a Google Drive link or GCS URI to your proposal file (PPTX format)"
                  />

                  <Button
                    type="submit"
                    size="lg"
                    className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-primary to-red-600 hover:from-red-600 hover:to-red-700 shadow-lg hover:shadow-xl transition-all duration-300"
                  >
                    <Sparkles className="mr-2 h-5 w-5" />
                    Generate Statement of Work
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </motion.form>
              )}

              {currentStage !== "idle" && currentStage !== "complete" && (
                <ProgressTracker
                  currentStage={currentStage}
                  progress={progress}
                  message={progressMessage}
                />
              )}

              {currentStage === "complete" && generatedSowUrl && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5 }}
                  className="space-y-6"
                >
                  <div className="flex flex-col items-center justify-center py-8 space-y-4">
                    <div className="p-4 bg-green-100 rounded-full">
                      <CheckCircle2 className="h-16 w-16 text-green-600" />
                    </div>
                    <h3 className="text-2xl font-bold text-green-900">
                      SOW Generated Successfully!
                    </h3>
                    <p className="text-muted-foreground text-center max-w-md">
                      Your Statement of Work has been created and saved to your
                      Google Drive folder.
                    </p>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-4">
                    <Button
                      size="lg"
                      className="flex-1 h-12 bg-gradient-to-r from-primary to-red-600 hover:from-red-600 hover:to-red-700"
                      onClick={() => window.open(generatedSowUrl, "_blank")}
                    >
                      <Download className="mr-2 h-5 w-5" />
                      View Generated SOW
                    </Button>
                    <Button
                      size="lg"
                      variant="outline"
                      className="flex-1 h-12"
                      onClick={handleReset}
                    >
                      Generate Another SOW
                    </Button>
                  </div>
                </motion.div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Features Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-16 max-w-4xl mx-auto"
        >
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                icon: FileText,
                title: "Smart Extraction",
                description:
                  "Automatically extracts key details from your proposal documents",
              },
              {
                icon: Sparkles,
                title: "AI-Powered",
                description:
                  "Leverages advanced AI to generate comprehensive SOWs",
              },
              {
                icon: CheckCircle2,
                title: "Professional Output",
                description:
                  "Creates polished, professional Statement of Work documents",
              },
            ].map((feature, index) => (
              <Card
                key={index}
                className="border-0 bg-white/60 backdrop-blur-sm hover:bg-white/80 transition-all duration-300 hover:shadow-lg"
              >
                <CardHeader>
                  <div className="p-3 bg-gradient-to-br from-primary to-red-600 rounded-xl w-fit mb-2">
                    <feature.icon className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
