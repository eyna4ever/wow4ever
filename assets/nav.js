(function(){document.documentElement.classList.add('js');var b=document.querySelector('.menu-btn'),n=document.getElementById('mainnav');if(!b||!n)return;b.hidden=false;
b.addEventListener('click',function(){var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false');});})();
