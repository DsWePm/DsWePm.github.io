// Refresh src/data/repos.json from the GitHub API at build time, so visitors
// never hit the API rate limit.
//   GITHUB_USER=<login> node scripts/fetch-github.mjs
// Optional GITHUB_TOKEN raises the rate limit. Keeps the existing file on failure.
import { writeFile } from 'node:fs/promises'

const user = process.env.GITHUB_USER
const out = new URL('../src/data/repos.json', import.meta.url)
if (!user) {
  console.log('[fetch-github] GITHUB_USER not set, keeping existing repos.json')
  process.exit(0)
}
const headers = { Accept: 'application/vnd.github+json', 'User-Agent': 'homepage-build' }
if (process.env.GITHUB_TOKEN) headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`

try {
  const res = await fetch(`https://api.github.com/users/${user}/repos?per_page=100&sort=pushed`, { headers })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  const repos = (await res.json())
    .filter((r) => !r.fork && !r.archived)
    .sort((a, b) => b.stargazers_count - a.stargazers_count || Date.parse(b.pushed_at) - Date.parse(a.pushed_at))
    .slice(0, 9)
    .map((r) => ({
      name: r.name,
      description: r.description ?? '',
      language: r.language ?? '—',
      stars: r.stargazers_count,
      forks: r.forks_count,
      updated: r.pushed_at.slice(0, 10),
      url: r.html_url,
      topics: r.topics ?? [],
    }))
  await writeFile(out, JSON.stringify(repos, null, 2) + '\n')
  console.log(`[fetch-github] wrote ${repos.length} repos for ${user}`)
} catch (err) {
  console.warn('[fetch-github] failed, keeping existing repos.json:', err.message)
}
