'use strict';

// 深度追踪 - 本地服务端
// 功能：静态文件服务 + 关键词同步 API
// 启动：node server.js
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 9999;
const ROOT = __dirname;
const KEYWORDS_FILE = path.join(ROOT, 'deep-track-keywords.json');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.ico': 'image/x-icon',
};

function serveFile(res, filePath) {
  var ext = path.extname(filePath);
  fs.readFile(filePath, function(err, data) {
    if (err) {
      res.writeHead(404);
      res.end('Not found');
      return;
    }
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'text/plain' });
    res.end(data);
  });
}

function readKeywords() {
  try {
    var raw = fs.readFileSync(KEYWORDS_FILE, 'utf-8');
    return JSON.parse(raw);
  } catch (e) {
    return [];
  }
}

function writeKeywords(keywords) {
  fs.writeFileSync(KEYWORDS_FILE, JSON.stringify(keywords, null, 2), 'utf-8');
}

var server = http.createServer(function(req, res) {
  // CORS - allow same-origin
  res.setHeader('Access-Control-Allow-Origin', 'http://localhost:' + PORT);
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  var url = req.url.replace(/\?.*$/, '');

  // ── API: GET /api/keywords ──
  if (url === '/api/keywords' && req.method === 'GET') {
    var kwList = readKeywords();
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({ keywords: kwList, count: kwList.length }));
    return;
  }

  // ── API: POST /api/keywords ──
  if (url === '/api/keywords' && req.method === 'POST') {
    var body = '';
    req.on('data', function(c) { body += c; });
    req.on('end', function() {
      try {
        var payload = JSON.parse(body);
        if (Array.isArray(payload.keywords)) {
          writeKeywords(payload.keywords);
          console.log('[sync] keywords updated: ' + payload.keywords.join(', '));
          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
          res.end(JSON.stringify({ ok: true, count: payload.keywords.length }));
        } else {
          res.writeHead(400);
          res.end(JSON.stringify({ error: 'keywords must be an array' }));
        }
      } catch (e) {
        res.writeHead(400);
        res.end(JSON.stringify({ error: 'invalid json' }));
      }
    });
    return;
  }

  // ── Static files ──
  var filePath = path.join(ROOT, url === '/' ? 'index.html' : url);
  // Prevent directory traversal
  if (!filePath.startsWith(ROOT)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }
  serveFile(res, filePath);
});

server.listen(PORT, '127.0.0.1', function() {
  console.log('Deep Track server running at http://localhost:' + PORT);
  console.log('Keywords: ' + readKeywords().join(', ') || '(empty)');
});
