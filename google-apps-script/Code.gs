/**
 * Quote Engine — Google Sheets backend (Apps Script web app)
 * ---------------------------------------------------------------------------
 * This turns your Google Sheet into the read/write source for Quote Engine.
 *
 * SETUP
 *  1. Open your quotes Google Sheet (columns: Quote, Author, Source, Theme;
 *     an ID and Tags column are added automatically on first run).
 *  2. Extensions ▸ Apps Script. Delete the sample code, paste this whole file,
 *     and Save.
 *  3. Deploy ▸ New deployment ▸ type "Web app".
 *       - Execute as:  Me
 *       - Who has access:  Anyone
 *     Deploy, authorise, and copy the Web app URL (ends in /exec).
 *  4. Bake that URL into the app:
 *       QE_SHEET_API="https://script.google.com/macros/s/AKfy.../exec" \
 *       python3 scripts/build.py
 *     ...then commit index.html. (Or paste it into window.QE_CONFIG in index.html.)
 *
 * TAGS (Tags column) — steer any quote by hand or via the app's buttons:
 *   exclude | hide | off   -> never show it
 *   rarely | less          -> show it less often
 *   more | often           -> show it more often
 *   anything else          -> kept as your own free-form tag (never touched)
 *
 * SECURITY: "Anyone" access means anyone who has the /exec URL can post to the
 * Sheet. For a personal tool that's usually fine. Set WRITE_KEY below (and pass
 * QE_SHEET_KEY to build.py) as a light deterrent — note it ships in the page, so
 * it stops casual pokes, not a determined person.
 */

var SHEET_NAME = '';      // '' = first sheet; or set e.g. 'Quotes'
var WRITE_KEY  = '';      // '' = no key; else must match QE_SHEET_KEY baked into the app

var FREQ = ['rarely', 'less', 'normal', 'more', 'often'];
var EXCL = ['exclude', 'hide', 'off', 'mute', 'skip'];

function doGet() {
  var ctx = ctx_();
  var v = ctx.values, c = ctx.c, out = [];
  for (var i = 1; i < v.length; i++) {
    var q = String(v[i][c.q] || '').trim();
    if (!q) continue;
    out.push({
      id: String(v[i][c.id]),
      quote: q,
      author: cell_(v[i], c.a),
      source: cell_(v[i], c.s),
      theme: cell_(v[i], c.t),
      tags: cell_(v[i], c.tag)
    });
  }
  return json_({ quotes: out });
}

function doPost(e) {
  var body;
  try { body = JSON.parse(e.postData.contents); }
  catch (err) { return json_({ error: 'bad json' }); }

  if (WRITE_KEY && String(body.key || '') !== WRITE_KEY) return json_({ error: 'unauthorized' });

  var ctx = ctx_(), sh = ctx.sh, c = ctx.c, action = body.action;

  if (action === 'add') {
    var rows = body.rows || [body], ids = [];
    for (var k = 0; k < rows.length; k++) {
      var r = rows[k];
      ctx.maxId++;
      var full = new Array(sh.getLastColumn()).fill('');
      full[c.id] = ctx.maxId;
      if (c.q >= 0) full[c.q] = r.quote || '';
      if (c.a >= 0) full[c.a] = r.author || '';
      if (c.s >= 0) full[c.s] = r.source || '';
      if (c.t >= 0) full[c.t] = r.theme || '';
      if (c.tag >= 0) full[c.tag] = r.tags || '';
      sh.appendRow(full);
      ids.push(String(ctx.maxId));
    }
    return json_({ ok: true, ids: ids });
  }

  if (action === 'resetFreq') {
    for (var i = 1; i < ctx.values.length; i++) {
      var nw = setFreqTag_(ctx.values[i][c.tag], 'normal');
      if (nw !== String(ctx.values[i][c.tag])) sh.getRange(i + 1, c.tag + 1).setValue(nw);
    }
    return json_({ ok: true });
  }
  if (action === 'restoreAll') {
    for (var j = 1; j < ctx.values.length; j++) {
      var nr = setExclTag_(ctx.values[j][c.tag], false);
      if (nr !== String(ctx.values[j][c.tag])) sh.getRange(j + 1, c.tag + 1).setValue(nr);
    }
    return json_({ ok: true });
  }

  // row-targeted actions
  var ri = rowById_(ctx, body.id);
  if (ri < 0) return json_({ error: 'not found' });
  var cur = ctx.values[ri][c.tag];

  if (action === 'setFreq') {
    sh.getRange(ri + 1, c.tag + 1).setValue(setFreqTag_(cur, String(body.level || 'normal')));
  } else if (action === 'setExcluded') {
    sh.getRange(ri + 1, c.tag + 1).setValue(setExclTag_(cur, !!body.excluded));
  } else if (action === 'update') {
    if (c.q >= 0 && body.quote != null) sh.getRange(ri + 1, c.q + 1).setValue(body.quote);
    if (c.a >= 0 && body.author != null) sh.getRange(ri + 1, c.a + 1).setValue(body.author);
    if (c.s >= 0 && body.source != null) sh.getRange(ri + 1, c.s + 1).setValue(body.source);
    if (c.t >= 0 && body.theme != null) sh.getRange(ri + 1, c.t + 1).setValue(body.theme);
  } else {
    return json_({ error: 'unknown action' });
  }
  return json_({ ok: true });
}

// --- helpers ---------------------------------------------------------------
function ctx_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = (SHEET_NAME && ss.getSheetByName(SHEET_NAME)) || ss.getSheets()[0];
  if (sh.getLastRow() === 0) sh.appendRow(['ID', 'Quote', 'Author', 'Source', 'Theme', 'Tags']);

  var header = headerRow_(sh);
  if (header.indexOf('id') < 0) { sh.getRange(1, sh.getLastColumn() + 1).setValue('ID'); header = headerRow_(sh); }
  if (header.indexOf('tags') < 0) { sh.getRange(1, sh.getLastColumn() + 1).setValue('Tags'); header = headerRow_(sh); }

  var c = {
    id: header.indexOf('id'),
    q: findCol_(header, 'quote'),
    a: findCol_(header, 'author'),
    s: findCol_(header, 'source'),
    t: findCol_(header, 'theme'),
    tag: header.indexOf('tags')
  };

  var values = sh.getDataRange().getValues();
  // assign IDs to any rows missing one
  var maxId = 0;
  for (var i = 1; i < values.length; i++) { var n = parseInt(values[i][c.id], 10); if (!isNaN(n) && n > maxId) maxId = n; }
  for (var j = 1; j < values.length; j++) {
    if (String(values[j][c.id]).trim() === '' && String(values[j][c.q] || '').trim() !== '') {
      maxId++; values[j][c.id] = maxId; sh.getRange(j + 1, c.id + 1).setValue(maxId);
    }
  }
  return { sh: sh, values: values, c: c, maxId: maxId };
}
function headerRow_(sh) {
  return sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0].map(function (h) { return String(h).trim().toLowerCase(); });
}
function findCol_(header, name) { for (var i = 0; i < header.length; i++) { if (header[i].indexOf(name) >= 0) return i; } return -1; }
function cell_(row, ci) { return ci >= 0 ? String(row[ci] || '') : ''; }
function rowById_(ctx, id) {
  var v = ctx.values;
  for (var i = 1; i < v.length; i++) { if (String(v[i][ctx.c.id]) === String(id)) return i; }
  return -1;
}
function splitTags_(s) { return String(s || '').split(/[,\s]+/).map(function (x) { return x.trim(); }).filter(String); }
function setFreqTag_(tagsStr, level) {
  var toks = splitTags_(tagsStr).filter(function (t) { return FREQ.indexOf(t.toLowerCase()) < 0; });
  if (level && level !== 'normal') toks.push(level);
  return toks.join(', ');
}
function setExclTag_(tagsStr, excluded) {
  var toks = splitTags_(tagsStr).filter(function (t) { return EXCL.indexOf(t.toLowerCase()) < 0; });
  if (excluded) toks.push('exclude');
  return toks.join(', ');
}
function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
