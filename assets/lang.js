(function(){var ul=document.querySelector('[data-langs]');if(!ul)return;var langs=ul.dataset.langs.split(',');
var pref=(navigator.languages||[navigator.language||'']).map(function(l){return l.slice(0,2).toLowerCase();});
for(var i=0;i<pref.length;i++){if(langs.indexOf(pref[i])>-1){location.replace('/'+pref[i]+'/');return;}}})();
