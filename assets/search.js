(function(){var f=document.getElementById('sf'),q=document.getElementById('q'),r=document.getElementById('results'),idx=null;
function norm(s){return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');}
function run(){var t=norm(q.value.trim());r.textContent='';if(!t||!idx)return;var words=t.split(/\s+/);
var hits=idx.filter(function(e){var h=norm(e.t+' '+e.x);return words.every(function(w){return h.indexOf(w)>-1;});});
if(!hits.length){var p=document.createElement('p');p.textContent=f.dataset.none;r.appendChild(p);return;}
var ul=document.createElement('ul');hits.slice(0,50).forEach(function(e){var li=document.createElement('li'),a=document.createElement('a');a.href=e.u;a.textContent=e.t;li.appendChild(a);li.appendChild(document.createTextNode(' — '+e.x));ul.appendChild(li);});r.appendChild(ul);}
fetch(f.dataset.index).then(function(x){return x.json();}).then(function(j){idx=j;var p=new URLSearchParams(location.search).get('q');if(p){q.value=p;}run();});
f.addEventListener('submit',function(e){e.preventDefault();run();});q.addEventListener('input',run);})();
