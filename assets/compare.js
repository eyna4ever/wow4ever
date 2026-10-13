(function(){var f=document.getElementById('cf'),rows=document.querySelectorAll('#ct tbody tr'),c=document.getElementById('cnt');if(!f)return;
function run(){var s=f.sky.checked,n=0;rows.forEach(function(t){var ok=(!s||t.dataset.sky==='1');t.hidden=!ok;if(ok)n++;});c.textContent=n+' / '+rows.length;}
f.addEventListener('change',run);run();})();
