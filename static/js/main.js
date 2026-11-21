document.addEventListener('DOMContentLoaded',()=>{document.querySelectorAll('form[onsubmit]').forEach(form=>form.addEventListener('submit',e=>{if(!confirm('Are you sure?'))e.preventDefault()}));});
