// src/constants/menuItems.ts
export interface MenuItem {
  label: string;
  href: string;
}

export const menuItems: MenuItem[] = [
  { label: 'Home', href: '#home' },
  { label: 'About', href: '#about' },
  { label: 'Portfolio', href: '#portfolio' },
  { label: 'News', href: '#news' },
  { label: 'Contact', href: '#contact' },
  { label: 'Shit', href: '#shit' }
];
