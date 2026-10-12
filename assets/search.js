(function(){var f=document.getElementById('sf'),q=document.getElementById('q'),r=document.getElementById('results'),idx=null;
function norm(s){return (s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');}
function run(){r.textContent='';if(!idx)return;var t=norm(q.value.trim()),c=f.c.value,k=f.k.value,s=f.s.value;if(!t&&!c&&!k&&!s)return;
var w=t?t.split(/\s+/):[];var seen={};var hits=idx.filter(function(e){if(c&&e.c!==c)return false;if(k&&e.k!==k)return false;if(s&&e.s!==s)return false;var h=norm(e.t+' '+e.x);return w.every(function(x){return h.indexOf(x)>-1;});});
if(!hits.length){var p=document.createElement('p');p.textContent=f.dataset.none;r.appendChild(p);return;}
var info=document.createElement('p');info.textContent=hits.length;r.appendChild(info);
var ul=document.createElement('ul');ul.className='res';hits.slice(0,80).forEach(function(e){var li=document.createElement('li'),a=document.createElement('a'),b=document.createElement('span');b.className='badge b-'+e.s;b.textContent=e.s;a.href=e.u;a.textContent=e.t;li.appendChild(b);li.appendChild(document.createTextNode(' '));li.appendChild(a);li.appendChild(document.createTextNode(' — '+e.x));ul.appendChild(li);});r.appendChild(ul);}
fetch(f.dataset.index).then(function(x){return x.json();}).then(function(j){idx=j;var p=new URLSearchParams(location.search);if(p.get('q'))q.value=p.get('q');run();});
f.addEventListener('submit',function(e){e.preventDefault();run();});f.addEventListener('input',run);f.addEventListener('change',run);})();
