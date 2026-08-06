// 本地脆弱 Node 靶标 —— 仅供 hunt-prototype-pollution 端到端自测，绑定 127.0.0.1。
// POST / : 用有缺陷的 deepMerge 把 JSON body 合并进 CONFIG（允许 __proto__ 污染原型）。
// GET  / : dump 一个新对象的可枚举继承属性；若原型被污染，探针属性名会出现在响应里。
'use strict';
const http = require('http');

const PORT = parseInt(process.argv[2] || '8798', 10);
const CONFIG = {};

function vulnMerge(target, src) {
  for (const k in src) {
    if (src[k] && typeof src[k] === 'object') {
      if (!target[k] || typeof target[k] !== 'object') target[k] = {};
      vulnMerge(target[k], src[k]);
    } else {
      target[k] = src[k];
    }
  }
  return target;
}

const server = http.createServer((req, res) => {
  if (req.method === 'POST') {
    let buf = '';
    req.on('data', (c) => { buf += c; if (buf.length > 1e6) req.destroy(); });
    req.on('end', () => {
      try { vulnMerge(CONFIG, JSON.parse(buf || '{}')); } catch (e) { /* ignore */ }
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify({ ok: true }));
    });
    return;
  }
  // GET: 反射继承属性（污染后会带出探针属性名）
  const inherited = {};
  const probe = {};
  for (const k in probe) inherited[k] = probe[k];
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({ config: CONFIG, inherited }));
});

server.listen(PORT, '127.0.0.1', () => {
  console.log('pp target on http://127.0.0.1:' + PORT);
});
