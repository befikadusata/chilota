// frontend/app/components/ui/FileUploadInput.tsx
'use client';

import * as React from 'react';
import { Button } from './Button';
import { Input } from './Input';
import { Label } from './Label';
import { Upload, FileText, Image as ImageIcon, XCircle, Loader2 } from 'lucide-react';
import Image from 'next/image';

interface FileUploadInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  onFileChange: (file: File | null) => void;
  currentFileUrl?: string | null; // For displaying existing files
  allowedFileTypes?: string; // e.g., "image/*", ".pdf", ".jpg, .png"
  maxFileSizeMB?: number; // Maximum file size in MB
  loading?: boolean;
  error?: string | null;
}

const FileUploadInput = React.forwardRef<HTMLInputElement, FileUploadInputProps>(
  (
    {
      label,
      onFileChange,
      currentFileUrl,
      allowedFileTypes = 'image/*',
      maxFileSizeMB = 5,
      loading,
      error,
      id,
      ...props
    },
    ref
  ) => {
    const fileInputRef = React.useRef<HTMLInputElement>(null);
    const [previewUrl, setPreviewUrl] = React.useState<string | null>(currentFileUrl || null);
    const [fileName, setFileName] = React.useState<string | null>(null);
    const [internalError, setInternalError] = React.useState<string | null>(null);

    React.useEffect(() => {
      setPreviewUrl(currentFileUrl || null);
      if (currentFileUrl) {
        setFileName(currentFileUrl.substring(currentFileUrl.lastIndexOf('/') + 1));
      }
    }, [currentFileUrl]);

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      setInternalError(null);
      const file = event.target.files?.[0];

      if (file) {
        if (maxFileSizeMB && file.size > maxFileSizeMB * 1024 * 1024) {
          setInternalError(`File size exceeds ${maxFileSizeMB}MB limit.`);
          onFileChange(null);
          setPreviewUrl(null);
          setFileName(null);
          return;
        }

        const reader = new FileReader();
        reader.onloadend = () => {
          setPreviewUrl(reader.result as string);
        };
        reader.readAsDataURL(file);
        setFileName(file.name);
        onFileChange(file);
      } else {
        onFileChange(null);
        setPreviewUrl(null);
        setFileName(null);
      }
    };

    const triggerFileInput = () => {
      fileInputRef.current?.click();
    };

    const clearFile = () => {
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      onFileChange(null);
      setPreviewUrl(null);
      setFileName(null);
      setInternalError(null);
    };

    const displayError = internalError || error;

    return (
      <div className="space-y-2">
        {label && <Label htmlFor={id || props.name}>{label}</Label>}
        <div className="flex items-center space-x-2">
          <Input
            ref={fileInputRef}
            id={id || props.name}
            type="file"
            accept={allowedFileTypes}
            className="hidden" // Hide the actual file input
            onChange={handleFileChange}
            {...props}
          />
          <Button type="button" onClick={triggerFileInput} variant="outline" disabled={loading}>
            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Upload className="mr-2 h-4 w-4" />}
            {fileName ? 'Change File' : 'Choose File'}
          </Button>
          {fileName && (
            <span className="text-sm text-muted-foreground flex items-center">
              {fileName}
              <Button type="button" variant="ghost" size="icon" onClick={clearFile} className="ml-2 h-6 w-6">
                <XCircle className="h-4 w-4" />
              </Button>
            </span>
          )}
        </div>

        {displayError && <p className="text-sm text-error">{displayError}</p>}

        {previewUrl && allowedFileTypes.includes('image') && (
          <div className="mt-4 border border-border rounded-lg overflow-hidden flex items-center justify-center bg-muted">
            <Image
              src={previewUrl}
              alt="File preview"
              width={200}
              height={150}
              className="object-contain max-h-[150px]"
              priority={false}
            />
          </div>
        )}
        {previewUrl && !allowedFileTypes.includes('image') && (
          <div className="mt-4 flex items-center gap-2 text-muted-foreground">
            <FileText className="h-6 w-6" />
            <span>File selected: {fileName || 'Click to view'}</span>
          </div>
        )}
      </div>
    );
  }
);

FileUploadInput.displayName = 'FileUploadInput';

export { FileUploadInput };