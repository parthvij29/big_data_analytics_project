import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../src/web')
const mime = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.jpg': 'image/jpeg', '.webp': 'image/webp' }

http.createServer((request, response) => {
  let name
  try {
    name = decodeURIComponent(new URL(request.url, 'http://localhost').pathname)
  } catch {
    response.writeHead(400).end('Invalid URL')
    return
  }
  const file = path.resolve(root, '.' + (name === '/' ? '/index.html' : name))
  const relative = path.relative(root, file)
  if (relative === '..' || relative.startsWith('..' + path.sep) || path.isAbsolute(relative)) {
    response.writeHead(404).end('Not found')
    return
  }
  fs.readFile(file, (error, bytes) => {
    if (error) {
      response.writeHead(404).end('Not found')
      return
    }
    response.writeHead(200, { 'Content-Type': mime[path.extname(file)] || 'application/octet-stream' })
    response.end(bytes)
  })
}).listen(3000, '127.0.0.1', () => console.log('VoltPulse is available at http://localhost:3000'))
