// GET /api/jupjup-config — 결제 화면이 쓸 공개 설정(클라이언트 키·테스트 여부). 시크릿 키는 내보내지 않는다.
'use strict';
const J = require('./_jupjup');

module.exports = (req, res) => {
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify({ ready: J.ready(), clientKey: J.ready() ? J.ENV.clientKey : '', test: J.isTest() }));
};
