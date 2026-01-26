// lib/utils/formatters.ts
export const formatCurrency = (amount: number, currency: string = 'ETB'): string => {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: currency,
  }).format(amount);
};

export const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength) + '...';
};

export const capitalize = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1);
};

export const camelCaseToTitle = (str: string): string => {
  return str.replace(/([A-Z])/g, ' $1')
    .replace(/^./, str => str.toUpperCase());
};