// lib/utils/validation.ts
export const validateEmail = (email: string): boolean => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const validatePassword = (password: string): boolean => {
  // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
  const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
  return re.test(password);
};

export const validatePhone = (phone: string): boolean => {
  // Ethiopian phone number format
  const re = /^(\+251|0)?9\d{8}$/;
  return re.test(phone);
};

export const validateEthiopianName = (name: string): boolean => {
  // Allow Latin characters, Amharic characters, spaces, hyphens
  const re = /^[\u1200-\u137F\u1380-\u139F\u2D80-\u2DDF\uAB00-\uAB2F\sa-zA-Z\-']+$/;
  return re.test(name);
};

export const validateUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const validateFileSize = (file: File, maxSizeInMB: number): boolean => {
  return file.size <= maxSizeInMB * 1024 * 1024;
};

export const validateFileType = (file: File, allowedTypes: string[]): boolean => {
  return allowedTypes.includes(file.type);
};