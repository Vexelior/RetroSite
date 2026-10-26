// retro.js -- shared scripts for The World Wide Wayback
// Written in the "JavaScript 1.2" house style on purpose: var, document.write,
// no frameworks. The only modern bits are localStorage (standing in for the
// CGI-BIN we don't have) and Web Audio (standing in for the MIDI plug-in
// browsers no longer ship).

// ---- Hit counter --------------------------------------------------------
// A real 1997 counter was a Perl script on the server. Ours counts the
// visits *this browser* has made, on top of a suitably impressive base.
function hitCounter() {
  var base = 4217;
  var n = 1;
  try {
    n = parseInt(window.localStorage.getItem("wwwb_hits") || "0", 10) + 1;
    window.localStorage.setItem("wwwb_hits", String(n));
  } catch (e) {}
  var s = String(base + n);
  while (s.length < 7) s = "0" + s;
  var html = "";
  for (var i = 0; i < s.length; i++) {
    html += '<IMG SRC="images/digit' + s.charAt(i) + '.gif" WIDTH=15 HEIGHT=22 ALT="' + s.charAt(i) + '">';
  }
  document.write(html);
}

// ---- "Last updated" stamp ---------------------------------------------
function lastUpdated() {
  document.write("This page was last updated on " + document.lastModified);
}

// ---- Sparkle cursor trail ----------------------------------------------
function sparkleTrail() {
  var colors = ["#FFFF00", "#FF00FF", "#00FFFF", "#FFFFFF", "#FF9900"];
  var last = 0;
  document.onmousemove = function (ev) {
    var now = new Date().getTime();
    if (now - last < 30) return;
    last = now;
    var s = document.createElement("div");
    s.innerHTML = "*";
    s.style.position = "absolute";
    s.style.left = (ev.pageX + 6) + "px";
    s.style.top = (ev.pageY + 4) + "px";
    s.style.color = colors[Math.floor(Math.random() * colors.length)];
    s.style.font = "bold 14px Courier New, monospace";
    s.style.pointerEvents = "none";
    s.style.zIndex = 99;
    document.body.appendChild(s);
    var life = 0;
    var t = setInterval(function () {
      life++;
      s.style.top = (parseInt(s.style.top, 10) + 2) + "px";
      if (life > 12) {
        clearInterval(t);
        if (s.parentNode) s.parentNode.removeChild(s);
      }
    }, 40);
  };
}

// ---- Theme song (stand-in for the Crescendo MIDI plug-in) ---------------
// Same tune as midi/theme.mid, played with a square wave.
var wwwbAudio = null;
function playTheme() {
  var AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) {
    alert("Sorry! Your browser cannot play MIDI. Try downloading theme.mid instead.");
    return;
  }
  if (wwwbAudio) {
    wwwbAudio.close();
    wwwbAudio = null;
    return;
  }
  wwwbAudio = new AC();
  var ctx = wwwbAudio;
  var q = 0.5, e = 0.25, h = 1.0;
  var C = 72, D = 74, E = 76, A = 81, B = 83, G = 79;
  var tune = [
    [E, e], [G, e], [C + 12, q], [B, e], [A, e], [G, q],
    [A, e], [G, e], [E, q], [D, e], [E, e], [C, q],
    [E, e], [G, e], [A, q], [G, e], [E, e], [D, q],
    [C, e], [D, e], [E, e], [G, e], [C, h]
  ];
  var bass = [48, 45, 41, 43];
  var t = ctx.currentTime + 0.05;
  function note(midi, start, dur, type, vol) {
    var o = ctx.createOscillator();
    var g = ctx.createGain();
    o.type = type;
    o.frequency.value = 440 * Math.pow(2, (midi - 69) / 12);
    g.gain.setValueAtTime(vol, start);
    g.gain.setValueAtTime(vol, start + dur * 0.85);
    g.gain.linearRampToValueAtTime(0, start + dur);
    o.connect(g);
    g.connect(ctx.destination);
    o.start(start);
    o.stop(start + dur);
  }
  var start = t;
  for (var rep = 0; rep < 2; rep++) {
    for (var i = 0; i < tune.length; i++) {
      note(tune[i][0], t, tune[i][1], "square", 0.06);
      t += tune[i][1];
    }
  }
  for (var b = 0; b < 8; b++) {
    note(bass[b % 4], start + b * 2, 2, "triangle", 0.12);
  }
  setTimeout(function () {
    if (wwwbAudio === ctx) { ctx.close(); wwwbAudio = null; }
  }, (t - ctx.currentTime + 0.5) * 1000);
}

// ---- Guestbook (stand-in for guestbook.pl) -----------------------------
function gbLoad() {
  try {
    return JSON.parse(window.localStorage.getItem("wwwb_guestbook") || "[]");
  } catch (e) {
    return [];
  }
}

function gbEscape(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function gbRender() {
  var box = document.getElementById("gbEntries");
  if (!box) return;
  var list = gbLoad();
  var html = "";
  for (var i = list.length - 1; i >= 0; i--) {
    var x = list[i];
    html += '<TABLE WIDTH="100%" BORDER=1 CELLPADDING=6 CELLSPACING=0 BGCOLOR="#FFFFCC"><TR><TD>' +
      '<FONT FACE="Arial" SIZE=2><B>Name:</B> ' + gbEscape(x.name) +
      (x.home ? ' &nbsp; <B>Homepage:</B> <A HREF="#" onClick="return false">' + gbEscape(x.home) + '</A>' : '') +
      '<BR><B>Found us via:</B> ' + gbEscape(x.found) +
      '<BR><B>Date:</B> ' + gbEscape(x.date) +
      '<BR><B>Comments:</B> ' + gbEscape(x.comments).replace(/\n/g, "<BR>") +
      ' <FONT COLOR="#FF0000">(signed from your computer!)</FONT></FONT></TD></TR></TABLE><BR>';
  }
  box.innerHTML = html;
}

function gbSign(form) {
  if (!form.name.value || !form.comments.value) {
    alert("Please fill in your name and comments before signing my guestbook!");
    return false;
  }
  var list = gbLoad();
  list.push({
    name: form.name.value.substring(0, 60),
    home: form.home.value === "http://" ? "" : form.home.value.substring(0, 100),
    found: form.found.options[form.found.selectedIndex].text,
    comments: form.comments.value.substring(0, 1000),
    date: new Date().toDateString()
  });
  try {
    window.localStorage.setItem("wwwb_guestbook", JSON.stringify(list));
  } catch (e) {
    alert("Our guestbook server is down. Please try again later!");
    return false;
  }
  form.reset();
  gbRender();
  alert("Thanks for signing my guestbook!!! Come back soon!");
  return false;
}
