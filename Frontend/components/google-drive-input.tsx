"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { FolderOpen, CheckCircle2, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface GoogleDriveInputProps {
  label: string;
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  description?: string;
}

export function GoogleDriveInput({
  label,
  placeholder,
  value,
  onChange,
  error,
  description,
}: GoogleDriveInputProps) {
  const [isFocused, setIsFocused] = useState(false);
  const isValid = value && !error && (
    value.startsWith("gs://") ||
    value.includes("drive.google.com") ||
    value.includes("docs.google.com")
  );

  return (
    <div className="space-y-2 w-full">
      <Label htmlFor={label} className="text-base font-semibold">
        {label}
      </Label>
      {description && (
        <p className="text-sm text-muted-foreground">{description}</p>
      )}
      <div className="relative">
        <div
          className={cn(
            "absolute left-3 top-1/2 -translate-y-1/2 transition-colors",
            isFocused ? "text-primary" : "text-muted-foreground"
          )}
        >
          <FolderOpen className="h-5 w-5" />
        </div>
        <Input
          id={label}
          type="url"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          className={cn(
            "pl-11 pr-11 h-12 transition-all",
            isFocused && "ring-2 ring-primary ring-offset-2",
            error && "border-destructive focus-visible:ring-destructive",
            isValid && "border-green-500"
          )}
        />
        <div className="absolute right-3 top-1/2 -translate-y-1/2">
          {isValid && (
            <CheckCircle2 className="h-5 w-5 text-green-500 animate-fade-in" />
          )}
          {error && value && (
            <AlertCircle className="h-5 w-5 text-destructive animate-fade-in" />
          )}
        </div>
      </div>
      {error && value && (
        <p className="text-sm text-destructive flex items-center gap-1 animate-fade-in">
          <AlertCircle className="h-4 w-4" />
          {error}
        </p>
      )}
    </div>
  );
}
