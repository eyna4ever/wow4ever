(function(){document.documentElement.classList.add('js');var b=document.querySelector('.menu-btn'),n=document.getElementById('mainnav');if(!b||!n)return;b.hidden=false;
b.addEventListener('click',function(){var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false');});
var ds=n.querySelectorAll('details');ds.forEach(function(d){d.addEventListener('toggle',function(){if(d.open)ds.forEach(function(o){if(o!==d)o.open=false;});});});
document.addEventListener('click',function(e){if(!n.contains(e.target))ds.forEach(function(d){d.open=false;});});
document.addEventListener('keydown',function(e){if(e.key==='Escape')ds.forEach(function(d){if(d.open){d.open=false;d.querySelector('summary').focus();}});});})();
