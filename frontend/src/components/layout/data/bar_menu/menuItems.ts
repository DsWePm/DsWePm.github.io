export interface SubMenuItem {
  label: string
  href: string
}

export interface MenuItem {
  label: string
  href: string
  children?: SubMenuItem[]
}

export const menuItems: MenuItem[] = [
  { label: 'Home', href: '#home' },
  { label: 'About', href: '#about' },
  {
    label: 'Portfolio',
    href: '#portfolio',
    children: [
      { label: 'Projects', href: '#projects' },
      { label: 'Collections', href: '#collections' },
      { label: 'Demo', href: '#demo' },
    ],
  },
  {
    label: 'News',
    href: '#news',
    children: [
      { label: 'Blog', href: '#blog' },
      { label: 'Stream', href: '#stream' },
    ],
  },
  { label: 'Contact', href: '#contact' },
]
