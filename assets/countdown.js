(function(){var c=document.querySelector('.countdown');if(!c)return;var t=Date.parse(c.dataset.launch),u=c.querySelectorAll('[data-u]');if(isNaN(t))return;
function p(n){return n<10?'0'+n:''+n;}
function tick(){var d=Math.max(0,Math.floor((t-Date.now())/1000));if(d===0){c.textContent=c.dataset.done;return;}
var v=[Math.floor(d/86400),Math.floor(d%86400/3600),Math.floor(d%3600/60),d%60];u.forEach(function(e,i){e.textContent=i?p(v[i]):v[i];});setTimeout(tick,1000);}tick();})();
